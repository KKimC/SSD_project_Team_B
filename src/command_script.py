import inspect
from abc import ABC, abstractmethod

from constants import EMPTY_VALUE
from custom_exception import ExitException
from logger import Logger
from ssd_controller import SSDController
from utils.helpers import generate_random_hex


logger = Logger()


def _read_compare(receiver: SSDController, lba: int, write_value: str) -> bool:
    return receiver.read(str(lba)).strip() == write_value.strip()


class ScriptCommandType(ABC):
    def __init__(self, args, receiver):
        self.args = args
        self.receiver = receiver

    @abstractmethod
    def execute(self): ...


class FullWriteAndReadCommand(ScriptCommandType):
    SCRIPT_TYPE = "1_"
    SCRIPT_TYPE_FULL = "1_FullWriteAndReadCompare"

    def execute(self):
        for i in range(20):
            write_value_list = [generate_random_hex() for _ in range(5)]

            lba_address = i * 5
            for value in write_value_list:
                self.receiver.write(str(lba_address), value)
                lba_address += 1

            lba_address = i * 5
            for value in write_value_list:
                if _read_compare(self.receiver, lba_address, value) == False:
                    raise ExitException
                lba_address += 1
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_1",
        )


class PartialLbaWriteCommand(ScriptCommandType):
    SCRIPT_TYPE = "2_"
    SCRIPT_TYPE_FULL = "2_PartialLBAWrite"

    def execute(self):
        for _ in range(30):
            write_value = generate_random_hex()
            lba_address_list = [4, 0, 3, 1, 2]
            for write_lba_address in lba_address_list:
                self.receiver.write(str(write_lba_address), write_value)
            for read_lba_address in range(5):
                if _read_compare(self.receiver, read_lba_address, write_value) == False:
                    raise ExitException
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_2",
        )


class WriteReadAgingCommand(ScriptCommandType):
    SCRIPT_TYPE = "3_"
    SCRIPT_TYPE_FULL = "3_WriteReadAging"

    def execute(self):
        lba_address_list = [0, 99]
        for _ in range(200):
            write_value_list = [generate_random_hex()] * 2
            for i, lba_address in enumerate(lba_address_list):
                self.receiver.write(str(lba_address), write_value_list[i])
            for i, lba_address in enumerate(lba_address_list):
                if (
                    _read_compare(self.receiver, lba_address, write_value_list[i])
                    == False
                ):
                    raise ExitException
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_3",
        )


class EraseAndAgingCommand(ScriptCommandType):
    SCRIPT_TYPE = "4_"
    SCRIPT_TYPE_FULL = "4_EraseAndWriteAging"

    def execute(self):
        for i in range(30):
            lba_address_list = [2 * (i + 1), 2 * (i + 1) + 1, 2 * (i + 1) + 2]
            write_value = generate_random_hex()
            self.receiver.write(str(lba_address_list[0]), write_value)
            # Overwrite
            self.receiver.write(str(lba_address_list[0]), write_value)
            self.receiver.erase(str(lba_address_list[0]), str(3))
            for lba_address in lba_address_list:
                if _read_compare(self.receiver, lba_address, EMPTY_VALUE) == False:
                    raise ExitException
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_4",
        )


list_script_commands = [
    FullWriteAndReadCommand,
    PartialLbaWriteCommand,
    WriteReadAgingCommand,
    EraseAndAgingCommand,
]


def get_matched_script(command_str: str):
    for script_command in list_script_commands:
        if (
            command_str.startswith(script_command.SCRIPT_TYPE)
            and command_str in script_command.SCRIPT_TYPE_FULL
        ):
            return script_command
    return None
