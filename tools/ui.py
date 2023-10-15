from functools import partial
from PyQt6.QtCore import Qt, QFileInfo
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QCheckBox, QPushButton, QVBoxLayout, QWidget, \
    QScrollArea, QGridLayout, QFileIconProvider


class UninstallerUI:
    def __init__(self, uninstaller):
        super().__init__()

        self.uninstall_button = None
        self.app = None
        self.uninstaller = uninstaller
        self.selected_paths = []
        self.selected_executables = []
        self.selected_registries = []
        self.selected_processes = []

    def close_ui(self):
        self.app.quit()

    def update_uninstall_state(self, item, checkbox, category):
        if category == "Path":
            if checkbox.isChecked():
                self.selected_paths.append(item)
            elif len(self.selected_paths) > 0:
                self.selected_paths.remove(item)
        elif category == "Executable":
            if checkbox.isChecked():
                self.selected_executables.append(item)
            elif len(self.selected_executables) > 0:
                self.selected_executables.remove(item)
        elif category == "Registry":
            if checkbox.isChecked():
                self.selected_registries.append(item)
            elif len(self.selected_registries) > 0:
                self.selected_registries.remove(item)
        elif category == "Process":
            if checkbox.isChecked():
                self.selected_processes.append(item)
            elif len(self.selected_processes) > 0:
                self.selected_processes.remove(item)
        print(self.selected_paths, self.selected_executables, self.selected_registries, self.selected_processes)
        if self.uninstall_button:
            self.uninstall_button.setEnabled(len(self.selected_paths) > 0 or
                                        len(self.selected_executables) > 0 or
                                        len(self.selected_registries) > 0 or
                                        len(self.selected_processes) > 0)

    def create_confirmation_ui(self):
        self.app = QApplication([])
        file_icon_provider = QFileIconProvider()  # Create an icon provider
        main_window = QMainWindow()
        main_window.setMinimumWidth(1280)
        main_window.setMinimumHeight(720)
        main_window.setWindowTitle("Uninstall Confirmation")

        central_widget = QWidget(main_window)
        main_layout = QVBoxLayout(central_widget)
        main_window.setCentralWidget(central_widget)

        (program_paths, uninstaller_exe, filtered_exe,
         executable_paths, registry_files, open_processes) = self.uninstaller.retrieve_information()

        selected_paths = []
        selected_executables = []
        selected_processes = []
        selected_registries = []
        checkboxes = []

        confirm_message = f"Uninstall program at '{self.uninstaller.path}'?\n\n"
        confirm_message += f"Detected Uninstaller: {uninstaller_exe}\n\n" if uninstaller_exe else ""
        confirm_message += f"Best matching executable file: {filtered_exe}\n\n" if filtered_exe else ""

        label = QLabel(confirm_message)
        label.setWordWrap(True)
        main_layout.addWidget(label)

        checkboxes_layout = QGridLayout()

        if program_paths:
            program_paths_label = QLabel("Program Paths")
            program_paths_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkboxes_layout.addWidget(program_paths_label, 0, 0)

            program_paths_scroll = QScrollArea()
            program_paths_scroll.setWidgetResizable(True)
            program_paths_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            program_paths_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

            program_paths_widget = QWidget()
            program_paths_layout = QVBoxLayout(program_paths_widget)

            for item in program_paths:
                checkbox = QCheckBox(item)
                checkbox.setChecked(True)
                self.update_uninstall_state(item, checkbox, "Path")
                checkboxes.append(checkbox)
                icon = QIcon(file_icon_provider.icon(QFileIconProvider.IconType.Folder))
                checkbox.setIcon(icon)  # Set the icon for the checkbox
                update_state = partial(self.update_uninstall_state, item, checkbox, "Path")
                checkbox.stateChanged.connect(update_state)
                program_paths_layout.addWidget(checkbox)

            program_paths_scroll.setWidget(program_paths_widget)
            checkboxes_layout.addWidget(program_paths_scroll, 1, 0)

        if executable_paths:
            executable_paths_label = QLabel("Executable Paths")
            executable_paths_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkboxes_layout.addWidget(executable_paths_label, 0, 1)

            executable_paths_scroll = QScrollArea()
            executable_paths_scroll.setWidgetResizable(True)
            executable_paths_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            executable_paths_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            executable_paths_widget = QWidget()
            executable_paths_layout = QVBoxLayout(executable_paths_widget)

            for item in executable_paths:
                checkbox = QCheckBox(item)
                checkbox.setChecked(True)
                self.update_uninstall_state(item, checkbox, "Executable")
                info = QFileInfo(item)
                icon = QIcon(file_icon_provider.icon(info))
                checkbox.setIcon(icon)  # Set the icon for the checkbox
                checkboxes.append(checkbox)
                update_state = partial(self.update_uninstall_state, item, checkbox, "Executable")
                checkbox.stateChanged.connect(update_state)
                executable_paths_layout.addWidget(checkbox)

            executable_paths_scroll.setWidget(executable_paths_widget)
            checkboxes_layout.addWidget(executable_paths_scroll, 1, 1)

        if registry_files:
            registry_files_label = QLabel("Registry Files")
            registry_files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkboxes_layout.addWidget(registry_files_label, 0, 2)

            registry_files_scroll = QScrollArea()
            registry_files_scroll.setWidgetResizable(True)
            registry_files_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            registry_files_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            registry_files_widget = QWidget()
            registry_files_layout = QVBoxLayout(registry_files_widget)

            for item in registry_files:
                checkbox = QCheckBox(item)
                checkbox.setChecked(True)
                self.update_uninstall_state(item, checkbox, "Registry")
                icon = QIcon(file_icon_provider.icon(QFileIconProvider.IconType.Folder))
                checkbox.setIcon(icon)  # Set the icon for the checkbox
                checkboxes.append(checkbox)
                update_state = partial(self.update_uninstall_state, item, checkbox, "Registry")
                checkbox.stateChanged.connect(update_state)
                registry_files_layout.addWidget(checkbox)

            registry_files_scroll.setWidget(registry_files_widget)
            checkboxes_layout.addWidget(registry_files_scroll, 1, 2)

        if open_processes:
            process_label = QLabel("Open Processes")
            process_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkboxes_layout.addWidget(process_label, 0, 3)

            open_processes_scroll = QScrollArea()
            open_processes_scroll.setWidgetResizable(True)
            open_processes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            open_processes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            open_processes_widget = QWidget()
            open_processes_layout = QVBoxLayout(open_processes_widget)

            for process in open_processes:
                item = (f"|- PID: {process.pid}\n"
                        f"|- {process.name()}")
                path = process.info['exe']
                checkbox = QCheckBox(item)
                checkbox.setChecked(True)
                self.update_uninstall_state(process, checkbox, "Process")
                info = QFileInfo(path)
                icon = QIcon(file_icon_provider.icon(info))
                checkbox.setIcon(icon)  # Set the icon for the checkbox
                checkboxes.append(checkbox)
                update_state = partial(self.update_uninstall_state, process, checkbox, "Process")
                checkbox.stateChanged.connect(update_state)
                open_processes_layout.addWidget(checkbox)

            open_processes_scroll.setWidget(open_processes_widget)
            checkboxes_layout.addWidget(open_processes_scroll, 1, 3)

        main_layout.addLayout(checkboxes_layout)

        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.setEnabled(False)
        uninstall_action = partial(self.uninstaller.uninstall, self.selected_paths, uninstaller_exe, filtered_exe,
                                   self.selected_executables, self.selected_registries, self.selected_processes)
        self.uninstall_button.clicked.connect(uninstall_action)
        main_layout.addWidget(self.uninstall_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_ui)
        main_layout.addWidget(cancel_button)

        self.update_uninstall_state(None, None, "None")

        main_window.show()
        self.app.exec()