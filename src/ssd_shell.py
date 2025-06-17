class SsdShell:
    def __init__(self):
        pass

    def run(self):
        pass

    def make_command(self, command: str) -> str:
        tokens = command.strip().split()
        if tokens[0] == "fullwrite":
            return self.check_vailid_command(tokens[1])
        return "None"

    def check_vailid_command(self,  command: str):
        if command == "0xABCDFFFF":
            return "SUCCESS"
        elif command =="0xABCF":
            return "INVALID COMMAND"
        elif command =="ABCF33":
            return "INVALID COMMAND"