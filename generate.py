import os
import shutil
import subprocess
import sys


def get_program_path(exe_name="Clean Uninstall.exe"):
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
        base_path = sys._MEIPASS  # Get the executable's directory
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))  # Use the script's directory

    program_path = os.path.join(base_path, 'dist', exe_name)  # Build the path to Clean Uninstall.exe
    return program_path

def generate_executable(script_name, exe_name):
    try:
        # Get the path to Clean Uninstall.exe using the get_program_path function
        program_path = get_program_path()
        uninstaller_path = get_program_path("uninstaller.exe")
        icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icon', 'icon.ico')  # Use the script's directory
        if script_name == "clean_uninstall.py":
            shutil.rmtree(get_program_path(exe_name=""), ignore_errors=True)

        # Prepare the PyInstaller command
        if script_name == "installer.py":
            command = [
                "pyinstaller",
                "--name", exe_name,  # Set the name of the generated executable
                "--onefile",
               # "--noconsole",
                "--uac-admin",
                "--add-binary", f"{program_path};.",
                "--add-binary", f"{uninstaller_path};.",
                "--add-data", f"{icon_path};.",
                "--icon", f"{icon_path}",
                # Add "Clean Uninstall.exe" to the root directory of the generated executable
                script_name,
            ]
        else:
            command = [
                "pyinstaller",
                "--name", exe_name,  # Set the name of the generated executable
                "--onefile",
                #"--noconsole",
                "--uac-admin",
                "--add-data", f"{icon_path};.",
                "--icon", f"{icon_path}",
                # Add "Clean Uninstall.exe" to the root directory of the generated executable
                script_name,
            ]

        # Run PyInstaller
        subprocess.check_call(command)

        print(f"Executable '{script_name}.exe' created successfully in the 'dist' folder.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    script_location = os.path.abspath(__file__)
    # The script_name is the name of the script you want to convert to an EXE.
    # In this case, we are using "installer.py".
    generate_executable("tools\\uninstaller.py", exe_name="uninstaller.exe")  # Pass the desired executable name
    generate_executable("tools\\clean_uninstall.py", exe_name="Clean Uninstall.exe")  # Pass the desired executable name
    generate_executable("installer.py", exe_name="Clean Uninstall v1.0-installer.exe")  # Pass the desired executable name
