import re
from logger import Logger

logger = Logger()

from src.command import (
    WriteCommand,
    ReadCommand,
    FullReadCommand,
    FullWriteCommand,
    ExitCommand,
    ExitException,
    HelpCommand,
    Command,
    ScriptCommand,
)

INVALID_COMMAND = "INVALID COMMAND"


class SSDShell:
    COMMAND_MAP = {
        "read": ReadCommand,
        "write": WriteCommand,
        "fullread": FullReadCommand,
        "fullwrite": FullWriteCommand,
        "exit": ExitCommand,
        "help": HelpCommand,
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
        command = self._parse_command()
        if not command or not command.is_valid():
            print(INVALID_COMMAND)
            logger.print("Shell.run()", f"INVALID COMMAND입니다.")
            return

        self._execute_command(command)

    def _make_command(self) -> str or list[str]:
        command = input("Shell> ")
        return command

    def _parse_command(self):
        command_str = self._make_command()
        command_list = command_str.split()

        if not command_list:
            return None

        command_type = command_list[0]
        command_class = self.COMMAND_MAP.get(command_type)
        if not command_class:
            if command_type in [
                "1_",
                "1_FullWriteAndReadCompare",
                "2_",
                "2_PartialLBAWrite",
                "3_",
                "3_WriteReadAging",
            ]:
                return ScriptCommand(args=command_list)
            return None

        return command_class(args=command_list)

    def _execute_command(self, command: Command):
        try:
            command.execute()
        except ExitException:
            self._is_running = False


if __name__ == "__main__":
    shell = SSDShell()
    while shell.is_running:
        shell.run()
