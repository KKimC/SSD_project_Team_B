class SsdShell:
    def __init__(self):
        pass

    def run(self):
        pass

    def make_command(self, command: str)->str:
        if command == "fullwrite 0xABCDFFFF":
            return 1
        pass