import argparse
import os
import re
import subprocess
import xml.dom.minidom as mxml
import time


class Entity(object):
    def __init__(self):
        self.name             = ""
        self.rel_path         = ""
        self.sources          = []
        self.includes         = []

        self.unsatisfied_deps = []
        self.dependencies     = []

    def fetch_info_from_xml_file(self, file):
        def getNodeText(node):
            nodelist = node.childNodes
            result = []
            for node in nodelist:
                if node.nodeType == node.TEXT_NODE:
                    result.append(node.data)
            return ''.join(result)

        doc = mxml.parse(file)

        entity = doc.getElementsByTagName("Entity")[0]

        self.name = entity.getAttribute("name")

        sources = entity.getElementsByTagName("Source")
        for src in sources:
            self.sources.append(os.path.join(getNodeText(src)))

        includes = entity.getElementsByTagName("Include")
        for inc_path in includes:
            self.includes.append(os.path.join(getNodeText(inc_path)))

        unsatisfied_deps = entity.getElementsByTagName("Dependency")
        for dep in unsatisfied_deps:
            self.unsatisfied_deps.append(getNodeText(dep))



class Build_system_entity_mapper(object):
    def __init__(self, root_path):
        self.tests       = []
        self.executables = []
        self.modules     = []

        self.total_c_files = 0
        self.total_h_files = 0

        start_time = time.time()

        print("Mapping entities...")
        self.run_mapper(root_path)

        print("Satisfies dependencies...")
        self.satisfy_dependencies()

        end_time = time.time()
        print("Mapping and dependency satisfaction took: "+str(end_time - start_time)+" sec(s)")
        self.print_stats()

    def run_mapper(self, root_path):
        exclude_dirs = [".git", "_build", "framework"]

        re_test_file        = re.compile(".*\.test")
        re_executable_file = re.compile(".*\.executable")
        re_module_file      = re.compile(".*\.module")
        re_c_file           = re.compile(".*\.c")
        re_h_file           = re.compile(".*\.h")

        build_sys_root = root_path.split(os.path.sep)
        for root, dirs, files in os.walk(root_path):
            rel_path = root.replace(root_path+os.sep, "")
            
            dir_path_list = root.split(os.path.sep)
            dir_path_list = [d for d in dir_path_list if d not in build_sys_root]
            if list(set(dir_path_list) & set(exclude_dirs)) != []:
                continue

            for file in files:
                enty = Entity()
                if re_test_file.match(file):
                    enty.fetch_info_from_xml_file(os.path.join(root, file))
                    enty.rel_path = rel_path
                    self.tests.append(enty)

                elif re_executable_file.match(file):
                    enty.fetch_info_from_xml_file(os.path.join(root, file))
                    enty.rel_path = rel_path
                    self.executables.append(enty)

                elif re_module_file.match(file):
                    enty.fetch_info_from_xml_file(os.path.join(root, file))
                    enty.rel_path = rel_path
                    self.modules.append(enty)

                elif re_c_file.match(file):
                    self.total_c_files += 1

                elif re_h_file.match(file):
                    self.total_h_files += 1



    def satisfy_dependencies(self):
        for enty in (self.modules+self.executables+self.tests):
            while enty.unsatisfied_deps != []:
                dep_name = enty.unsatisfied_deps.pop(0)
                dep_ref  = self.get_dependency_items(dep_name)
                if dep_ref != None:
                    enty.dependencies.append(dep_ref)
                else:
                    print("Missing dependency in "+enty.name+". Missing dependency: "+dep_name)

        
    def get_dependency_items(self, dependency_name):
        for mod in self.modules:
            if mod.name == dependency_name:
                return mod
        return None


    def print_stats(self):
        print("======[Entities]======")
        print("Modules:     "+str(len(self.modules)))
        print("Executables: "+str(len(self.executables)))
        print("Tests:       "+str(len(self.tests)))

        print("\n", end="")

        print("======[Files]=========")
        print("Total c files: "+str(self.total_c_files))
        print("Total h files: "+str(self.total_h_files))

        print("\n", end="")



def get_dependency_files(entity, pymk_root, lists):
    for src in entity.sources:
        abs_src_path = os.path.abspath(os.path.join(pymk_root, entity.rel_path, src))
        lists.src_list.append(abs_src_path)

    for inc in entity.includes:
        abs_inc_path = os.path.abspath(os.path.join(pymk_root, entity.rel_path, inc))
        lists.inc_list.append(abs_inc_path)

    for dep in entity.dependencies:
        get_dependency_files(dep, pymk_root, lists)

    return


