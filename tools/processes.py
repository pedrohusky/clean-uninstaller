import psutil


class Processes:
    def __init__(self):
        self.processes_to_terminate = []

    def find_processes_to_terminate(self, executable_paths, read_only=False, processes_to_terminate=None):
        if processes_to_terminate:
            self.processes_to_terminate.extend(processes_to_terminate)
            skip = True
        else:
            skip = False

        if not skip:
            # Locate and add processes to the list of processes to terminate
            for process in psutil.process_iter(attrs=['pid', 'exe']):
                try:
                    process_exe = process.info['exe']
                    # Check if the process executable is one of the executables in executable_paths
                    for path in executable_paths:
                        if process_exe == path:
                            self.processes_to_terminate.append(process)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

        if read_only:
            return self.processes_to_terminate
        else:
            self._terminate_processes()

    def _terminate_processes(self):
        # Terminate processes
        for process in self.processes_to_terminate:
            try:
                process.terminate()
            except Exception as e:
                print(f"Error terminating process: {str(e)}")
