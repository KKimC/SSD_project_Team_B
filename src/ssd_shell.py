import re

INVALID_COMMAND = "INVALID COMMAND"

class SsdShell:
    def __init__(self):
        pass

    def run(self):
        command = self.make_command()
        command_list = command.split()
        if not command_list:
            print(INVALID_COMMAND)
            return

        command_type = command_list[0]

        if command_type not in ["read", "write", "fullwrite", "fullread"]:
            print(INVALID_COMMAND)
            return
          
        if command_type == "fullwrite":
            if self.is_invalid_fullwrite_command(command):
                print("INVALID COMMAND")
                return
            else:
                # ssd.py fullwrite 0x12345678 호출부
                print("[Write] Done")
                return

        if command_type == "read":
            if self.is_invalid_read_command(command_list):
                print(INVALID_COMMAND)
                return
              
        elif command_type == "write":
            if not self._validate_write(command_list):
                print(INVALID_COMMAND)
                return
            print("[Write] Done")

    def make_command(self) -> str:
        command = input("Shell> ")
        return command

    def real_full_read(self):
        for i in range(100):
            self.real_read()

    def real_full_write(self):
        for i in range(100):
            self.real_write()

    def is_invalid_fullwrite_command(self, command: str):
        return True
    def is_invalid_read_command(self, command: list):
        if len(command) < 2:
            return True

        LBA = command[1]
        if not LBA.isdigit():
            return True

        LBA = int(command[1])
        if LBA > 99 or LBA < 0:
            return True

        return False
    def _validate_write(self, args):
        if len(args) != 3:
            return False
        return self._is_valid_lba(args[1]) and self._is_valid_8char_hex(args[2])

    def _is_valid_lba(self, value):
        try:
            num = int(value)
            return 0 <= num <= 99
        except ValueError:
            return False

    def _is_valid_8char_hex(self, write_value_str: str) -> bool:
        return bool(re.fullmatch(r"0x[0-9a-fA-F]{8}", write_value_str))
