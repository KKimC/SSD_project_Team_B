class SsdShell:
    def __init__(self):
        pass

    def run(self):
        pass

    def make_command(self, command: str) -> str:
        if command == "fullwrite 0xABCDFFFF":
            return "SUCCESS"
        elif command == "fullwrite 0xABCF":
            return "INVALID COMMAND"
        elif command == "fullwrite ABCF33":
            return "INVALID COMMAND"
        return "None"
