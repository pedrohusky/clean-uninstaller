import os
import sys
from PyQt6.QtWidgets import QMessageBox
from tools.processes import Processes
from tools.registry import Registry
from tools.files import Files
from tools.ui import UninstallerUI
from windows.settings_window import MySettingsWindow
from windows.about_window import MyAboutWindow


class Uninstaller:
    def __init__(self, path):
        super().__init__()
        self.current_version = "v1.0"
        self.path = path
        self.folder_name = os.path.basename(path)
        self.program_name = ""
        self.registry = Registry(self)
        self.processes = Processes()
        self.files = Files(self)
        # Check if the script is running from the temporary directory
        program_dir = os.path.dirname(os.path.abspath(sys.executable))
        self.UI = UninstallerUI(self, os.path.join(program_dir))
        self.settings_window = None
        self.about_window = None

        self.processes_to_terminate = []

    def init_windows(self):
        self.settings_window = MySettingsWindow(self.UI)
        self.about_window = MyAboutWindow(self.UI)

    def retrieve_information(self):
        program_paths = self.files.find_program_installation_path()
        if len(program_paths) == 1 and program_paths[0].endswith(".lnk"):
            uninstaller_exe, filtered_exe, executable_paths = None, None, None
            open_processes = self.processes.find_processes_to_terminate(
                program_paths, read_only=True
            )
        else:
            (
                uninstaller_exe,
                filtered_exe,
                executable_paths,
            ) = self.files.get_best_matching_exe(program_paths)
            open_processes = self.processes.find_processes_to_terminate(
                executable_paths, read_only=True
            )

        if os.name == "posix":  # For macOS and Linux
            registry_files = None
        elif os.name == "nt":  # For Windows
            registry_files = self.registry.find_and_remove_registry_entries(
                read_only=True
            )

        return (
            program_paths,
            uninstaller_exe,
            filtered_exe,
            executable_paths,
            registry_files,
            open_processes,
        )

    def uninstall(
        self,
        program_paths=None,
        uninstaller_exe=None,
        executable_paths=None,
        registry_files=None,
        open_processes=None,
    ):
        # Are you sure messagebox
        messagebox = QMessageBox()
        messagebox.setWindowIcon(self.UI.icon)
        messagebox.setWindowTitle("Are you sure?")
        messagebox.setText(f"Are you sure you want to uninstall {self.folder_name}?")
        messagebox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        messagebox.setDefaultButton(QMessageBox.StandardButton.No)
        messagebox.setIcon(QMessageBox.Icon.Question)
        result = messagebox.exec()

        if result == 65536 or not result:
            return

        if open_processes:
            self.processes.find_processes_to_terminate(
                executable_paths, read_only=False, processes_to_terminate=open_processes
            )

        if uninstaller_exe and os.name == "nt":
            self.files.start_program_uninstaller(uninstaller_exe)
            # Are you sure messagebox
            messagebox = QMessageBox()
            messagebox.setWindowTitle(
                "Please DO NOT CLOSE UNTIL THE UNINSTALL IS COMPLETE"
            )
            messagebox.setWindowIcon(self.UI.icon)
            messagebox.setText("Only press YES after the program uninstall finishes.")
            messagebox.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            messagebox.setDefaultButton(QMessageBox.StandardButton.No)
            messagebox.setIcon(QMessageBox.Icon.Warning)

        print(f"Uninstalling registry paths {registry_files}...")

        if registry_files:
            self.registry.find_and_remove_registry_entries(
                read_only=False, registry_files=registry_files
            )

        print(f"Uninstalling paths {program_paths}...")

        if program_paths:
            self.files.remove_files_and_folders(program_paths)

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
