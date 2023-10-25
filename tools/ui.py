import os
from functools import partial

import qdarktheme
from PyQt6.QtCore import Qt, QFileInfo
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
)


class UninstallerUI:
    def __init__(self, uninstaller, icon):
        super().__init__()

        self.uninstall_button_uninstaller = None
        self.main_window = None
        self.file_icon_provider = None
        self.uninstall_button = None
        self.app = None
        self.uninstaller = uninstaller
        self.selected_paths = []
        self.selected_executables = []
        self.selected_registries = []
        self.selected_processes = []
        self.icon = icon

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
        icon_label.setPixmap(icon.pixmap(64, 64))

        label_layout = QHBoxLayout()

        title_label = QLabel(title_text)
        label_layout.addWidget(title_label)
        label_layout.addWidget(icon_label)
        label = QLabel(label_text)
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

        # Calculate the center point
        center_point = screen_geometry.center()

        # Calculate the new position for the main window
        new_x = center_point.x() - self.main_window.width() / 2
        new_y = center_point.y() - self.main_window.height() / 1.85

        # Set the new position
        self.main_window.move(int(new_x), int(new_y))

    def create_confirmation_ui(self):
        self.app = QApplication([])
        self.file_icon_provider = QFileIconProvider()  # Create an icon provider
        main_window = QMainWindow()
        self.icon = QIcon(self.icon)
        qdarktheme.setup_theme("auto")
        self.main_window = main_window
        main_window.setWindowIcon(self.icon)
        main_window.setWindowTitle(f"Uninstall {self.uninstaller.folder_name}?")

        central_widget = QWidget(main_window)
        main_layout = QVBoxLayout(central_widget)
        main_window.setCentralWidget(central_widget)

        (
            program_paths,
            uninstaller_exe,
            filtered_exe,
            executable_paths,
            registry_files,
            open_processes,
        ) = self.uninstaller.retrieve_information()

        not_found = False

        # If all of the above is none, we should display that nothing was found, then, nothing can be done.
        # No buttons will be generated
        if (
            not executable_paths
            and not registry_files
            and not open_processes
            and not program_paths
        ):
            # Display a label showing there's nothing to do, and a button to exit
            main_layout.addWidget(
                QLabel("No files found"), alignment=Qt.AlignmentFlag.AlignCenter
            )
            self.uninstall_button = QPushButton("Exit")
            self.uninstall_button.clicked.connect(self.close_ui)
            main_layout.addWidget(self.uninstall_button)
            not_found = True
        else:
            main_window.setMinimumWidth(1280)
            main_window.setMinimumHeight(720)
            checkboxes = []

            if uninstaller_exe:
                main_layout.addWidget(
                    self.generate_label_with_icon(
                        uninstaller_exe, "Detected Uninstaller:", icon=uninstaller_exe
                    )
                )

            if filtered_exe and filtered_exe != uninstaller_exe:
                main_layout.addWidget(
                    self.generate_label_with_icon(
                        filtered_exe, "Main executable file:", icon=filtered_exe
                    )
                )

            checkboxes_layout = QGridLayout()

            if program_paths:
                program_paths_label = QLabel(f"Program Paths ({len(program_paths)})")
                program_paths_label.setToolTip("Select the dirs you want to remove.")
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
                        "Select the dir you want to remove from your computer."
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
                    f"Executable Paths ({len(executable_paths)})"
                )
                executable_paths_label.setToolTip(
                    "Select the executable files you want to terminate their "
                    "process to force a uninstall.\n"
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
                registry_files_label = QLabel(f"Registry Files ({len(registry_files)})")
                registry_files_label.setToolTip(
                    "Select the registry files you want to remove from your computer."
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
                        "Select the registry file you want to remove from your computer."
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
                process_label = QLabel(f"Open Processes ({len(open_processes)})")
                process_label.setToolTip(
                    "Select the open processes you want to terminate to be able to uninstall.\n"
                    "Warning: These are mandatory for the clean complete uninstall."
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
                        "Select the open process you want to terminate to be able to uninstall."
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

            main_layout.addLayout(checkboxes_layout)

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
                f"{self.uninstaller.folder_name} Info: \n\n"
                f"{self.uninstaller.folder_name} has {overall_info['dir_count']} directories.\n"
                f"{self.uninstaller.folder_name} has {overall_info['file_count']} files.\n"
                f"{self.uninstaller.folder_name} is using approximately: {program_size} {unit} ({total_space_used_percentage:.2f}% of disk)\n"
            )

            # Calculate the gain in storage in percentage
            initial_space = system_info["free_space_before"]
            space_after_uninstall = system_info["free_space_after"]
            storage_gain_percentage = (
                (space_after_uninstall - initial_space) / initial_space
            ) * 100

            system_info_label = QLabel(
                f"System Info: \n\n"
                f"Free Space Before Uninstall: {system_info['free_space_before_converted']} {system_info['free_space_before_unit']} \n"
                f"Will be removed from disk: {program_size} {unit}\n"
                f"Free Space After Uninstall: {system_info['free_space_after_converted']} {system_info['free_space_after_unit']} (+{storage_gain_percentage:.2f}%)\n"
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
            main_layout.addLayout(info_layout)

            if uninstaller_exe:
                self.uninstall_button_uninstaller = QPushButton(
                    "Program Uninstaller + Clean Uninstall (Recommended)"
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
                main_layout.addWidget(self.uninstall_button_uninstaller)

            self.uninstall_button = QPushButton(
                "Clean Uninstall"
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
            main_layout.addWidget(self.uninstall_button)

            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(self.close_ui)
            main_layout.addWidget(cancel_button)

            self.update_uninstall_state(None, None, "None")

        main_window.show()
        self.center_window()
        if not not_found:
            # Maximize the main window
            main_window.showMaximized()
        self.app.exec()
