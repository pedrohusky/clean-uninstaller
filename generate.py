from genericpath import isdir
import os
import shutil
import subprocess
import sys
import concurrent.futures
import time

def get_program_path(exe_name="UniClean.exe"):
    if getattr(sys, "frozen", False):  # Check if running as a PyInstaller executable
        base_path = sys._MEIPASS  # Get the executable's directory
    else:
        base_path = os.path.abspath(
            os.path.dirname(__file__)
        )  # Use the script's directory

    program_path = os.path.join(
        base_path, "dist", exe_name
    )  # Build the path to Clean Uninstall.exe
    return program_path

def cleanup(item):
    item_path = os.path.basename(item) + ".spec"
    if os.path.exists(item_path):
        os.remove(item_path)
    
def clean_up_all(even_installer):
    dist = os.path.join("dist")
    build = os.path.join("build")
    
    if os.path.exists(dist):
        for item in os.listdir(dist):
            if even_installer:
                shutil.rmtree(os.path.join(dist))
                continue
            if "installer-" not in item:
                if os.path.isdir(os.path.join(dist, item)):
                    shutil.rmtree(os.path.join(dist, item))
                else:
                    os.remove(os.path.join(dist, item))
    
    if os.path.exists(build):
        shutil.rmtree(build)
    
    
    


def generate_executable(script_name, exe_name):
    try:
        # Get the path to Clean Uninstall.exe using the get_program_path function
        program_path = get_program_path()
        uninstaller_path = get_program_path("uninstaller.exe")
        icon_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "icon", "icon.ico"
        )
        localization_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "localization"
        )
        
        settings_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "settings"
        )

        # Prepare the PyInstaller command
        if script_name == "tools\\install_ui.py":
            command = [
                "pyinstaller",
                "--name",
                exe_name,  # Set the name of the generated executable
                "--onefile",
                "--noconsole",
                "--uac-admin",
                "--add-binary",
                f"{program_path};.",
                "--add-binary",
                f"{uninstaller_path};.",
                "--add-data",
                f"{icon_path};.",
                "--add-data",
                f"{localization_path};localization",
                "--add-data",
                f"{settings_path};settings",
                "--icon",
                f"{icon_path}",
                # Add "UniClean.exe" to the root directory of the generated executable
                script_name,
            ]
        else:
            command = [
                "pyinstaller",
                "--name",
                exe_name,  # Set the name of the generated executable
                "--onefile",
                "--noconsole",
                "--uac-admin",
                "--add-data",
                f"{icon_path};.",
                "--icon",
                f"{icon_path}",
                # Add "UniClean.exe" to the root directory of the generated executable
                script_name,
            ]

        # Run PyInstaller
        subprocess.check_call(command)

        print(
            f"Executable '{script_name}.exe' created successfully in the 'dist' folder."
        )
        
        cleanup(exe_name)

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    script_location = os.path.abspath(__file__)

    platform = sys.platform
    
    clean_up_all(True)

    if platform == "linux" or platform == "darwin":
        path_separator = "/"
        exe_extension = ""  # No extension needed for Linux and macOS
    else:
        path_separator = "\\"
        exe_extension = ".exe"  # Add .exe extension for Windows
        
    start_time = time.time()  # Record the start time

    # Create a ThreadPoolExecutor to generate the uninstaller and UniClean concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        uninstaller_future = executor.submit(generate_executable, f"tools{path_separator}uninstaller.py", f"uninstaller{exe_extension}")
        uniclean_future = executor.submit(generate_executable, "clean_uninstall.py", f"UniClean{exe_extension}")

        # Wait for both tasks to complete
        concurrent.futures.wait([uninstaller_future, uniclean_future])

    # Now that both the uninstaller and UniClean are generated, generate the installer
    generate_executable(f"tools{path_separator}install_ui.py", f"UniClean-installer-v1.0{exe_extension}")
    
    # Calculate the time spent on generating the installer
    elapsed_time = time.time() - start_time
    print(f"Time spent on generating the installer: {elapsed_time:.2f} seconds")
        
    clean_up_all(False)
