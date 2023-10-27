import json
import locale
import os
from functools import partial

import qdarktheme as theme
from PyQt6.QtCore import Qt, QFileInfo, QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QCheckBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QGridLayout,
    QFileIconProvider,
    QHBoxLayout,
    QMenu,
    QTextEdit
)


class UninstallerUI:
    def __init__(self, uninstaller, program_dir):
        super().__init__()

        self.uninstall_button_uninstaller = None
        self.main_window = None
        self.file_icon_provider = None
        self.uninstall_button = None
        self.app = None
        self.settings = None
        self.strings = None
        self.uninstaller = uninstaller
        self.selected_paths = []
        self.selected_executables = []
        self.selected_registries = []
        self.selected_processes = []
        self.program_dir = program_dir
        self.icon = os.path.join(program_dir, "icon.ico")
        self.saved_height = None
        self.saved_width = None

    def load_strings(self):
        """
        Load strings from the localization folder based on the system language.

        :return: None
        """
        # Path to the localization folder
        localization_dir = os.path.join(
            self.program_dir, "localization"
        )  # Replace with the path to your localization folder

        print(self.settings["Language"])

        if self.settings["Language"] == "auto":
            # Get the default system language
            system_language = locale.getdefaultlocale()[0]
        else:
            system_language = self.settings["Language"]

        # Define the desired language code (fallback to "en" if not found)
        language = (
            system_language
            if os.path.exists(os.path.join(localization_dir, f"{system_language}.json"))
            else "en_US"
        )

        strings_file = os.path.join(localization_dir, f"{language}.json")

        strings = {}

        with open(strings_file, "r", encoding="utf-8") as file:
            strings = json.load(file)
        return strings

    def load_settings(self):
        """
        Load settings from the setting folder.

        :return: None
        """
        # Path to the setting folder
        setting_dir = os.path.join(
            self.program_dir, "settings"
        )  # Replace with the path to your setting folder
        strings_file = os.path.join(setting_dir, "settings.json")

        settings = {}

        try:
            with open(strings_file, "r", encoding="utf-8") as file:
                settings = json.load(file)
        except Exception as e:
            print(e)

        return settings

    def reopen(self):
        self.generate_UI()

    def save_settings(self, settings):
        """
        Save settings to the setting folder.

        :param settings: A dictionary containing the settings.
        :return: None
        """
        # Path to the setting folder
        setting_dir = os.path.join(
            self.program_dir, "settings"
        )  # Replace with the path to your setting folder
        settings_file = os.path.join(setting_dir, "settings.json")

        with open(settings_file, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)

        self.reopen()

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
        # print(self.selected_paths, self.selected_executables, self.selected_registries, self.selected_processes)
        if self.uninstall_button:
            self.uninstall_button.setEnabled(
                len(self.selected_paths) > 0
                or len(self.selected_executables) > 0
                or len(self.selected_registries) > 0
                or len(self.selected_processes) > 0
            )
        if self.uninstall_button_uninstaller:
            self.uninstall_button_uninstaller.setEnabled(
                len(self.selected_paths) > 0
                or len(self.selected_executables) > 0
                or len(self.selected_registries) > 0
                or len(self.selected_processes) > 0
            )

    def generate_label_with_icon(self, label_text, title_text, icon=None):
        if icon:
            info = QFileInfo(icon)
            icon = QIcon(self.file_icon_provider.icon(info).pixmap(32, 32))
        else:
            icon = QIcon(
                self.file_icon_provider.icon(QFileIconProvider.IconType.Folder).pixmap(
                    32, 32
                )
            )

        icon_label = QLabel()
        icon_label.setToolTip(label_text)
        icon_label.setPixmap(icon.pixmap(64, 64))

        label_layout = QHBoxLayout()

        title_label = QLabel(title_text)
        label_layout.addWidget(title_label)
        label_layout.addWidget(icon_label)
        label = QLabel(os.path.basename(label_text))
        label.setToolTip(label_text)
        label_layout.addWidget(label)
        label_layout.addStretch()
        label_layout.addSpacing(5)

        # Create a container widget for the label_layout
        label_container = QWidget()
        label_container.setLayout(label_layout)
        return label_container

    def center_window(self):
        # Get the screen geometry
        screen_geometry = self.app.primaryScreen().geometry()
        print(screen_geometry)

        # Calculate the center point of the screen
        center_x = screen_geometry.center().x()
        center_y = screen_geometry.center().y()
        print(center_x, center_y)

        # Calculate the new position for the main window
        new_x = center_x - self.main_window.width() / 2
        new_y = center_y - self.main_window.height() / 2
        print(new_x, new_y)

        # Set the new position
        self.main_window.move(int(new_x), int(new_y))


    def create_menu_bar(self):
        menuBar = self.main_window.menuBar()  # No need for self.main_window.menuBar()

        menuBar.clear()

        fileMenu = QMenu(self.strings["MenuBar"]["File"], self.main_window)
        fileMenu.addAction(
            self.strings["MenuBar"]["Settings"], self.open_settings_window
        )
        fileMenu.addAction(self.strings["MenuBar"]["Exit"], self.close_ui)

        helpMenu = QMenu(self.strings["MenuBar"]["Help"], self.main_window)
        helpMenu.addAction(self.strings["MenuBar"]["About"], self.open_about_window)

        menuBar.addMenu(fileMenu)
        menuBar.addMenu(helpMenu)

    def close_ui(self):
        self.main_window.close()

    def open_about_window(self):
        settings_window = self.uninstaller.about_window
        settings_window.exec()

    def open_settings_window(self):
        settings_window = self.uninstaller.settings_window
        settings_window.exec()

    def is_fast_mode(
        self,
        program_paths,
        uninstaller_exe,
        filtered_exe,
        executable_paths,
        registry_files,
        open_processes,
    ):
        if self.settings["FastMode"]:
            # Create a dialog box to show what will be removed
            self.main_window.setWindowTitle(self.strings["AppUI"]["FastModeEnabled"])

            # Create a label to display the list of items to be removed
            removal_list_label = QLabel(self.strings["AppUI"]["FastModeToBeRemoved"])
            removal_list_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Create a list to hold the items to be removed
            removal_list = []

            if program_paths:
                removal_list.append(
                    f"{self.strings['AppUI']['Checkboxes']['Programs']['LabelText']} ({len(program_paths)}):"
                )
                removal_list.extend(program_paths)

            if uninstaller_exe:
                removal_list.append(f"{self.strings['AppUI']['Uninstaller']}:")
                removal_list.append(uninstaller_exe)

            if filtered_exe and filtered_exe != uninstaller_exe:
                removal_list.append(f"{self.strings['AppUI']['MainExe']}:")
                removal_list.append(filtered_exe)

            if executable_paths:
                removal_list.append(
                    f"{self.strings['AppUI']['Checkboxes']['Executables']['LabelText']} ({len(executable_paths)}):"
                )
                removal_list.extend(executable_paths)

            if registry_files:
                removal_list.append(
                    f"{self.strings['AppUI']['Checkboxes']['Registry']['LabelText']} ({len(registry_files)}):"
                )
                removal_list.extend(registry_files)

            if open_processes:
                removal_list.append(
                    f"{self.strings['AppUI']['Checkboxes']['Processes']['LabelText']} ({len(open_processes)}):"
                )
                for process in open_processes:
                    removal_list.append(f"- PID: {process.pid} | {process.name()}")

            # Create a QTextEdit widget to display the removal list
            removal_list_textedit = QTextEdit()
            removal_list_textedit.setReadOnly(True)
            removal_list_textedit.setPlainText("\n".join(removal_list))
            removal_list_textedit.setMinimumHeight(200)

            # Create a "Continue" button
            continue_button = QPushButton(self.strings["AppUI"]["Buttons"]["Continue"])
            # continue_button.clicked.connect(fast_mode_dialog.accept)

            # Create a "Cancel" button
            cancel_button = QPushButton(self.strings["AppUI"]["Buttons"]["Cancel"])
            # cancel_button.clicked.connect(fast_mode_dialog.reject)

            # Create a layout for the dialog box
            dialog_layout = QVBoxLayout()
            dialog_layout.addWidget(removal_list_label)
            dialog_layout.addWidget(removal_list_textedit)
            button_layout = QHBoxLayout()
            button_layout.addWidget(continue_button)
            button_layout.addWidget(cancel_button)
            dialog_layout.addLayout(button_layout)

            self.main_layout.addLayout(dialog_layout)

            return True
        return False

    def generate_UI(self):
        self.settings = self.load_settings()
        self.strings = self.load_strings()

        self.uninstall_button = None
        self.uninstall_button_uninstaller = None

        central_widget = QWidget(self.main_window)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_window.setCentralWidget(central_widget)
        self.create_menu_bar()
        theme.setup_theme(self.settings["Theme"].lower())

        (
            program_paths,
            uninstaller_exe,
            filtered_exe,
            executable_paths,
            registry_files,
            open_processes,
        ) = self.uninstaller.retrieve_information()

        # If all of the above is none, we should display that nothing was found, then, nothing can be done.
        # No buttons will be generated
        if (
            not executable_paths
            and not registry_files
            and not open_processes
            and not program_paths
        ):
            # Display a label showing there's nothing to do, and a button to exit
            self.main_layout.addWidget(
                QLabel(self.strings["AppUI"]["InvalidDirectory"]),
                alignment=Qt.AlignmentFlag.AlignCenter,
            )
            self.uninstall_button = QPushButton(self.strings["MenuBar"]["Exit"])
            self.uninstall_button.clicked.connect(self.close_ui)
            self.main_layout.addWidget(self.uninstall_button)
            self.main_window.adjustSize()
        else:
            is_fast_mode = self.is_fast_mode(
                program_paths,
                uninstaller_exe,
                filtered_exe,
                executable_paths,
                registry_files,
                open_processes,
            )

            if is_fast_mode:
                self.update_window_size(0)
                return

            checkboxes = []
            self.selected_paths = []
            self.selected_executables = []
            self.selected_registries = []
            self.selected_processes = []

            self.main_window.setWindowTitle(
                f"{self.strings['AppUI']['Uninstall']} {self.uninstaller.folder_name}?"
            )

            if uninstaller_exe:
                self.main_layout.addWidget(
                    self.generate_label_with_icon(
                        uninstaller_exe,
                        f"{self.strings['AppUI']['DetectedUninstaller']}:",
                        icon=uninstaller_exe,
                    ),
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )

            if filtered_exe and filtered_exe != uninstaller_exe:
                self.main_layout.addWidget(
                    self.generate_label_with_icon(
                        filtered_exe,
                        f"{self.strings['AppUI']['MainExe']}:",
                        icon=filtered_exe,
                    ),
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )

            checkboxes_layout = QGridLayout()
            checkboxes_layout.setRowMinimumHeight(1, 200)

            if program_paths:
                program_paths_label = QLabel(
                    f"{self.strings['AppUI']['Checkboxes']['Programs']['LabelText']} ({len(program_paths)})"
                )
                program_paths_label.setToolTip(
                    self.strings["AppUI"]["Checkboxes"]["Programs"]["LabelTooltip"]
                )
                program_paths_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkboxes_layout.addWidget(program_paths_label, 0, 0)

                program_paths_scroll = QScrollArea()
                program_paths_scroll.setWidgetResizable(True)
                program_paths_scroll.setVerticalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )
                program_paths_scroll.setHorizontalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )

                program_paths_widget = QWidget()
                program_paths_layout = QVBoxLayout(program_paths_widget)

                for item in program_paths:
                    checkbox = QCheckBox(item)
                    checkbox.setChecked(True)
                    self.update_uninstall_state(item, checkbox, "Path")
                    checkboxes.append(checkbox)

                    # Check if the item is a folder or a file
                    if os.path.isdir(item):
                        icon = QIcon(
                            self.file_icon_provider.icon(
                                QFileIconProvider.IconType.Folder
                            ).pixmap(32, 32)
                        )
                    else:
                        info = QFileInfo(item)
                        icon = QIcon(self.file_icon_provider.icon(info).pixmap(32, 32))

                    checkbox.setIcon(icon)  # Set the icon for the checkbox
                    checkbox.setToolTip(
                        self.strings["AppUI"]["Checkboxes"]["Programs"][
                            "CheckBoxTooltip"
                        ]
                    )
                    update_state = partial(
                        self.update_uninstall_state, item, checkbox, "Path"
                    )
                    checkbox.stateChanged.connect(update_state)
                    program_paths_layout.addSpacing(10)
                    program_paths_layout.addWidget(checkbox)

                program_paths_scroll.setWidget(program_paths_widget)
                checkboxes_layout.addWidget(program_paths_scroll, 1, 0)

            if executable_paths:
                executable_paths_label = QLabel(
                    f"{self.strings['AppUI']['Checkboxes']['Executables']['LabelText']} ({len(executable_paths)})"
                )
                executable_paths_label.setToolTip(
                    self.strings["AppUI"]["Checkboxes"]["Executables"]["LabelTooltip"]
                )
                executable_paths_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkboxes_layout.addWidget(executable_paths_label, 0, 1)

                executable_paths_scroll = QScrollArea()
                executable_paths_scroll.setWidgetResizable(True)
                executable_paths_scroll.setVerticalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )
                executable_paths_scroll.setHorizontalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )

                executable_paths_widget = QWidget()
                executable_paths_layout = QVBoxLayout(executable_paths_widget)

                for item in executable_paths:
                    checkbox = QCheckBox(os.path.basename(item))
                    checkbox.setChecked(True)
                    self.update_uninstall_state(item, checkbox, "Executable")
                    info = QFileInfo(item)
                    icon = QIcon(self.file_icon_provider.icon(info).pixmap(32, 32))
                    checkbox.setIcon(icon)  # Set the icon for the checkbox
                    checkbox.setToolTip(item)
                    checkboxes.append(checkbox)
                    update_state = partial(
                        self.update_uninstall_state, item, checkbox, "Executable"
                    )
                    checkbox.stateChanged.connect(update_state)
                    executable_paths_layout.addSpacing(10)
                    executable_paths_layout.addWidget(checkbox)

                executable_paths_scroll.setWidget(executable_paths_widget)
                checkboxes_layout.addWidget(executable_paths_scroll, 1, 1)

            if registry_files:
                registry_files_label = QLabel(
                    f"{self.strings['AppUI']['Checkboxes']['Registry']['LabelText']} ({len(registry_files)})"
                )
                registry_files_label.setToolTip(
                    self.strings["AppUI"]["Checkboxes"]["Registry"]["LabelTooltip"]
                )
                registry_files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkboxes_layout.addWidget(registry_files_label, 0, 2)

                registry_files_scroll = QScrollArea()
                registry_files_scroll.setWidgetResizable(True)
                registry_files_scroll.setVerticalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )
                registry_files_scroll.setHorizontalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )

                registry_files_widget = QWidget()
                registry_files_layout = QVBoxLayout(registry_files_widget)

                for item in registry_files:
                    checkbox = QCheckBox(item)
                    checkbox.setChecked(True)
                    self.update_uninstall_state(item, checkbox, "Registry")
                    icon = QIcon(
                        self.file_icon_provider.icon(
                            QFileIconProvider.IconType.Folder
                        ).pixmap(32, 32)
                    )
                    checkbox.setIcon(icon)  # Set the icon for the checkbox
                    checkbox.setToolTip(
                        self.strings["AppUI"]["Checkboxes"]["Registry"][
                            "CheckBoxTooltip"
                        ]
                    )
                    checkboxes.append(checkbox)
                    update_state = partial(
                        self.update_uninstall_state, item, checkbox, "Registry"
                    )
                    checkbox.stateChanged.connect(update_state)
                    registry_files_layout.addSpacing(10)
                    registry_files_layout.addWidget(checkbox)

                registry_files_scroll.setWidget(registry_files_widget)
                checkboxes_layout.addWidget(registry_files_scroll, 1, 2)

            if open_processes:
                process_label = QLabel(
                    f"{self.strings['AppUI']['Checkboxes']['Processes']['LabelText']} ({len(open_processes)})"
                )
                process_label.setToolTip(
                    self.strings["AppUI"]["Checkboxes"]["Processes"]["LabelTooltip"]
                )
                process_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkboxes_layout.addWidget(process_label, 0, 3)

                open_processes_scroll = QScrollArea()
                open_processes_scroll.setWidgetResizable(True)
                open_processes_scroll.setVerticalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )
                open_processes_scroll.setHorizontalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )

                open_processes_widget = QWidget()
                open_processes_layout = QVBoxLayout(open_processes_widget)

                for process in open_processes:
                    item = f"|- PID: {process.pid}\n" f"|- {process.name()}"
                    path = process.info["exe"]
                    checkbox = QCheckBox(item)
                    checkbox.setChecked(True)
                    self.update_uninstall_state(process, checkbox, "Process")
                    info = QFileInfo(path)
                    icon = QIcon(self.file_icon_provider.icon(info).pixmap(32, 32))
                    checkbox.setIcon(icon)  # Set the icon for the checkbox
                    checkbox.setToolTip(
                        self.strings["AppUI"]["Checkboxes"]["Processes"][
                            "CheckBoxTooltip"
                        ]
                    )
                    checkboxes.append(checkbox)
                    update_state = partial(
                        self.update_uninstall_state, process, checkbox, "Process"
                    )
                    checkbox.stateChanged.connect(update_state)
                    open_processes_layout.addSpacing(10)
                    open_processes_layout.addWidget(checkbox)

                open_processes_scroll.setWidget(open_processes_widget)
                checkboxes_layout.addWidget(open_processes_scroll, 1, 3)

            self.main_layout.addLayout(checkboxes_layout)
            
            

            overall_info = self.uninstaller.files.get_directory_info(program_paths)
            system_info = self.uninstaller.files.get_system_overall_info(
                overall_info["size"]["total_size"]
            )

            # Add precision to the total size. Only two decimals after the comma
            program_size = overall_info["size"]["total_size_converted"]
            unit = overall_info["size"]["unit"]

            # Calculate the percentage of total space used by the program
            total_space_used_percentage = (
                overall_info["size"]["total_size"] / system_info["free_space_before"]
            ) * 100

            overall_info_label = QLabel(
                f"{self.uninstaller.folder_name} {self.strings['AppUI']['Info']['ProgramInfo']['Info']}: \n\n"
                f"{self.uninstaller.folder_name} {self.strings['AppUI']['Info']['ProgramInfo']['Has']} {overall_info['dir_count']} {self.strings['AppUI']['Info']['ProgramInfo']['Directories']}.\n"
                f"{self.uninstaller.folder_name} {self.strings['AppUI']['Info']['ProgramInfo']['Has']} {overall_info['file_count']} {self.strings['AppUI']['Info']['ProgramInfo']['Files']}.\n"
                f"{self.uninstaller.folder_name} {self.strings['AppUI']['Info']['ProgramInfo']['Using']}: {program_size} {unit} ({total_space_used_percentage:.2f}% {self.strings['AppUI']['Info']['ProgramInfo']['OfDisk']})\n"
            )

            # Calculate the gain in storage in percentage
            initial_space = system_info["free_space_before"]
            space_after_uninstall = system_info["free_space_after"]
            storage_gain_percentage = (
                (space_after_uninstall - initial_space) / initial_space
            ) * 100

            system_info_label = QLabel(
                f"{self.strings['AppUI']['Info']['SystemInfo']['Info']}: \n\n"
                f"{self.strings['AppUI']['Info']['SystemInfo']['FreeSpace']}: {system_info['free_space_before_converted']} {system_info['free_space_before_unit']} \n"
                f"{self.strings['AppUI']['Info']['SystemInfo']['WillBeRemoved']}: {program_size} {unit}\n"
                f"{self.strings['AppUI']['Info']['SystemInfo']['FreeSpaceAfter']}: {system_info['free_space_after_converted']} {system_info['free_space_after_unit']} (+{storage_gain_percentage:.2f}%)\n"
            )

            # Create a horizontal layout
            info_layout = QHBoxLayout()

            # Add the program info label on the left
            info_layout.addWidget(overall_info_label)

            # Add a stretchable space in between to separate the labels
            info_layout.addStretch(1)

            # Add the system info label on the right
            info_layout.addWidget(system_info_label)

            # Add the horizontal layout to the main layout
            self.main_layout.addLayout(info_layout)

            if uninstaller_exe:
                self.uninstall_button_uninstaller = QPushButton(
                    self.strings["AppUI"]["Buttons"]["WithUninstaller"]
                )
                self.uninstall_button_uninstaller.setEnabled(False)
                uninstall_action = partial(
                    self.uninstaller.uninstall,
                    self.selected_paths,
                    uninstaller_exe,
                    self.selected_executables,
                    self.selected_registries,
                    self.selected_processes,
                )
                self.uninstall_button_uninstaller.clicked.connect(uninstall_action)
                self.main_layout.addWidget(self.uninstall_button_uninstaller)

            self.uninstall_button = QPushButton(
                self.strings["AppUI"]["Buttons"]["WithoutUninstaller"]
            )
            self.uninstall_button.setEnabled(False)
            uninstall_action = partial(
                self.uninstaller.uninstall,
                self.selected_paths,
                None,
                self.selected_executables,
                self.selected_registries,
                self.selected_processes,
            )
            self.uninstall_button.clicked.connect(uninstall_action)
            self.main_layout.addWidget(self.uninstall_button)

            cancel_button = QPushButton(self.strings["AppUI"]["Buttons"]["Cancel"])
            cancel_button.clicked.connect(self.close_ui)
            self.main_layout.addWidget(cancel_button)

            self.update_uninstall_state(None, None, "None")
            
            self.update_window_size(checkboxes_layout.count())
            
            
            # Ensure that the window is resized to fit its contents
            #self.main_window.adjustSize()
            
    def update_window_size(self, count):
        max_count = 8  # Count where it maximizes
        
        self.main_window.adjustSize()
    
        if count == max_count: 
            self.main_window.showMaximized()
        else:
            self.main_window.show()
            QCoreApplication.processEvents()  # Process pending events
            self.center_window()
        
        
        



    def create_confirmation_ui(self):
        self.settings = self.load_settings()
        self.strings = self.load_strings()
        self.app = QApplication([])
        self.file_icon_provider = QFileIconProvider()  # Create an icon provider
        self.uninstaller.init_windows()
        self.main_window = QMainWindow()
        self.icon = QIcon(self.icon)
        self.main_window.setWindowIcon(self.icon)

        self.generate_UI()
        self.app.exec()
