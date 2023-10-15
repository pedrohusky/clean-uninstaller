import os
import sys
from processes import Processes
from registry import Registry
from tools.files import Files
from tools.ui import UninstallerUI


class Uninstaller:
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.folder_name = os.path.basename(path)
        self.program_name = ""
        self.registry = Registry(self)
        self.processes = Processes()
        self.files = Files(self)
        self.UI = UninstallerUI(self)

        self.processes_to_terminate = []

    def retrieve_information(self):
        program_paths = self.files.find_program_installation_path()
        uninstaller_exe, filtered_exe, executable_paths = self.files.get_best_matching_exe(program_paths)
        registry_files = self.registry.find_and_remove_registry_entries(read_only=True)
        open_processes = self.processes.find_processes_to_terminate(executable_paths, read_only=True)
        return program_paths, uninstaller_exe, filtered_exe, executable_paths, registry_files, open_processes

    def uninstall(self, program_paths=None, uninstaller_exe=None, filtered_exe=None,
                  executable_paths=None, registry_files=None, open_processes=None):
        self.processes.find_processes_to_terminate(executable_paths, read_only=False,
                                                   processes_to_terminate=open_processes)

        if uninstaller_exe is not None:
            self.files.start_program_uninstaller(uninstaller_exe)

        print(f"Uninstalling paths {program_paths}...")

        self.files.remove_files_and_folders(program_paths)

        print(f"Uninstalling registry paths {registry_files}...")

        self.registry.find_and_remove_registry_entries(read_only=False, registry_files=registry_files)

        input("Press enter to continue...")

        self.UI.close_ui()

    def start_uninstaller(self):
        self.UI.create_confirmation_ui()


# Example usage:
if __name__ == "__main__":
    # Check if at least one command-line argument is provided
    if len(sys.argv) < 2:
        print("Usage: my_uninstaller.exe <program_path>")
    else:
        uninstaller = Uninstaller(sys.argv[1])
        uninstaller.UI.create_confirmation_ui()
