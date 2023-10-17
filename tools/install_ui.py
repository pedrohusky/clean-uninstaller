import ctypes
import locale
import os
import shutil
import sys
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QFileDialog, QProgressBar, QStackedWidget
import winreg as reg

# Example usage:
app_name = "UniClean"
app_version = "1.0"
app_publisher = "PedroHusky"

language_translations = {
    'en_US': 'Uninstall',
    'es_ES': 'Desinstalar',  # Spanish
    'fr_FR': 'Désinstaller',  # French
    'de_DE': 'Deinstallieren',  # German
    'it_IT': 'Disinstalla',  # Italian
    'pt_BR': 'Desinstalar',  # Portuguese
    'zh_CN': '卸载',  # Chinese (Simplified)
    'ja_JP': 'アンインストール',  # Japanese
    'ko_KR': '제거',  # Korean
    'ru_RU': 'Деинсталляция',  # Russian
    'ar_SA': 'إلغاء التثبيت',  # Arabic (Saudi Arabia)
    'hi_IN': 'अनइंस्टॉल करें',  # Hindi
    'tr_TR': 'Kaldır',  # Turkish
    'nl_NL': 'Deïnstalleren',  # Dutch
    'sv_SE': 'Avinstallera',  # Swedish
    'pl_PL': 'Odinstaluj',  # Polish
    # Add more languages and translations as needed
}

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    MAIN_EXECUTABLE_PATH = sys._MEIPASS
else:
    MAIN_EXECUTABLE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_custom_menu_name():
    # Get the current OS language
    os_language = locale.getdefaultlocale()[0]

    # Use the language to determine the custom menu name
    custom_menu_name = language_translations.get(os_language, "Uninstall Program")
    return custom_menu_name


# Determine the target installation directory (e.g., "Program Files" or "Program Files (x86)")
MAIN_DIR = os.path.join(os.environ['ProgramFiles'], app_name)

program_script = "UniClean.exe"  # Replace with the name of your Python script
program_script_path = os.path.join(MAIN_EXECUTABLE_PATH, program_script)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def add_uninstaller_registry_entry(app_name, app_version, app_publisher, app_install_dir, app_icon_path,
                                   uninstaller_path):
    try:
        # Create a registry key for the application's uninstall information
        uninstall_key = f"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        with reg.CreateKey(reg.HKEY_LOCAL_MACHINE, uninstall_key) as key:
            reg.SetValueEx(key, "DisplayName", 0, reg.REG_SZ, app_name)
            reg.SetValueEx(key, "DisplayVersion", 0, reg.REG_SZ, app_version)
            reg.SetValueEx(key, "Publisher", 0, reg.REG_SZ, app_publisher)
            reg.SetValueEx(key, "InstallLocation", 0, reg.REG_SZ, app_install_dir)
            reg.SetValueEx(key, "DisplayIcon", 0, reg.REG_SZ, app_icon_path)
            reg.SetValueEx(key, "UninstallString", 0, reg.REG_SZ, uninstaller_path)
            reg.SetValueEx(key, "NoModify", 0, reg.REG_DWORD, 1)  # Set this as needed
            reg.SetValueEx(key, "NoRepair", 0, reg.REG_DWORD, 1)  # Set this as needed
            reg.SetValueEx(key, "QuietUninstallString", 0, reg.REG_SZ, uninstaller_path)  # Same as UninstallString

        return True
    except Exception as e:
        print("Error:", e)
        return False


def add_custom_context_menu_command(menu_name, command, icon_path=None):
    try:
        if is_admin():
            key = r'Folder\shell\{}'.format(app_name)
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


def copy_program_to_installation_directory(path, name="UniClean.exe", selected_path=None):
    try:
        if selected_path:
            final_path = selected_path
        else:
            final_path = MAIN_DIR

        if app_name not in final_path:
            final_path = final_path + f"/{app_name}"
        print(f"Copying {name} to the installation directory {final_path}...")

        print(f"Final path: {final_path}")

        # Create the target directory if it doesn't exist
        os.makedirs(final_path, exist_ok=True)

        new_dir = os.path.join(final_path, name)

        print(f"New dir: {new_dir}")

        # Copy "UniClean.exe" to the target directory
        shutil.copy2(path, new_dir)
        print(f"Copied {name} to the installation directory.")
        return new_dir

    except Exception as e:
        print("Error:", e)


class InstallationThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir
        print(f"Target dir: {self.target_dir}")

    def run(self):
        menu_name = get_custom_menu_name()  # Replace with the name of the command you want to add
        self.update_progress.emit(25)
        new_folder = copy_program_to_installation_directory(program_script_path, selected_path=self.target_dir)
        self.update_progress.emit(55)
        icon_path = copy_program_to_installation_directory(os.path.join(MAIN_EXECUTABLE_PATH, "icon.ico"),
                                                           "icon.ico", selected_path=self.target_dir)
        self.update_progress.emit(75)
        copy_program_to_installation_directory(os.path.join(MAIN_EXECUTABLE_PATH, "uninstaller.exe"),
                                               "UniClean-uninstaller.exe", selected_path=self.target_dir)
        self.update_progress.emit(85)
        command = f'"{new_folder}" "%1"'

        add_custom_context_menu_command(menu_name, command, icon_path=icon_path)

        self.update_progress.emit(95)

        app_install_dir = self.target_dir  # Replace with your installation directory
        app_icon_path = os.path.join(app_install_dir, "icon.ico")  # Replace with your application's icon path
        uninstaller_path = os.path.join(app_install_dir,
                                        "UniClean-uninstaller.exe")  # Replace with your uninstaller executable

        if add_uninstaller_registry_entry(app_name, app_version, app_publisher, app_install_dir, app_icon_path,
                                          uninstaller_path):
            print("Uninstaller registry entry added successfully.")
            self.update_progress.emit(100)
        else:
            print("Failed to add uninstaller registry entry.")


