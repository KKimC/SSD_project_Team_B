import re
import random
import subprocess
from typing import List
from abc import abstractmethod, ABC

import random


def generate_random_hex() -> str:
    value = random.randint(0, 0xFFFFFFFF)  # 32비트 범위 (8자리)
    return f"0x{value:08X}"  # 대문자, 0으로 패딩


class ExitException(Exception):
    pass


class Command(ABC):
    def __init__(self, args: List[str]):
        self.args = args

    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def execute(self): ...

    def _is_valid_8char_hex(self, write_value_str: str) -> bool:
        return bool(re.fullmatch(r"0x[0-9a-fA-F]{8}", write_value_str))

    def _is_valid_lba(self, value: str) -> bool:
        try:
            num = int(value)
            return 0 <= num <= 99
        except ValueError:
            return False


class WriteCommand(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)

    def is_valid(self) -> bool:
        if len(self.args) != 3:
            return False
        lba_address, write_value = self.args[1:]
        return self._is_valid_lba(lba_address) and self._is_valid_8char_hex(write_value)

    def execute(self):
        lba_address = self.args[1]
        hex_val = self.args[2]

        result = subprocess.run(
            ["python", "ssd.py", "W", lba_address, hex_val],
            capture_output=True,
            text=True,
        )
        print("[Write] Done")


class ReadCommand(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)

    def is_valid(self) -> bool:
        if len(self.args) < 2:
            return False

        return self._is_valid_lba(self.args[1])

    def execute(self):
        lba_address = self.args[1]

        result = subprocess.run(
            ["python", "ssd.py", "R", lba_address],
            capture_output=True,
            text=True,
        )
        print("[Read] Done")


class FullReadCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        list_cmds = self._make_cmds_for_fullread()
        for i in range(100):
            print("0x00000000")

    def _make_cmds_for_fullread(self):
        list_cmds = []
        for i in range(100):
            list_cmds.append(f"ssd.py R {i}")
        return list_cmds


class FullWriteCommand(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)

    def is_valid(self) -> bool:
        if len(self.args) != 2:
            return False
        return self._is_valid_8char_hex(self.args[1])

    def execute(self):
        for lba in range(100):
            cmd = ["python", "ssd.py", "W", int(lba), self.args[1]]
            result = subprocess.run(cmd)
        print("[Write] Done")


class ExitCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        raise ExitException


class FullWriteAndReadCompareCommand(Command):

    def is_valid(self) -> bool:
        if len(self.args) == 1 and self.args[0] in ["1_", "1_FullWriteAndReadCompare"]:
            return True
        return False

    def execute(self):
        lba_address = 0
        while lba_address < 100:
            write_value_list = [generate_random_hex() for _ in range(5)]
            for value in write_value_list:
                command_list = ["write", str(lba_address), value]
                WriteCommand(command_list).execute()
                if self._read_compare(lba_address, value):
                    print("PASS")
                else:
                    print("FAIL")
                    raise ExitException
                lba_address += 1

    def _read_compare(self, lba_address: int, value: str) -> bool:
        read_command = ReadCommand(["read", lba_address])
        result = read_command.execute()
        return result == value
