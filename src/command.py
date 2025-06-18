import re
import subprocess
from typing import List
from abc import abstractmethod, ABC


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
            result = subprocess.run(
                ["python", "ssd.py", "R", f"{i}"],
                capture_output=True,
                text=True,
            )
            print(result)

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
            cmd = ["python", "ssd.py", "W", str(lba), self.args[1]]
            result = subprocess.run(cmd)
        print("[Write] Done")
        return


class ExitCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        raise ExitException
