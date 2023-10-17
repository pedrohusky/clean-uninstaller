import locale
import os
import ctypes
import shutil
import sys
import winreg as reg

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

def get_custom_menu_name():
    # Get the current OS language
    os_language = locale.getdefaultlocale()[0]

    # Use the language to determine the custom menu name
    custom_menu_name = language_translations.get(os_language, "Uninstall Program")
    return custom_menu_name


# Determine the target installation directory (e.g., "Program Files" or "Program Files (x86)")
MAIN_DIR = os.path.join(os.environ['ProgramFiles'], get_custom_menu_name())

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    MAIN_EXECUTABLE_PATH = sys._MEIPASS
else:
    MAIN_EXECUTABLE_PATH = os.path.dirname(os.path.abspath(__file__))


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def add_custom_context_menu_command(menu_name, command, icon_path=None):
    try:
        if is_admin():
            key = r'Folder\shell\{}'.format(menu_name)
            reg.CreateKey(reg.HKEY_CLASSES_ROOT, key)
            key_handle = reg.OpenKey(reg.HKEY_CLASSES_ROOT, key, 0, reg.KEY_WRITE)
            reg.SetValue(key_handle, '', reg.REG_SZ, menu_name)

            if icon_path:
                # Ensure the icon path is absolute
                reg.SetValueEx(key_handle, 'Icon', 0, reg.REG_SZ, icon_path)

            command_key = reg.CreateKey(key_handle, 'command')
            reg.SetValue(command_key, '', reg.REG_SZ, command)

            reg.CloseKey(command_key)
            reg.CloseKey(key_handle)

            print(f"Added '{menu_name}' to the context menu.")
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    except Exception as e:
        output = "Error: " + str(e)
        print(output)


def copy_program_to_installation_directory(path, name="UniClean.exe"):
    try:
        print(f"Copying {name} to the installation directory...")

        # Create the target directory if it doesn't exist
        os.makedirs(MAIN_DIR, exist_ok=True)

        new_dir = os.path.join(MAIN_DIR, name)

        # Copy "UniClean.exe" to the target directory
        shutil.copy2(path, new_dir)
        print(f"Copied {name} to the installation directory.")
        return new_dir

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    menu_name = get_custom_menu_name()  # Replace with the name of the command you want to add
    program_script = "UniClean.exe"  # Replace with the name of your Python script
    program_script_path = os.path.join(MAIN_EXECUTABLE_PATH, program_script)
    new_folder = copy_program_to_installation_directory(program_script_path)
    icon_path = copy_program_to_installation_directory(os.path.join(MAIN_EXECUTABLE_PATH, "icon.ico"), "icon.ico")
    copy_program_to_installation_directory(os.path.join(MAIN_EXECUTABLE_PATH, "uninstaller.exe"),
                                           "UniClean-uninstaller.exe")
    command = f'"{new_folder}" "%1"'

    add_custom_context_menu_command(menu_name, command, icon_path=icon_path)
    #Registry(None).edit_context_menu_item(menu_name, command)

    input("Installation completed. Press Enter to exit...")

