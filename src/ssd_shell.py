import re

from src.command import (
    WriteCommand,
    ReadCommand,
    FullReadCommand,
    FullWriteCommand,
    ExitCommand,
    ExitException,
)

INVALID_COMMAND = "INVALID COMMAND"


class SsdShell:
    COMMAND_MAP = {
        "read": ReadCommand,
        "write": WriteCommand,
        "fullread": FullReadCommand,
        "fullwrite": FullWriteCommand,
        "exit": ExitCommand,
    }

    def __init__(self):
        self.validator = {}
        self._is_running = True

    @property
    def is_running(self):
        return self._is_running

    def _make_cmds_for_fullread(self):
        list_cmds = []
        for i in range(100):
            list_cmds.append(f"ssd.py R {i}")
        return list_cmds

    def run(self):
        command_str = self.make_command()
        command_list = command_str.split()
        if not command_list:
            print(INVALID_COMMAND)
            return

        command_type = command_list[0]
        command_class = self.COMMAND_MAP.get(command_type)
        if not command_class:
            print(INVALID_COMMAND)
            return

        command = command_class(args=command_list)
        if not command.is_valid():
            print(INVALID_COMMAND)
            return

        try:
            command.execute()
        except ExitException:
            self._is_running = False

    def make_command(self) -> str or list[str]:
        command = input("Shell> ")
        return command


if __name__ == "__main__":
    shell = SsdShell()
    while shell.is_running:
        shell.run()
