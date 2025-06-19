from src.command import (
    WriteCommand,
    ReadCommand,
    FullWriteCommand,
    FullReadCommand,
    ExitCommand,
    HelpCommand,
    ScriptCommand,
    EraseCommand,
    EraseRangeCommand,
)
from src.constants import TestScriptType
from src.utils.validators import is_right_script_name


class CommandFactory:
    @staticmethod
    def create(command_str: str):
        if command_str == "read":
            return ReadCommand
        if command_str == "write":
            return WriteCommand
        if command_str == "fullwrite":
            return FullWriteCommand
        if command_str == "fullread":
            return FullReadCommand
        if command_str == "exit":
            return ExitCommand
        if command_str == "help":
            return HelpCommand
        if command_str == "erase":
            return EraseCommand
        if command_str == "erase_range":
            return EraseRangeCommand
        if (
            is_right_script_name(command_str, TestScriptType.FULL_WRITE_AND_READ.value)
            or is_right_script_name(command_str, TestScriptType.PARTIAL_LBA_WRITE.value)
            or is_right_script_name(command_str, TestScriptType.WRITE_READ_AGING.value)
            or is_right_script_name(command_str, TestScriptType.ERASE_AND_AGING.value)
        ):

            return ScriptCommand
        return None