class InstallerUI(QMainWindow):
    def __init__(self, icon):
        super().__init__()

        self.target_dir_label = None
        self.selected_path = ''

        self.setWindowTitle("UniClean Installer")
        self.setGeometry(100, 100, 300, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.icon = QIcon(icon)
        self.setWindowIcon(self.icon)

        self.layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()
        self.welcome_screen = QWidget()
        self.path_selection_screen = QWidget()
        self.summary_screen = QWidget()
        self.installation_screen = QWidget()
        self.final_screen = QWidget()

        self.setup_welcome_screen()
        self.setup_path_selection_screen()
        self.setup_summary_screen()
        self.setup_installation_screen()
        self.setup_final_screen()

        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.path_selection_screen)
        self.stacked_widget.addWidget(self.summary_screen)
        self.stacked_widget.addWidget(self.installation_screen)
        self.stacked_widget.addWidget(self.final_screen)

        self.layout.addWidget(self.stacked_widget)
        self.central_widget.setLayout(self.layout)

        self.current_screen = 0
        self.stacked_widget.setCurrentIndex(self.current_screen)
        self.center_window()

    def center_window(self):
        # Get the screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()

        # Calculate the center point
        center_point = screen_geometry.center()

        # Calculate the new position for the main window
        new_x = center_point.x() - self.width() / 2
        new_y = center_point.y() - self.height() / 1.85

        # Set the new position
        self.move(int(new_x), int(new_y))

    def setup_welcome_screen(self):
        layout = QVBoxLayout()
        image = QLabel()
        image.setPixmap(self.icon.pixmap(128, 128))
        layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Welcome to the UniClean installer!\n"
                       "We'll help you trough this\n"
                       "super-easy-process of three steps!\n"
                       "To start, click Next.")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.next_screen)
        layout.addWidget(next_button)
        self.welcome_screen.setLayout(layout)

    def setup_path_selection_screen(self):
        layout = QVBoxLayout()
        label = QLabel("Select the target directory:")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        default_dir = os.path.join(os.environ['ProgramFiles'], app_name)
        self.selected_path = default_dir

        self.target_dir_label = QLabel(f"Target Directory: {default_dir}")
        select_target_button = QPushButton("Select Target")
        select_target_button.clicked.connect(self.select_target_directory)

        layout.addWidget(self.target_dir_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(select_target_button)

        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(self.previous_screen)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.next_screen)

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)

        layout.addLayout(button_layout)
        self.path_selection_screen.setLayout(layout)

    def select_target_directory(self):
        target_dir = QFileDialog.getExistingDirectory(self, "Select Target Directory")
        self.target_dir_label.setText(f"Target Directory: {target_dir}")
        self.selected_path = target_dir

    def setup_final_screen(self):
        layout = QVBoxLayout()
        label = QLabel("Installation Complete!")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        # Add the close button to close the installer
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.final_screen.setLayout(layout)

    def setup_summary_screen(self):
        layout = QVBoxLayout()
        label = QLabel(f"Will be installed in: {self.selected_path}\n\n"
                       "Are you sure you want to install ?")
        layout.addWidget(label)

        # Add summary information here

        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(self.previous_screen)
        next_button = QPushButton("Install")
        next_button.clicked.connect(self.next_screen)

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)

        layout.addLayout(button_layout)
        self.summary_screen.setLayout(layout)

    def cancel_installation(self):
        pass

    def setup_installation_screen(self):
        layout = QVBoxLayout()
        label = QLabel("Installation Progress:")
        layout.addWidget(label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        install_button = QPushButton("Cancel")
        install_button.clicked.connect(self.cancel_installation)
        layout.addWidget(install_button)

        self.installation_screen.setLayout(layout)

    def next_screen(self):
        self.current_screen += 1
        self.stacked_widget.setCurrentIndex(self.current_screen)
        if self.current_screen == 3:
            self.start_installation()

    def previous_screen(self):
        self.current_screen -= 1
        self.stacked_widget.setCurrentIndex(self.current_screen)

    def start_installation(self):
        self.install_thread = InstallationThread(self.selected_path)
        self.install_thread.update_progress.connect(self.update_progress)
        self.install_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        if progress == 100:
            self.install_thread.quit()
            self.current_screen = 4
            self.stacked_widget.setCurrentIndex(self.current_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallerUI(os.path.join(MAIN_EXECUTABLE_PATH, 'icon.ico'))
    window.show()
    sys.exit(app.exec())
