from command import (
    WriteCommand,
    ReadCommand,
    FullWriteCommand,
    FullReadCommand,
    ExitCommand,
    HelpCommand,
    ScriptCommand,
    FlushCommand,
    EraseCommand,
    EraseRangeCommand,
)


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
        if command_str == "flush":
            return FlushCommand
        if command_str == "erase":
            return EraseCommand
        if command_str == "erase_range":
            return EraseRangeCommand
        if ScriptCommand.is_script_name_matched(command_str):
            return ScriptCommand
        return None
