import os.path
import sys

from logger import Logger

from command import Command
from command_factory import CommandFactory
from constants import INVALID_COMMAND
from ssd_controller import SSDController

from custom_exception import ExitException

logger = Logger()


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


class SSDRunner:
    def __init__(self, receiver=None):
        self._receiver = receiver or SSDController()

    def run(self, shell_script):
        with open(shell_script, "r") as f:
            contents = f.read()
            test_script_commands = contents.splitlines()

        for command_str in test_script_commands:
            input_command_str, command = self._parse_command(command_str)
            if not command or not command.is_valid():
                print(INVALID_COMMAND)
                logger.print("Runner.run()", f"INVALID COMMAND입니다.")
                return

            self._execute_command(command)

    def _execute_command(self, command: Command):
        try:
            command.execute()
        except ExitException:
            exit()

    def _parse_command(self,command_str):
        command_list = command_str.split()
        if not command_list:
            return command_str, None

        command_type = command_list[0]
        command_class = CommandFactory.create(command_type)
        if not command_class:
            return command_str, None

        return command_str, command_class(args=command_list, receiver=self._receiver)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2 and os.path.basename(args[1]) == "shell_scripts.txt":
        runner = SSDRunner()
        runner.run(args[1])
    else:
        shell = SSDShell()
        while shell.is_running:
            shell.run()
