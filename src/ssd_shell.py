import re


class SsdShell:
    def __init__(self):
        pass

    def run(self):
        command = self.make_command()
        command_list = command.split()
        command_type = command_list[0]

        if command_type == "read":
            if self.is_invalid_read_command(command):
                return "INVALID COMMAND"

        if command_type == "write" and len(command_list) != 3:
            print("INVALID COMMAND")
            return

        if command_type == "fullwrite":
            if self.is_invalid_fullwrite_command(command):
                print("INVALID COMMAND")
                return
            else:
                # ssd.py fullwrite 0x12345678 호출부
                print("[Write] Done")
                return

    def make_command(self) -> str:
        command = input("Shell> ")
        return command

    def real_read(self):
        pass

    def real_full_read(self):
        for i in range(100):
            self.real_read()

    def real_write(self):
        pass

    def real_full_write(self):
        for i in range(100):
            self.real_write()

    def is_invalid_read_command(self, command: str):
        return True

    def is_invalid_fullwrite_command(self, command: str):
        return True

    def _is_valid_8char_hex(s):
        return bool(re.fullmatch(r"0x[0-9a-fA-F]{8}", s))
