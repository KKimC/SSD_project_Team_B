from src.command import (
    WriteCommand,
    ReadCommand,
    FullWriteCommand,
    FullReadCommand,
    ExitCommand,
    HelpCommand,
    ScriptCommand,
    FlushCommand,
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
        if (
            (
                command_str.startswith("1_")
                and command_str in "1_FullWriteAndReadCompare"
            )
            or (command_str.startswith("2_") and command_str in "2_PartialLBAWrite")
            or (command_str.startswith("3_") and command_str in "3_WriteReadAging")
        ):

            return ScriptCommand
        return None
