class SsdShell:
    def __init__(self):
        pass

    def run(self):
        command = self.make_command()
        command_list = command.split()
        if command_list[0] == "write" and len(command_list) != 3:
            print("INVALID COMMAND")
            return
        print("[Write] Done")

    def make_command(self) -> str:
        command = input("Shell> ")
        return command
