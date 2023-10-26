import os
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QComboBox, QCheckBox, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
class MySettingsWindow(QDialog):
    def __init__(self, ui):
        super().__init__()
        
        self.strings = ui.strings

        self.setWindowTitle(self.strings['MenuBar']['Settings'])
        
        self.ui = ui
        
        self.current_version = ui.uninstaller.current_version
        self.language_combobox = None
        self.fast_mode_checkbox = None

        self.create_settings_ui()
        
    def update_languages(self):
        # Path to the localization folder
        localization_dir = os.path.join(
            self.ui.program_dir, "localization"
        )  # Replace with the path to your localization folder
        
        files = os.listdir(localization_dir)
        available_languages = ["auto"]
        available_languages.extend([lang.replace(".json", "") for lang in files if lang.endswith(".json")])
        return available_languages

    def create_settings_ui(self):
        settings = self.ui.settings
        layout = QVBoxLayout()

        # Center-align the layout within the dialog
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label for selecting language
        lang_label = QLabel(f"{self.strings['Windows']['Settings']['SelectLanguage']}:")
        layout.addWidget(lang_label)

        # ComboBox for language selection
        self.language_combobox = QComboBox()
        languages = self.update_languages()
        self.language_combobox.addItems(languages)  # Add your languages
        self.language_combobox.setCurrentText(settings['Language'])
        layout.addWidget(self.language_combobox)
        
        # Add spacing between the buttons
        layout.addSpacing(35)
        
        # Label for selecting language
        theme_label = QLabel(f"{self.strings['Windows']['Settings']['SelectTheme']}:")
        layout.addWidget(theme_label)

        # ComboBox for language selection
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["auto", "Dark", "Light"])  # Add your languages
        self.theme_combobox.setCurrentText(settings['Theme'])
        layout.addWidget(self.theme_combobox)
        
        # Add spacing between the buttons
        layout.addSpacing(35)

        # Checkbox for enabling fast mode
        self.fast_mode_checkbox = QCheckBox(self.strings['Windows']['Settings']['EnableFastMode'])
        self.fast_mode_checkbox.setChecked(settings['FastMode'])
        layout.addWidget(self.fast_mode_checkbox)
        
        # Add spacing between the buttons
        layout.addSpacing(25)

        # Save button to apply changes
        save_button = QPushButton(self.strings['AppUI']['Buttons']['Save'])
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        settings = self.ui.settings
        settings["Language"] = self.language_combobox.currentText()
        settings["Theme"] = self.theme_combobox.currentText()
        settings["FastMode"] = self.fast_mode_checkbox.isChecked()
        self.ui.save_settings(settings)
        self.close()
