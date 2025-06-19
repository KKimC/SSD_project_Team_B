import random
from typing import List
from abc import abstractmethod, ABC
from logger import Logger
import inspect
from src.constants import HELP_TEXT, TestScriptType, EMPTY_VALUE, MAX_ERASE_SIZE
from src.ssd_controller import SSDController
from src.utils.validators import (
    is_int,
    is_valid_lba_address,
    is_valid_8char_hex,
    is_right_script_name,
)

logger = Logger()


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
    def is_valid(self) -> bool:
        ...

    @abstractmethod
    def execute(self):
        ...


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


class ReadCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) < 2:
            return False

        return is_valid_lba_address(self.args[1])

    def execute(self):
        lba_address = self.args[1]
        read_value = self.receiver.read(lba_address)
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
        self.receiver.full_read()
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
        self.receiver.full_write(hex_val)
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"FULLWRITE VALUE: {hex_val}",
        )


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
        lba_1, lba_2 = int(self.args[1]), int(self.args[2])
        end_lba = lba + size - 1
        total = size

        num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)
        for i in range(num_cmds):
            if total < MAX_ERASE_SIZE:
                size = total
                total = 0
            else:
                size = MAX_ERASE_SIZE
                total -= MAX_ERASE_SIZE
            self.receiver.erase(str(lba), str(size))
            lba += MAX_ERASE_SIZE
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"LBA: {lba}, SIZE: {size}",
        )


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
        lba_1, lba_2 = int(self.args[1]), int(self.args[2])
        end_lba = lba_2 if lba_1 < lba_2 else lba_1
        lba = lba_1 if lba_1 < lba_2 else lba_2
        total = end_lba - lba + 1

        num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)
        for i in range(num_cmds):
            if total < MAX_ERASE_SIZE:
                size = total
                total = 0
            else:
                size = MAX_ERASE_SIZE
                total -= MAX_ERASE_SIZE
            self.receiver.erase(str(lba), str(size))
            lba += MAX_ERASE_SIZE
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"LBA: {lba_1}, SIZE: {lba_2}",
        )


class ScriptCommand(Command):
    def __init__(self, args: List[str], receiver: SSDController):
        super().__init__(args, receiver)
        self._test_script_type = ""

    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        script_name = self.args[0]
        if is_right_script_name(script_name, TestScriptType.FULL_WRITE_AND_READ.value):
            self._test_script_type = TestScriptType.FULL_WRITE_AND_READ.value
            return True
        if is_right_script_name(script_name, TestScriptType.PARTIAL_LBA_WRITE.value):
            self._test_script_type = TestScriptType.PARTIAL_LBA_WRITE.value
            return True
        if is_right_script_name(script_name, TestScriptType.WRITE_READ_AGING.value):
            self._test_script_type = TestScriptType.WRITE_READ_AGING.value
            return True
        if is_right_script_name(script_name, TestScriptType.ERASE_AND_AGING.value):
            self._test_script_type = TestScriptType.ERASE_AND_AGING.value
            return True
        return False

    def execute(self):
        if self._test_script_type == TestScriptType.FULL_WRITE_AND_READ.value:
            self._execute_script_1()
        elif self._test_script_type == TestScriptType.PARTIAL_LBA_WRITE.value:
            self._execute_script_2()
        elif self._test_script_type == TestScriptType.WRITE_READ_AGING.value:
            self._execute_script_3()
        elif self._test_script_type == TestScriptType.ERASE_AND_AGING.value:
            self._execute_script_4()

    def _execute_script_1(self):
        for i in range(20):
            write_value_list = [generate_random_hex() for _ in range(5)]

            lba_address = i * 5
            for value in write_value_list:
                self.receiver.write(str(lba_address), value)
                lba_address += 1

            lba_address = i * 5
            for value in write_value_list:
                self._read_compare_and_check_pass_or_fail(lba_address, value)
                lba_address += 1
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_1",
        )

    def _execute_script_2(self):
        for _ in range(30):
            write_value = generate_random_hex()
            lba_address_list = [4, 0, 3, 1, 2]
            for write_lba_address in lba_address_list:
                self.receiver.write(str(write_lba_address), write_value)
            for read_lba_address in range(5):
                self._read_compare_and_check_pass_or_fail(read_lba_address, write_value)
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_2",
        )

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
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_3",
        )

    def _execute_script_4(self):
        for i in range(30):
            lba_address_list = [2 * (i + 1), 2 * (i + 1) + 1, 2 * (i + 1) + 2]
            write_value = generate_random_hex()
            self.receiver.write(str(lba_address_list[0]), write_value)
            # Overwrite
            self.receiver.write(str(lba_address_list[0]), write_value)
            self.receiver.erase(str(lba_address_list[0]), str(3))
            for lba_address in lba_address_list:
                self._read_compare_and_check_pass_or_fail(lba_address, EMPTY_VALUE)
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"SCRIPT_4",
        )

    def _read_compare_and_check_pass_or_fail(
        self, read_lba_address: int, write_value: str
    ):
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
        logger.print(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}()",
            f"HELP",
        )
        return
