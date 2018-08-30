import os
import subprocess

from tester_base import TesterBase

RELATIVE_CMOCK_GENERATOR_PATH = os.path.join("framework", "CMock", "lib", "cmock.rb")

class UnityTester(TesterBase):
    def __init__(self, entity, pymk_root, args):
        TesterBase.__init__(self)

        self.apps    = entity.apps
        self.modules = entity.modules

        self.root_path = pymk_root


    def _should_mock_file(self, h_file_path, mock_folder_path):
        h_file_base_name = os.path.basename(h_file_path)
        mock_h_file_base_name = "Mock"+h_file_base_name
        mock_c_file_base_name = "Mock"+(h_file_base_name.replace(".h","")+".c")

        mock_h_file_path = os.path.join(mock_folder_path, mock_h_file_base_name)
        mock_c_file_path = os.path.join(mock_folder_path, mock_c_file_base_name)

        if not (os.path.isfile(mock_h_file_path) and os.path.isfile(mock_c_file_path)):
            return True

        if os.path.getmtime(h_file_path) > os.path.getmtime(mock_h_file_path):
            return True

        return False


    # Create new mock files for all headers in modules and apps and place
    #   new mock file in a folder named mock in the same directory as the mocked header file.
    # Only create the mock file from the header file if the mock file does not exist in the folder
    #   named mock or the timestamp on the mock file in older than the timestamp of the header file
    def prepare(self):
        original_cwd = os.getcwd()  # Save current working directory for restoration at a later time

        cmock_path = os.path.join(self.root_path, RELATIVE_CMOCK_GENERATOR_PATH)

        for module in self.modules:
            module_folder_path = os.path.join(self.root_path, module.rel_path)
            mock_folder_path   = os.path.join(module_folder_path, "mocks")
            
            if not os.path.isdir(mock_folder_path):
                if os.path.exists(mock_folder_path):
                    print("File with name \"mock\" in "+module_folder_path+" blocks creation of mock folder!!")
                else:
                    os.makedirs(mock_folder_path)

            os.chdir(module_folder_path)

            
            for file in module.includes:
                header_file_to_mock = os.path.join(self.root_path, module.rel_path, file)
                cmd = ["ruby", cmock_path, header_file_to_mock]


                if self._should_mock_file(header_file_to_mock, mock_folder_path):
                    try:
                        subprocess.check_call(cmd)
                        #print(cmd)
                    except CalledProcessError:
                        os.chdir(original_cwd)
                        raise CalledProcessError
                

        os.chdir(original_cwd)


    def run(self):
        pass
