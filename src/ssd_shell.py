import re
from logger import Logger

logger = Logger()


from src.command import (
    ExitException,
    Command,
)
from src.command_factory import CommandFactory
from src.constants import INVALID_COMMAND
from src.ssd_controller import SSDController


class SSDShell:
    def __init__(self):
        self._is_running = True
        self._receiver = SSDController()

    @property
    def is_running(self):
        return self._is_running

    def run(self):
        command = self._parse_command()
        if not command or not command.is_valid():
            print(INVALID_COMMAND)
            logger.print("Shell.run()", f"INVALID COMMAND입니다.")
            return

        self._execute_command(command)

    def _make_command(self) -> str:
        command = input("Shell> ")
        return command

    def _parse_command(self):
        command_str = self._make_command()
        command_list = command_str.split()

        if not command_list:
            return None

        command_type = command_list[0]
        command_class = CommandFactory.create(command_type)
        if not command_class:
            return None

        return command_class(args=command_list, receiver=self._receiver)

    def _execute_command(self, command: Command):
        try:
            command.execute()
        except ExitException:
            self._is_running = False


if __name__ == "__main__":
    shell = SSDShell()
    while shell.is_running:
        shell.run()
