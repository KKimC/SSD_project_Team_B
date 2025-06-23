from typing import List
from abc import abstractmethod, ABC
from logger import Logger
import inspect

from command_script import (
    list_script_commands,
    get_matched_script,
)
from constants import HELP_TEXT, MAX_ERASE_SIZE
from custom_exception import ExitException
from ssd_controller import SSDController
from utils.helpers import (
    adjust_lba_and_count,
    normalize_lba_range,
)
from utils.validators import (
    is_int,
    is_valid_lba_address,
    is_valid_8char_hex,
)

logger = Logger()


class Command(ABC):
    def __init__(self, args: List[str], receiver: SSDController):
        self.args = args
        self.receiver = receiver

    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def execute(self): ...


class WriteCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 3:
            return False
        lba_address, write_value = self.args[1:]
        return is_valid_lba_address(lba_address) and is_valid_8char_hex(write_value)

    def execute(self):
        lba_address = self.args[1]
        hex_val = self.args[2]
        self.receiver.write(lba_address, hex_val)
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"LBA: {lba_address}, VALUE: {hex_val}",
        )
        print("[Write] Done")


class ReadCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 2:
            return False

        return is_valid_lba_address(self.args[1])

    def execute(self):
        lba_address = self.args[1]
        read_value = self.receiver.read(lba_address)
        print(f"[Read] LBA {lba_address} : {read_value}")
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"LBA: {lba_address}, VALUE: {read_value.rstrip()}",
        )

        return read_value


class FullReadCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        for lba_address in range(100):
            read_value = self.receiver.read(str(lba_address))
            print(f"[Read] LBA {lba_address} : {read_value}")
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"FULLREAD",
        )

class FullWriteCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 2:
            return False
        return is_valid_8char_hex(self.args[1])

    def execute(self):
        hex_val = self.args[1]
        for lba_address in range(100):
            self.receiver.write(str(lba_address), hex_val)
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"FULLWRITE VALUE: {hex_val}",
        )
        print("[Full-Write] Done")


class ExitCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"EXIT",
        )
        raise ExitException


def erase_per_chunk(receiver, lba: int, total: int):
    num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)
    for i in range(num_cmds):
        if total < MAX_ERASE_SIZE:
            size = total
            total = 0
        else:
            size = MAX_ERASE_SIZE
            total -= MAX_ERASE_SIZE
        receiver.erase(str(lba), str(size))
        lba += MAX_ERASE_SIZE


class EraseCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 3:
            return False

        lba_address, size = self.args[1:]
        if not is_valid_lba_address(lba_address):
            return False

        return is_int(size)

    def execute(self):
        lba, size = int(self.args[1]), int(self.args[2])
        adjusted_start_lba, total = adjust_lba_and_count(lba, size)
        erase_per_chunk(self.receiver, adjusted_start_lba, total)
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"LBA: {lba}, SIZE: {size}",
        )
        print("[Erase] Done")


class EraseRangeCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 3:
            return False

        start_lba_address, end_lba_address = self.args[1:]
        if is_valid_lba_address(start_lba_address) and is_valid_lba_address(
            end_lba_address
        ):
            return True
        return False

    def execute(self):
        start_lba, end_lba = int(self.args[1]), int(self.args[2])
        adjusted_start_lba, total = normalize_lba_range(start_lba, end_lba)
        erase_per_chunk(self.receiver, adjusted_start_lba, total)

        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"START_LBA: {start_lba}, END_LBA: {end_lba}",
        )
        print("[Erase-Range] Done")


class ScriptCommand(Command):
    @staticmethod
    def is_script_name_matched(command_str: str) -> bool:
        for script_command in list_script_commands:
            if (
                command_str.startswith(script_command.SCRIPT_TYPE)
                and command_str in script_command.SCRIPT_TYPE_FULL
            ):
                return True
        return False

    def __init__(self, args: List[str], receiver: SSDController):
        super().__init__(args, receiver)

        # inject strategy
        script_class = get_matched_script(args[0])
        self.script_command_type = script_class(self.args, self.receiver)

    def is_valid(self) -> bool:
        return True if len(self.args) == 1 else False

    def execute(self):
        self.script_command_type.execute()


class HelpCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        print(HELP_TEXT)
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"HELP",
        )
        return


class FlushCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"FLUSH",
        )
        self.receiver.flush()
        print("[Flush] Done")
