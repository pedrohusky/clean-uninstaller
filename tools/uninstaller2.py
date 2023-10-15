import atexit
import ctypes
import locale
import os
import shutil
import subprocess
import sys
import tempfile
import time
import winreg as reg

from tools.files import Files
from tools.registry import Registry

language_translations = {
    'en_US': 'Uninstall Program',
    'es_ES': 'Desinstalar Programa',  # Spanish
    'fr_FR': 'Désinstaller Programme',  # French
    'de_DE': 'Programm deinstallieren',  # German
    'it_IT': 'Disinstalla Programma',  # Italian
    'pt_BR': 'Desinstalar Programa',  # Portuguese
    'zh_CN': '卸载程序',  # Chinese (Simplified)
    'ja_JP': 'プログラムをアンインストール',  # Japanese
    'ko_KR': '프로그램 제거',  # Korean
    'ru_RU': 'Деинсталляция программы',  # Russian
    'ar_SA': 'إلغاء تثبيت البرنامج',  # Arabic (Saudi Arabia)
    'hi_IN': 'प्रोग्राम को अनइंस्टॉल करें',  # Hindi
    'tr_TR': 'Program Kaldır',  # Turkish
    'nl_NL': 'Programma Deïnstalleren',  # Dutch
    'sv_SE': 'Avinstallera Program',  # Swedish
    'pl_PL': 'Odinstaluj Program',  # Polish
    # Add more languages and translations as needed
}


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def remove_custom_context_menu_command(menu_name):
    try:
        if is_admin():
            key = r'Folder\shell\{}'.format(menu_name)
            Registry(None).delete_sub_key(reg.HKEY_CLASSES_ROOT, [key], should_delete=True)
            backup_path = os.path.join(os.environ['ProgramFiles'], get_custom_menu_name(), 'registry_backup.reg')

            if os.path.exists(backup_path):
                try:
                    print(f"Restoring the registry key from the backup: {backup_path}")
                    subprocess.run(["reg", "import", backup_path], check=True)
                    print("Restored the registry key from the backup successfully.")

                except Exception as e:
                    print(f"Error while restoring the registry key from the backup: {e}")

        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    except Exception as e:
        output = "Error: " + str(e)
        print(output)


def get_custom_menu_name():
    # Get the current OS language
    os_language = locale.getdefaultlocale()[0]

    # Use the language to determine the custom menu name
    custom_menu_name = language_translations.get(os_language, "Uninstall Program")
    return custom_menu_name


def uninstall_program(program_dir):
    try:
        if os.path.exists(program_dir):
            # Recursively remove the program directory and all its contents
            uninstaller_path = None
            for root, dirs, files in os.walk(program_dir, topdown=False):
                try:
                    for name in files:
                        file_path = os.path.join(root, name)
                        if 'uninstaller.exe' in file_path:
                            uninstaller_path = file_path
                        else:
                            os.remove(file_path)
                    for name in dirs:
                        dir_path = os.path.join(root, name)
                        os.rmdir(dir_path)
                except:
                    continue

            print(f"Removed program directory and all its contents: {program_dir}")
            return uninstaller_path

        # Additional cleanup steps, e.g., removing shortcuts, configuration files, etc.

    except Exception as e:
        print("Error Uninstalling:", e)

def generate_temp_path_in_appdata(file_name):
    # Get the path to the user's %APPDATA% directory
    appdata_dir = os.path.expanduser(os.path.join("~", "AppData", "Roaming"))

    # Create a subdirectory within %APPDATA% for your temporary file
    temp_dir = os.path.join(appdata_dir, "YourAppName")

    # Ensure the directory exists or create it if it doesn't
    os.makedirs(temp_dir, exist_ok=True)

    # Create the full path to the temporary file within the subdirectory
    temporary_path = os.path.join(temp_dir, file_name)

    return temporary_path, temp_dir

def schedule_deletion(exe, program_directory, temporary_path):

    # Create a batch file with the deletion command
    batch_file = os.path.join(temporary_path, "deletion_script.bat")
    # Schedule the temporary script for deletion upon system restart
    deletion_command = (
        f'timeout /t 1 && del /f /q "{exe}" && '
        f'del /f /q "{batch_file}" && '
        f'rmdir /s /q "{program_directory}"'
    )
    print(deletion_command)
    input(f"Deleting {exe}...")

    with open(batch_file, "w") as f:
        f.write(deletion_command)

    subprocess.Popen(['cmd', '/c', batch_file], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

def copy_self_to_temp():
    # Get the script's current directory and filename
    program_dir = os.path.join(os.environ['ProgramFiles'], get_custom_menu_name(), 'uninstaller.exe')  # Replace with the program installation directory
    script_filename = os.path.basename(program_dir)

    # Generate a temporary directory for the script
    temp_dir = tempfile.gettempdir()
    temp_script_path = os.path.join(temp_dir, "uninstaller_temporary.exe")
    input(f"Copying {program_dir} to {temp_script_path}...")

    # Copy the script to the temporary directory
    shutil.copyfile(program_dir, temp_script_path)

    return temp_script_path
if __name__ == "__main__":
    # Check if the script is running from the temporary directory
    print(f"Running from temporary directory: {sys.executable}")
    if tempfile.gettempdir() in sys.executable:
        # This is the copied script in the temp directory, trigger the uninstall
        menu_name = get_custom_menu_name()  # Replace with the name of the context menu command
        program_dir = os.path.join(os.environ['ProgramFiles'],
                                   get_custom_menu_name())  # Replace with the program installation directory
        temp_path = os.path.join(tempfile.gettempdir())

        remove_custom_context_menu_command(menu_name)
        #uninstaller_path = uninstall_program(program_dir)
        #input(f"Uninstalling {uninstaller_path}...")
        # Now remove all files inside the program_dir, and then, remove program_dir folder itself using os.walk
        path = os.path.join(tempfile.gettempdir(), "uninstaller_temporary.exe")
        Files(None).remove_files_and_folders([program_dir])
        schedule_deletion(path, program_directory=program_dir, temporary_path=temp_path)
    else:
        # This is the original script, copy it to the temp directory, start the copied script, and terminate the original
        temp_script_path = copy_self_to_temp()
        print(f"Script copied to {temp_script_path}")
        input("Press Enter to continue...")
        subprocess.Popen([temp_script_path], shell=True)
        sys.exit()
