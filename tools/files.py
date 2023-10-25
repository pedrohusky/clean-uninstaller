import os
import shutil
import subprocess
import psutil
import concurrent.futures


class Files:
    def __init__(self, uninstaller):
        super().__init__()
        self.uninstaller = uninstaller

    def get_system_overall_info(self, program_size):
        root_drive = os.path.splitdrive(os.getcwd())[0]  # Get the root drive (e.g., C:)
        disk_usage = psutil.disk_usage(root_drive)

        # Calculate the free space after uninstalling
        # You should replace this with the actual space you'll free up
        space_freed_up = program_size  # Replace this with the actual value in MB

        system_info = {
            "total_space": disk_usage.total,
            "free_space_before": disk_usage.free,
            "free_space_after": disk_usage.free
            + space_freed_up,  # This is a placeholder value, replace it
        }

        sizes = ["GB", "MB", "KB"]
        size_converted = 0
        unit = ""
        for size in sizes:
            size_converted = float(
                "{:.2f}".format(
                    self.convert_bytes(system_info["free_space_before"], size)
                )
            )
            if size_converted > 1:
                unit = size
                break

        system_info["free_space_before_converted"] = size_converted
        system_info["free_space_before_unit"] = unit

        # Now, calculate the unit for free_space_after
        unit = ""
        for size in sizes:
            size_converted = float(
                "{:.2f}".format(
                    self.convert_bytes(system_info["free_space_after"], size)
                )
            )
            if size_converted > 1:
                unit = size
                break

        system_info["free_space_after_converted"] = size_converted
        system_info["free_space_after_unit"] = unit

        return system_info

    def get_directory_info(self, paths):
        total_size = 0
        file_count = 0
        dir_count = 0

        for path in paths:
            for dirpath, dirnames, filenames in os.walk(path):
                file_count += len(filenames)
                dir_count += len(dirnames)

                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)

        sizes = ["GB", "MB", "KB"]
        size_converted = 0
        unit = ""
        for size in sizes:
            size_converted = float(
                "{:.2f}".format(self.convert_bytes(total_size, size))
            )
            if size_converted > 1:
                unit = size
                break

        return {
            "size": {
                "total_size_converted": size_converted,
                "total_size": total_size,
                "unit": unit,
            },
            "file_count": file_count,
            "dir_count": dir_count,
        }

    @staticmethod
    def convert_bytes(size, unit=None):
        if unit == "KB":
            return size / 1024
        elif unit == "MB":
            return size / (1024 * 1024)
        elif unit == "GB":
            return size / (1024 * 1024 * 1024)
        else:
            return size

    def find_program_installation_path(self):
        # Initialize a set to store unique paths
        paths = set()
        print(f"Step 1: Initialize paths as a set: {paths}")

        # Find the uninstaller and other executable paths
        _, filtered_exe, _ = self.get_best_matching_exe([self.uninstaller.path])
        print(
            f"Step 2: Found program executable: {filtered_exe}, program name: {self.uninstaller.program_name}"
        )

        # Specify common program files directories to search
        common_program_directories = []

        if os.name == "posix":  # For macOS and Linux
            common_program_directories.extend(
                ["/usr/local", "/opt", os.path.expanduser("~/.local/share")]
            )
        elif os.name == "nt":  # For Windows
            common_program_directories.extend(
                [
                    os.path.join(os.environ["ProgramFiles"]),
                    os.path.join(os.environ["ProgramFiles(x86)"]),
                    os.path.join(
                        os.environ["ProgramData"],
                        "Microsoft",
                        "Windows",
                        "Start Menu",
                        "Programs",
                    ),
                    os.path.join(
                        os.environ["ProgramData"],
                        "Microsoft",
                        "Windows",
                        "Start Menu",
                        "Programs",
                        "Startup",
                    ),
                    os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs"),
                    os.path.expanduser("~\\AppData\\Local"),
                    os.path.expanduser("~\\AppData\\Roaming"),
                ]
            )

        print(f"Step 3: Searching in program files paths: {common_program_directories}")

        # Use concurrent.futures for parallel directory scanning
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []

            for program_files_path in common_program_directories:
                futures.append(
                    executor.submit(self.scan_directory, program_files_path, paths)
                )

            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

        # Convert the set of paths to a list
        unique_paths = list(paths)
        print(f"Step 5: Unique paths found: {unique_paths}")

        # Return the list of paths if any are found
        if unique_paths:
            return unique_paths

        # Return None if no program installations are found
        return [self.uninstaller.path] if os.path.exists(self.uninstaller.path) else []

    def scan_directory(self, directory, paths):
        for entry in os.scandir(directory):
            if entry.is_dir():
                dir_name = entry.name
                if (
                    self.uninstaller.program_name.lower() in dir_name.lower()
                    or self.uninstaller.folder_name.lower() in dir_name.lower()
                ):
                    # Check if the new path is not a sub path of any existing path in paths
                    dir_path = entry.path
                    is_sub_path = any(
                        dir_path.startswith(existing_path) for existing_path in paths
                    )

                    if not is_sub_path:
                        paths.add(dir_path)
                        print(f"Found program installation path: {dir_path}")
                    else:
                        print(f"Would be added to an existing path: {dir_path}")

            elif entry.is_file() and entry.name.lower().endswith(".lnk"):
                # Check if the file is a shortcut and contains the program name
                if (
                    self.uninstaller.program_name in entry.name
                    or self.uninstaller.folder_name in entry.name
                ):
                    shortcut_path = entry.path

                    paths.add(shortcut_path)
                    print(f"Found program installation path: {shortcut_path}")

    def get_best_matching_exe(
        self, paths, main_folder_names=["Application", "Program"]
    ):
        best_uninstaller = None
        best_remaining_executable = None
        detected_executables = set()
        best_uninstaller_score = 0
        best_remaining_executable_score = 0

        detected_files = []

        def score_file(exe_path):
            nonlocal best_uninstaller, best_uninstaller_score
            nonlocal best_remaining_executable, best_remaining_executable_score

            exe_base_name = os.path.basename(exe_path).lower()

            # Initialize a score for each executable
            score = 0

            # Check for "32" or "64" in the base name
            if "32" in exe_base_name or "64" in exe_base_name:
                score += 1 / 32 if "32" in exe_base_name else 1 / 64

            # Consider file size in scoring
            file_size = os.path.getsize(exe_path)
            if file_size > 0:
                score += file_size / (file_size / 3)

            # Assign a higher score to shallower depths
            depth = len(exe_path.split(os.sep))
            score += 1 / (depth + 1)  # Now, deeper paths will receive lower scores

            # Check if it's an uninstaller
            if "unins" in exe_base_name:
                if best_uninstaller is None or score > best_uninstaller_score:
                    best_uninstaller = exe_path
                    best_uninstaller_score = score
            else:
                # Check if the executable is inside a folder with a main_folder_name
                folder_name = os.path.basename(os.path.dirname(exe_path))
                if any(
                    name.lower() in folder_name.lower() for name in main_folder_names
                ):
                    if (
                        best_remaining_executable is None
                        or score > best_remaining_executable_score
                    ):
                        best_remaining_executable = exe_path
                        best_remaining_executable_score = score

            detected_files.append((exe_path, score))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for path in paths:
                for root, dirs, files in os.walk(path):
                    for filename in files:
                        if filename.lower().endswith(".exe"):
                            exe_path = os.path.join(root, filename)
                            executor.submit(score_file, exe_path)

        # Sort the detected files by score
        detected_files.sort(key=lambda x: x[1], reverse=True)

        # Update the best remaining executable
        if detected_files:
            best_remaining_executable = detected_files[0][0]

        if len(detected_files) > 0:
            # Add all detected executable files (excluding uninstallers) to the set
            detected_executables.update(exe[0] for exe in detected_files)

        print(detected_files)

        try:
            self.uninstaller.program_name = (
                os.path.basename(best_remaining_executable)
                .replace(".exe", "")
                .replace("64", "")
                .replace("32", "")
            )
        except TypeError:
            self.uninstaller.program_name = self.uninstaller.folder_name

        detected_executables = list(detected_executables)

        return best_uninstaller, best_remaining_executable, detected_executables

    @staticmethod
    def remove_files_and_folders(paths_to_remove):
        for removed_path in paths_to_remove:
            try:
                if os.path.exists(removed_path) and os.path.isdir(removed_path):
                    shutil.rmtree(removed_path)
                elif os.path.exists(removed_path):
                    os.remove(removed_path)
            except Exception as e:
                print(f"Failed to remove: {removed_path} - {e}")

    @staticmethod
    def start_program_uninstaller(uninstaller_path):
        # Start the uninstaller executable
        subprocess.Popen(uninstaller_path)
