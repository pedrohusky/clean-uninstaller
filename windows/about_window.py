import subprocess
import tempfile
import requests
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtCore import Qt
import webbrowser


class MyAboutWindow(QDialog):
    def __init__(self, ui):
        super().__init__()

        self.strings = ui.strings

        self.setWindowTitle(self.strings["MenuBar"]["About"])

        self.create_about_ui()

        self.ui = ui

        self.current_version = ui.uninstaller.current_version

    def create_about_ui(self):
        layout = QVBoxLayout()

        # Center-align the layout within the dialog
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label for GitHub link
        github_label = QLabel(
            "<a href='https://github.com/pedrohusky/clean-uninstaller'>GitHub Repository</a>",
            self,
        )
        github_label.setOpenExternalLinks(True)
        layout.addWidget(github_label)

        # Add spacing between the buttons
        layout.addSpacing(25)

        # Label for displaying the current version
        version_label = QLabel(
            f"{self.strings['Windows']['About']['CurrentVersion']}: {self.current_version}", self
        )  # Replace with your app's version
        layout.addWidget(version_label)

        # Add spacing between the buttons
        layout.addSpacing(25)

        # Label for displaying the creator
        creator_label = QLabel(
            f"{self.strings['Windows']['About']['CurrentVersion']}: Pedro Ganzo", self
        )
        layout.addWidget(creator_label)

        # Add spacing between the buttons
        layout.addSpacing(25)

        # Button to open the releases page
        update_button = QPushButton(self.strings["AppUI"]["Buttons"]["Update"], self)
        update_button.clicked.connect(self.open_releases_page)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def open_releases_page(self):
        try:
            releases_url = (
                "https://api.github.com/repos/pedrohusky/clean-uninstaller/releases"
            )
            response = requests.get(releases_url)
            response.raise_for_status()

            releases = response.json()

            if releases:
                first_release = releases[0]
                assets = first_release.get("assets")

                if assets:
                    # Find the first asset with the .exe extension
                    exe_asset = next(
                        (asset for asset in assets if asset["name"].endswith(".exe")),
                        None,
                    )
                    
                    released_version = float(first_release["tag_name"].replace("v", ""))

                    if exe_asset:
                        if self.current_version < released_version:
                            # Are you sure messagebox
                            messagebox = QMessageBox()
                            messagebox.setWindowIcon(self.ui.icon)
                            messagebox.setWindowTitle(
                                f'{self.strings["Windows"]["About"]["NewVersion"]} {first_release["tag_name"]}'
                            )
                            messagebox.setText(
                                f'{self.strings["Windows"]["About"]["NewVersion"]}, download it?'
                            )
                            messagebox.addButton(
                                QMessageBox.StandardButton.Yes
                            )
                            messagebox.setDefaultButton(QMessageBox.StandardButton.No)
                            messagebox.setIcon(QMessageBox.Icon.Information)
                            result = messagebox.exec()
                            
                            if result == 65536 or not result:
                                return
                            else:
                                # Open the URL of the .exe file
                                webbrowser.open(exe_asset["browser_download_url"])
                        else:
                            # Are you sure messagebox
                            messagebox = QMessageBox()
                            messagebox.setWindowIcon(self.ui.icon)
                            messagebox.setWindowTitle(
                                self.strings["Windows"]["About"]["UpToDate"]
                            )
                            messagebox.setText(
                                self.strings["Windows"]["About"]["NoNewVersion"]
                            )
                            messagebox.setDefaultButton(QMessageBox.StandardButton.Ok)
                            messagebox.setIcon(QMessageBox.Icon.Information)
                            messagebox.exec()

                        return

                        # Download the .exe file into a temporary location
                        response = requests.get(exe_asset["browser_download_url"])

                        if response.status_code == 200:
                            with tempfile.NamedTemporaryFile(
                                delete=False, suffix=".exe"
                            ) as temp_file:
                                temp_filename = temp_file.name
                                temp_file.write(response.content)

                            # Run the .exe file from the temporary location
                            subprocess.Popen([temp_filename])

                            # Close the current application
                            self.close()
                    else:
                        print("No .exe file found in the release assets.")
                else:
                    print("No assets found in the first release.")
            else:
                print("No releases found for the repository.")
        except Exception as e:
            print("An error occurred:", e)

    def open_about_link(self):
        # Implement the logic to open a link in your default web browser
        webbrowser.open("https://github.com/pedrohusky/clean-uninstaller")
