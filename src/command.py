import random
from typing import List
from abc import abstractmethod, ABC

from src.constants import HELP_TEXT
from src.ssd_controller import SSDController
from src.utils.validators import is_int, is_valid_lba_address, is_valid_8char_hex


def generate_random_hex() -> str:
    value = random.randint(0, 0xFFFFFFFF)  # 32비트 범위 (8자리)
    return f"0x{value:08X}"  # 대문자, 0으로 패딩


class ExitException(Exception):
    pass


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


class ReadCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) < 2:
            return False

        return is_valid_lba_address(self.args[1])

    def execute(self):
        lba_address = self.args[1]
        read_value = self.receiver.read(lba_address)
        return read_value


class FullReadCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        self.receiver.full_read()


class FullWriteCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 2:
            return False
        return is_valid_8char_hex(self.args[1])

    def execute(self):
        hex_val = self.args[1]
        self.receiver.full_write(hex_val)


class ExitCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        raise ExitException


class EraseCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 3:
            return False

        lba_address, size = self.args[1:]
        if not is_valid_lba_address(lba_address):
            return False

        return is_int(size)

    def execute(self):
        lba, size = self.args[1:]
        self.receiver.erase(lba, size)


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
        lba_1, lba_2 = self.args[1:]
        self.receiver.eraserange(lba_1, lba_2)


class ScriptCommand(Command):
    def __init__(self, args: List[str], receiver: SSDController):
        super().__init__(args, receiver)
        self._test_script_type = ""

    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False

        if self.args[0] in ["1_", "1_FullWriteAndReadCompare"]:
            self._test_script_type = "1_FullWriteAndReadCompare"
            return True
        if self.args[0] in ["2_", "2_PartialLBAWrite"]:
            self._test_script_type = "2_PartialLBAWrite"
            return True
        if self.args[0] in ["3_", "3_WriteReadAging"]:
            self._test_script_type = "3_WriteReadAging"
            return True
        return False

    def execute(self):
        if self._test_script_type == "1_FullWriteAndReadCompare":
            self._execute_script_1()
        elif self._test_script_type == "2_PartialLBAWrite":
            self._execute_script_2()
        elif self._test_script_type == "3_WriteReadAging":
            self._execute_script_3()

    def _execute_script_1(self):
        for lba_address in range(100):
            write_value_list = [generate_random_hex() for _ in range(5)]
            for value in write_value_list:
                self.receiver.write(str(lba_address), value)
                self._read_compare_and_check_pass_or_fail(lba_address, value)

    def _execute_script_2(self):
        for _ in range(30):
            write_value = generate_random_hex()
            lba_address_list = [4, 0, 3, 1, 2]
            for write_lba_address in lba_address_list:
                self.receiver.write(str(write_lba_address), write_value)
            for read_lba_address in range(5):
                self._read_compare_and_check_pass_or_fail(read_lba_address, write_value)

    def _execute_script_3(self):
        lba_address_list = [0, 99]
        for _ in range(200):
            write_value_list = [generate_random_hex()] * 2
            for i, lba_address in enumerate(lba_address_list):
                self.receiver.write(str(lba_address), write_value_list[i])
            for i, lba_address in enumerate(lba_address_list):
                self._read_compare_and_check_pass_or_fail(
                    lba_address, write_value_list[i]
                )

    def _read_compare_and_check_pass_or_fail(self, read_lba_address, write_value):
        if self._read_compare(read_lba_address, write_value):
            print("PASS")
        else:
            print("FAIL")
            raise ExitException

    def _read_compare(self, lba_address: int, value: str) -> bool:
        result = self.receiver.read(str(lba_address))
        return result.strip() == value.strip()


class HelpCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        print(HELP_TEXT)
        return
