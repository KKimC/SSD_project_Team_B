import os.path
import re
import sys

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
    def __init__(self, receiver=None):
        self._is_running = True
        self._receiver = receiver or SSDController()

    @property
    def is_running(self):
        return self._is_running

    def run(self):
        input_command_str, command = self._parse_command()
        if not command or not command.is_valid():
            if input_command_str.strip() == "":
                return
            logger.print("Shell.run()", f"INVALID COMMAND입니다.")
            return

        self._execute_command(command)

    def run_runner(self, shell_script):
        with open(shell_script, "r") as f:
            contents = f.read()
            test_script_commands = contents.splitlines()

        for command_type in test_script_commands:
            command_class = CommandFactory.create(command_type)
            command = command_class(args=[command_type], receiver=self._receiver)
            if not command or not command.is_valid():
                print(INVALID_COMMAND)
                return
            self._execute_command(command)

    def _make_command(self) -> str:
        command = input("Shell> ")
        return command

    def _parse_command(self):
        command_str = self._make_command()
        command_list = command_str.split()
        if not command_list:
            return command_str, None

        command_type = command_list[0]
        command_class = CommandFactory.create(command_type)
        if not command_class:
            return command_str, None

        return command_str, command_class(args=command_list, receiver=self._receiver)

    def _execute_command(self, command: Command):
        try:
            command.execute()
        except ExitException:
            self._is_running = False


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2 and os.path.basename(args[1]) == "shell_scripts.txt":
        shell = SSDShell()
        shell.run_runner(args[1])
    else:
        shell = SSDShell()
        while shell.is_running:
            shell.run()
