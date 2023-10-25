from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QComboBox, QCheckBox, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
class MySettingsWindow(QDialog):
    def __init__(self, ui):
        super().__init__()
        
        self.strings = ui.strings

        self.setWindowTitle(self.strings['MenuBar']['Settings'])

        self.create_settings_ui()
        
        self.ui = ui
        
        self.current_version = ui.uninstaller.current_version

    def create_settings_ui(self):
        layout = QVBoxLayout()

        # Center-align the layout within the dialog
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label for selecting language
        lang_label = QLabel(self.strings['Windows']['Settings']['SelectLanguage'])
        layout.addWidget(lang_label)

        # ComboBox for language selection
        language_combobox = QComboBox()
        language_combobox.addItems(["English", "French", "Spanish"])  # Add your languages
        layout.addWidget(language_combobox)
        
        # Add spacing between the buttons
        layout.addSpacing(35)

        # Checkbox for enabling fast mode
        fast_mode_checkbox = QCheckBox(self.strings['Windows']['Settings']['EnableFastMode'])
        layout.addWidget(fast_mode_checkbox)
        
        # Add spacing between the buttons
        layout.addSpacing(25)

        # Save button to apply changes
        save_button = QPushButton(self.strings['AppUI']['Buttons']['Save'])
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        pass
        # Implement the logic to save the selected settings here
        # You can retrieve the selected language and fast mode checkbox state
        # and update your application settings accordingly
