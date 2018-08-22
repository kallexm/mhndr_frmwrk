import os
import subprocess

import entity_finder


class AppBuilder(object):
    def __init__(self, app, pymk_root):
        self.pymk_root    = pymk_root
        self.build_folder = os.path.join(self.pymk_root, app.rel_path, "_build")
        self.exe_file     = os.path.join(self.build_folder, app.name+".exe")
        self.app          = app

        self.temp_srcs    = []
        self.temp_headers = []
        self.temp_objects = []

        self.entities = []
        self.entities.append(app)
        self._get_entities(app)

        print("Building application "+self.app.name+" ...")

        for enty in self.entities:
            self.temp_srcs    = []
            self.temp_headers = []
            self._create_obj(enty)

        if self._should_link(self.exe_file, self.temp_objects):
            print("Linking "+self.exe_file+" ...")
            self._link_application()

        print("Finished building application "+self.app.name+"!")

    def _get_entities(self, entity):
        for dep in entity.dependencies:
            self.entities.append(dep)
            self._get_entities(dep)

    def _get_headers(self, entity):
        for dep in entity.dependencies:
            for inc in dep.includes:
                self.temp_headers.append(os.path.join(self.pymk_root, dep.rel_path, inc))
            self._get_headers(dep)


    def _should_compile(self, o_file, c_file, h_files):
        if not os.path.isfile(o_file):
            return True

        last_time_compiled = os.path.getmtime(o_file)
        
        if os.path.getmtime(c_file) > last_time_compiled:
            return True

        for h_file in h_files:
            if os.path.getmtime(h_file) > last_time_compiled:
                return True

        return False


    def _compile_to_obj(self, output_obj_file_to, c_file, h_files):
        inc_folder_list = []
        for h_file in h_files:
            inc_folder_list.append(os.path.dirname(h_file))

        inc_folder_set = set(inc_folder_list)
        inc_folder_list = list(inc_folder_set)

        cmd = ["gcc", "-c"]
        cmd.extend(["-o", output_obj_file_to])
        for inc in inc_folder_list:
            cmd.append("-I"+inc)
        cmd.append(c_file)

        subprocess.call(cmd)


    def _create_obj(self, entity):
        for src in entity.sources:
            self.temp_srcs.append(os.path.join(self.pymk_root, entity.rel_path, src))
        for inc in entity.includes:
            self.temp_headers.append(os.path.join(self.pymk_root, entity.rel_path, inc))
        self._get_headers(entity)

        for src in self.temp_srcs:
            c_file_name_base = os.path.basename(src)
            o_file_name_base = c_file_name_base.replace(".c", ".o")
            o_file = os.path.join(self.build_folder, o_file_name_base)

            if self._should_compile(o_file, src, self.temp_headers):
                print("Compiling "+src+" ...")
                self._compile_to_obj(o_file, src, self.temp_headers)
            self.temp_objects.append(o_file)


    def _should_link(self, exe_file, o_files):
        if not os.path.isfile(exe_file):
            return True

        last_time_compiled = os.path.getmtime(exe_file)

        for o_file in o_files:
            if os.path.getmtime(o_file) > last_time_compiled:
                return True

        return False


    def _link_application(self):
        cmd = ["gcc"]
        cmd.extend(["-o", self.exe_file])
        cmd.extend(self.temp_objects)

        subprocess.call(cmd)

