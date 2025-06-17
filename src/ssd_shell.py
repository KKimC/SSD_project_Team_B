class SsdShell:
    def __init__(self):
        pass

    def run(self):
        pass

    def run_read(self, command: str):
        if self.is_invalid_read_command(command):
            return "INVALID COMMAND"

    def is_invalid_read_command(self, command: str):
        return True
