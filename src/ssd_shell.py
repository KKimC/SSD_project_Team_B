class SsdShell:
    def __init__(self):
        pass

    def run(self):
        command = self.make_command()
        command_list = command.split()
        command_type = command_list[0]
        if command_type == "write" and len(command_list) != 3:
            print("INVALID COMMAND")
            return

        param1, param2 = command_list[1:]
        if int(param1) < 0 or int(param1) > 99:
            print("INVALID COMMAND")
            return
        print("[Write] Done")

    def make_command(self) -> str:
        command = input("Shell> ")
        return command
