# Uni-Clean
<img src="https://github.com/pedrohusky/clean-uninstaller/assets/59580251/62787b56-8704-4a6e-a466-3a4e1145e05b" width="200" height="200">

An uninstaller tool built with PyQt6 to improve the uninstalling of programs and making it as easy as copy a file.
Adds a new context menu under the Right click in any folder.
This really does a clean uninstall. I think even better than the windows "Uninstall Program". Currently, it works on windows. WIP other platforms.


<img src="https://github.com/pedrohusky/clean-uninstaller/assets/59580251/7cad706d-6711-4735-84df-40a3d44726df" width="500" height="300">
<img src="https://github.com/pedrohusky/clean-uninstaller/assets/59580251/5042adad-f717-44d6-b41f-256118130bd9" width="400" height="200">

## Features

- Program uninstallation with user interaction.
- Termination of related processes.
- Removal of registry entries.
- Deletion of program directories and files.
- Registry install and uninstall for the program itself.
![Captura de tela 2023-10-17 154549](https://github.com/pedrohusky/clean-uninstaller/assets/59580251/8742ef83-e6dc-4670-84f8-38333e71e179)


## Prerequisites

To use this tool, you'll need:
- To download the installer from the releases OR editting yourself the code to match anything you like.
 ```
  Only if you want to modify the code!!
  - Python 3.6 or higher
  - PyQt6
  - A compatible operating system (Windows, macOS, or Linux)
 ```

## Usage

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/uninstaller-pyqt6.git

2. Navigate to the repository directory:
   
   ```bash
   cd uninstaller-pyqt6

3. Install requirements (OPTIONAL: ONLY IF YOU WANT TO MODIFY THE EXE):

   ```bash
   pip install requirements.txt
   
4. Open the installer file under the 'dist' folder. There is three exes because two of them will be packed into one if you modify the code itself.
 - To modify the code, you can re-generate those .exes just by running the generate.py withouy any arguments. Ex: python generate.py
 - It will recreate or update the exes inside the dist folder. Three exes are crated: installer, program and uninstaller.
 - Program and uninstaller are packed inside the installer itself that will help handle all the super-easy-three-steps install.

5. After the installer finishes, you can execute the program this way:
 - By just right clicking any folder you want to remove or uninstall and selecting "Uninstall".

   <img src="https://github.com/pedrohusky/clean-uninstaller/assets/59580251/5042adad-f717-44d6-b41f-256118130bd9" width="800" height="400">
