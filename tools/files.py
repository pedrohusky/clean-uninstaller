import os
import re
import shutil
import subprocess
import time


class Files:
    def __init__(self, uninstaller):
        super().__init__()
        self.uninstaller = uninstaller

    def find_program_installation_path(self):
        # Initialize a set to store unique paths
        paths = []
        print(f"Step 1: Initialize paths as a set: {paths}")

        # Find the uninstaller and other executable paths
        _, filtered_exe, _ = self.get_best_matching_exe([self.uninstaller.path])
        print(f"Step 2: Found program executable: {filtered_exe}, program name: {self.uninstaller.program_name}")

        # Specify common program files directories to search
        program_files_paths = ["C:\\Program Files", "C:\\Program Files (x86)"]
        print(f"Step 3: Searching in program files paths: {program_files_paths}")

        # Iterate through the program files directories
        for program_files_path in program_files_paths:
            for root, dirs, _ in os.walk(program_files_path):
                if self.uninstaller.program_name in dirs:
                    program_installation_path = os.path.join(root, self.uninstaller.program_name)
                    paths.append(program_installation_path)
                    print(f"Step 4: Found program installation path: {program_installation_path}")
                elif self.uninstaller.folder_name in dirs:
                    program_installation_path = os.path.join(root, self.uninstaller.folder_name)
                    paths.append(program_installation_path)
                    print(f"Step 4: Found program installation path: {program_installation_path}")

        # Convert the set of paths to a list
        unique_paths = list(paths)
        print(f"Step 5: Unique paths found: {unique_paths}")

        # Return the list of paths if any are found
        if unique_paths:
            return unique_paths

        # Return None if no program installations are found
        return [self.uninstaller.path]

    def get_best_matching_exe(self, paths, main_folder_names=['Application', 'Program']):
        """
        Given a list of paths, return the best matching executable file as an uninstaller
        (with the main executable beside it).
        """
        best_uninstaller = None
        best_remaining_executable = None
        detected_executables = set()  # Use a set to ensure unique values

        for path in paths:
            # Collect all detected executable files
            detected_files = []

            for root, dirs, files in os.walk(path):
                for filename in files:
                    if filename.lower().endswith('.exe'):
                        exe_path = os.path.join(root, filename)
                        # Get the base name of the exe_path
                        exe_base_name = os.path.basename(exe_path).lower()

                        # Check if the base name matches the pattern
                        if ' ' not in exe_base_name and 'unins' in exe_base_name:
                            best_uninstaller = exe_path
                            continue
                        else:
                            # Check if the executable is inside a folder with a main_folder_name
                            folder_name = os.path.basename(os.path.dirname(exe_path))
                            if any(name.lower() in folder_name.lower() for name in main_folder_names):
                                if best_remaining_executable is None:
                                    best_remaining_executable = exe_path

                        detected_files.append(exe_path)

            # Sort the detected files by size
            detected_files.sort(key=lambda f: os.path.getsize(f), reverse=True)

            # Update the best remaining executable
            if detected_files:
                if best_remaining_executable is None:
                    best_remaining_executable = detected_files[0]

            # Add all detected executable files (excluding uninstallers) to the set
            detected_executables.update(detected_files)

        try:
            self.uninstaller.program_name = os.path.basename(best_remaining_executable).replace('.exe', '')
        except TypeError:
            self.uninstaller.program_name = self.uninstaller.folder_name

        # Convert the set back to a list to maintain order
        detected_executables = list(detected_executables)

        # Return the best uninstaller, the best remaining executable, and all detected executable files
        return best_uninstaller, best_remaining_executable, detected_executables

    @staticmethod
    def remove_files_and_folders(paths_to_remove):
        for removed_path in paths_to_remove:
            if os.path.exists(removed_path) and os.path.isdir(removed_path):
                shutil.rmtree(removed_path)
            else:
                os.remove(removed_path)

    @staticmethod
    def start_program_uninstaller(uninstaller_path):
        # Start the uninstaller executable
        uninstaller_process = subprocess.Popen(uninstaller_path)

        # Wait for the uninstaller to finish
        uninstaller_process.wait()
        time.sleep(2)
