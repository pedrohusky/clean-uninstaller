import ctypes
import os
import subprocess
import winreg


class Registry:
    def __init__(self, uninstaller):
        self.uninstaller = uninstaller
        self.hkey_names = {
            winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
            winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
            winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
            winreg.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG",
            winreg.HKEY_USERS: "HKEY_USERS"
        }
        self.registry_key_constants = {
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
            "HKEY_USERS": winreg.HKEY_USERS,
        }
        self.registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, "Software"),
            (winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services"),
            (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"),
            (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"),
            (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce"),
            (winreg.HKEY_CURRENT_USER, "Software"),
            (winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"),
            (winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce"),
            (winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
        ]

    def edit_context_menu_item(self, name, command):
        try:
            # Backup the registry before making changes
            self.backup_registry()

            key_name = "*\\shell\\pintohomefile"

            # Open the existing key for writing
            command_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_name, 0, winreg.KEY_WRITE)

            # Set the "MUIVerb" value to the new name
            winreg.SetValueEx(command_key, "MUIVerb", 0, winreg.REG_SZ, name)

            # Open the command subkey for writing
            command_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_name + "\\command", 0, winreg.KEY_WRITE)

            # Set the default value to the new command
            winreg.SetValue(command_key, '', winreg.REG_SZ, command)

            # Close the registry keys
            winreg.CloseKey(command_key)

            print(f"Modified '{name}' in the context menu.")
        except Exception as e:
            print(f"Error while editing the context menu item: {e}")

    @staticmethod
    def backup_registry():
        key_path = r"HKCR\*\shell\pintohomefile"
        backup_path = os.path.join(os.environ['ProgramFiles'], 'Desinstalar Tudo', 'registry_backup.reg')
        try:
            export_command = f'reg export "{key_path}" "{backup_path}"'
            print(export_command)
            subprocess.run(export_command, shell=True, check=True)

            print(f"Registry key backup saved to: {backup_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error while backing up the registry key: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _delete_key(self, key, sub_key_name: str):
        with winreg.OpenKey(key, sub_key_name, 0, winreg.KEY_ALL_ACCESS) as sub_key:
            while True:
                try:
                    try:
                        sub_sub_key_name = winreg.EnumKey(sub_key, 0)
                        self._delete_key(sub_key, sub_sub_key_name)
                    except OSError:
                        sub_sub_key_name = winreg.EnumKey(sub_key, 1)
                        self._delete_key(sub_key, sub_sub_key_name)
                except OSError:
                    break

        winreg.DeleteKey(key, sub_key_name)

    def delete_sub_key(self, root, sub_keys, should_delete=False):
        registry_keys = []
        for sub in sub_keys:
            try:
                open_key = winreg.OpenKey(root, sub, 0, winreg.KEY_ALL_ACCESS)
                print(f"Opened registry key: {self.hkey_names[root]}\\{sub}")

                num, _, _ = winreg.QueryInfoKey(open_key)
                print(f"Found {num} sub_keys under {self.hkey_names[root]}\\{sub}")

                for _ in range(num):
                    child = winreg.EnumKey(open_key, 0)

                    if should_delete:
                        print(f"Deleting registry key: {self.hkey_names[root]}\\{sub}\\{child}")
                        self._delete_key(open_key, child)

                    registry_keys.append(f"{self.hkey_names[root]}\\{sub}\\{child}")

                try:
                    if should_delete:
                        print(f"Deleted registry key: {self.hkey_names[root]}\\{sub}")
                        winreg.DeleteKey(open_key, '')

                    registry_keys.append(f"{self.hkey_names[root]}\\{sub}")
                except WindowsError:
                    continue
                finally:
                    winreg.CloseKey(open_key)
            except WindowsError:
                continue
        return registry_keys

    def split_registry_path(self, registry_path):
        # Split the registry path into root key and subkey
        parts = registry_path.split('\\', 1)
        if len(parts) == 2:
            root_key, subkey = parts
            return self.registry_key_constants[root_key], subkey
        return None, None

    # log opening/closure failure

    def find_and_remove_registry_entries(self, read_only=False, registry_files=None):

        try:
            # Common registry locations to search

            registry_keys = []

            if registry_files:
                # Split registry_paths based on the number of backslashes and sort by the number of splits
                registry_files_sorted = sorted(registry_files, key=lambda path: path.count('\\'), reverse=True)

                for registry_path in registry_files_sorted:
                    # Split the registry path into root key and subkey
                    root_key, subkey = self.split_registry_path(registry_path)
                    if root_key and subkey:
                        print(f"Searching for registry keys: {self.hkey_names[root_key]}\\{subkey}")
                        registry_keys.extend(self.delete_sub_key(root_key, [subkey], should_delete=True))

            else:
                for root in self.registry_paths:
                    sub_keys_set = set()
                    sub_keys_set.add(root[1] + f"\\{self.uninstaller.folder_name}")
                    sub_keys_set.add(root[1] + f"\\{self.uninstaller.folder_name.replace(' ', '')}")
                    sub_keys_set.add(root[1] + f"\\{self.uninstaller.program_name}")
                    sub_keys_set.add(root[1] + f"\\{self.uninstaller.program_name.replace(' ', '')}")

                    # Convert the set back to a list
                    sub_keys = list(sub_keys_set)
                    print(f"Searching for registry keys: {sub_keys}")
                    registry_keys.extend(self.delete_sub_key(root[0], sub_keys, should_delete=not read_only))

            if read_only:
                return registry_keys

            print(f"Deleted registry keys: {registry_keys}")
        except Exception as e:
            print(f"Error in removing registry entries: {str(e)}")
