import os
import re
import xml.dom.minidom as mxml


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



class EntityFinder(object):
    def __init__(self, root_path, exclude_dir_names=[]):
        self.apps    = []
        self.tests   = []
        self.modules = []

        self.total_c_files = 0
        self.total_h_files = 0

        self.dir_root = root_path
        self.exclude_dirs = [".git", "_build", "framework"]
        self.exclude_dirs.extend(exclude_dir_names)

    def get_apps(self):
        return self.apps


    def get_tests(self):
        return self.tests


    def get_modules(self):
        return self.modules


    def _find_entities(self):
        re_test_file        = re.compile(".*\.test")
        re_app_file         = re.compile(".*\.executable")
        re_module_file      = re.compile(".*\.module")
        re_c_file           = re.compile(".*\.c")
        re_h_file           = re.compile(".*\.h")

        build_sys_root = self.dir_root.split(os.path.sep)
        for root, dirs, files in os.walk(self.dir_root):
            rel_path = root.replace(self.dir_root+os.sep, "")
            
            dir_path_list = root.split(os.path.sep)
            dir_path_list = [d for d in dir_path_list if d not in build_sys_root]
            if list(set(dir_path_list) & set(self.exclude_dirs)) != []:
                continue

            for file in files:
                enty = Entity()
                if re_test_file.match(file):
                    enty.fetch_info_from_xml_file(os.path.join(root, file))
                    enty.rel_path = rel_path
                    self.tests.append(enty)

                elif re_app_file.match(file):
                    enty.fetch_info_from_xml_file(os.path.join(root, file))
                    enty.rel_path = rel_path
                    self.apps.append(enty)

                elif re_module_file.match(file):
                    enty.fetch_info_from_xml_file(os.path.join(root, file))
                    enty.rel_path = rel_path
                    self.modules.append(enty)

                elif re_c_file.match(file):
                    self.total_c_files += 1

                elif re_h_file.match(file):
                    self.total_h_files += 1


    def _get_dependency_items(self, dependency_name):
        for mod in self.modules:
            if mod.name == dependency_name:
                return mod
        return None


    def _map_dependencies(self):
        for enty in (self.modules+self.apps+self.tests):
            while enty.unsatisfied_deps != []:
                dep_name = enty.unsatisfied_deps.pop(0)
                dep_ref  = self._get_dependency_items(dep_name)
                if dep_ref != None:
                    enty.dependencies.append(dep_ref)
                else:
                    print("Missing dependency in "+enty.name+". Missing dependency: "+dep_name)


    def _print_stats(self):
        print("======[Entities]======")
        print("Modules:      "+str(len(self.modules)))
        print("Applications: "+str(len(self.apps)))
        print("Tests:        "+str(len(self.tests)))

        print("")

        print("======[Files]=========")
        print("Total c files: "+str(self.total_c_files))
        print("Total h files: "+str(self.total_h_files))

        print("")


    def run(self):
        self._find_entities()
        self._map_dependencies()

        self._print_stats()