class build_file_lists(object):
    def __init__(self):
        self.src_list = []
        self.inc_list = []

    def remove_duplicates(self):
        sources_set   = set(self.src_list)
        include_set   = set(self.inc_list)
        self.src_list = list(sources_set)
        self.inc_list = list(include_set)


def compile_to_obj_file(src_file_path, inc_list, obj_file_path):
    cmd = []

    cmd.append("gcc")   # Use GCC compiler
    cmd.append("-c")    # Create object file (*.o)
    cmd.append("-o")
    cmd.append(obj_file_path)
    for inc in inc_list:
        cmd.append("-I\""+inc+"\"")
    cmd.append(src_file_path)

    print(cmd)
    subprocess.call(cmd)


def build(example, build_list, pymk_root):
    obj_base_path = os.path.join(pymk_root, example.rel_path, "_build")

    last_include_modification_time = 0
    for inc_file in build_list.inc_list:
        if os.path.getmtime(inc_file) > last_include_modification_time:
            last_include_modification_time = os.path.getmtime(inc_file)

    for src_file in build_list.src_list:
        src_file_name = os.path.basename(src_file)
        #(src_file_path, src_file_name) = os.path.split(src_file)
        obj_file_name = src_file_name.replace(".c", ".o")
        obj_file = os.path.join(obj_base_path, obj_file_name)

        # Recompile source file if the object file does not exist or if the source file have
        # been changed since last time the object file was created
        if not os.path.isfile(obj_file) or (os.path.getmtime(obj_file) <= os.path.getmtime(src_file)) or (os.path.getmtime(obj_file) <= last_include_modification_time):
            #build .o file from source file and headers
            compile_to_obj_file(src_file, build_list.inc_list, obj_file)
            
# Scrap much of this!!
# Instead of creating the src list and inc list before building, traverse "tree" and for
#   each .c file include all header files in the current entity and all include files in lower
#   dependencies. That way the source files are compiled with fewer include files, which leads to
#   less rebuilding of object files.

# Change content of cmd_build(). Affected sub functions and classes that have to be removed/rewritten: 
#   get_dependency_files(), build_file_lists, compile_to_obj_file() and build()

# Make some adaptive functionality for making the _build folder if it does not exist


def cmd_build(entity_map, pymk_root, args):
    print("build")
    for exe in entity_map.executables:
        lists = build_file_lists()

        get_dependency_files(exe, pymk_root, lists)
        lists.remove_duplicates()

        print("Entity "+exe.name+" have dependencies:")
        print("Sources:")
        print(lists.src_list)
        print("Include paths:")
        print(lists.inc_list)
        print("\n")

        build(exe, lists, pymk_root)
        



def cmd_test(entity_map, pymk_root, args):
    print("test")

def cmd_clean(entity_map, pymk_root, args):
    print("clean")

def cmd_stats(entity_map, pymk_root, args):
    print("stats")

def cmd_info(entity_map, pymk_root, args):
    print("info")


def main():
    parser = argparse.ArgumentParser(description="Tool to build and test c code.", epilog="Commands iterate through sub-directories recursively, looking for sources, dependencies and unit tests.")
    subparsers = parser.add_subparsers()

    parser_build = subparsers.add_parser("build", help="Iterate directories, compile and link modules and programs.")
    parser_build.set_defaults(func=cmd_build)

    parser_test  = subparsers.add_parser("test",  help="Iterate directories, generate mocks, build and run tests.")
    parser_test.set_defaults(func=cmd_test)

    parser_clean = subparsers.add_parser("clean", help="Remove build and test files.")
    parser_clean.set_defaults(func=cmd_clean)

    parser_stats = subparsers.add_parser("stats", help="Displays useful info about modules.")
    parser_stats.set_defaults(func=cmd_stats)

    parser_info  = subparsers.add_parser("info",  help="Display info on how to use this build system.")
    parser_info.set_defaults(func=cmd_info)

    arguments = parser.parse_args()

    pymk_root = os.path.dirname(os.path.abspath(__file__))
    entity_map = Build_system_entity_mapper(pymk_root)

    arguments.func(entity_map, pymk_root, arguments)



if __name__ == "__main__":
    main()