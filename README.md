# Uni-Clean

{ICON}

An uninstaller tool built with PyQt6 to improve the uninstalling of programs and making it as easy as copy a file.
Adds a new context menu under the Right click in any folder.
This really does a clean uninstall. I think even better than the windows "Uninstall Program". Besides, it should work in every OS.

{IMAGES} 
{IMAGES} {IMAGES} 

## Features

- Program uninstallation with user interaction.
- Termination of related processes.
- Removal of registry entries.
- Deletion of program directories and files.
- Registry install and uninstall for the program itself.

## Prerequisites

To use this tool, you'll need:

- Python 3.6 or higher
- PyQt6
- A compatible operating system (Windows, macOS, or Linux)

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
   
    {INSTALLER IMAGES} {INSTALLER IMAGES} 

5. After the installer finishes, you can execute the program by two methods:
 - Run the script as a command:
 
   ```bash
   python uninstaller.py <program_path>

 - Or just right clicking any folder you want to remove or uninstall and selecting "Uninstall".

   {IMAGE SHOWING THE COMMAND}
