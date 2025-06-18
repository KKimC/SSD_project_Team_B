import os
import re
import random
import subprocess
from typing import List
from abc import abstractmethod, ABC

def generate_random_hex() -> str:
    value = random.randint(0, 0xFFFFFFFF)  # 32비트 범위 (8자리)
    return f"0x{value:08X}"  # 대문자, 0으로 패딩

HELP_TEXT = """
AUTHOR
    비긴어게인 팀 제작자: 김성현, 강태윤, 임동혁, 김남민, 김기웅, 정보람, 김민규

NAME
    Test Shell - SSD 가상 장치 테스트용 커맨드 라인 셸

SYNOPSIS
    write [LBA] [VALUE]
    read [LBA]
    fullwrite [VALUE]
    fullread
    help
    exit

DESCRIPTION

    write
        지정한 LBA 주소에 값을 기록합니다.
        사용법: write [LBA 번호] [저장할 값]
        예시:  write 3 0xAAAABBBB

    read
        지정한 LBA 주소에서 값을 읽어 출력합니다.
        사용법: read [LBA 번호]
        예시:  read 3

    fullwrite
        전체 LBA(0~99)에 동일한 값을 기록합니다.
        사용법: fullwrite [저장할 값]
        예시:  fullwrite 0xABCDFFFF

    fullread
        전체 LBA(0~99)에서 값을 읽어 순차적으로 출력합니다.
        사용법: fullread

    help
        명령어 목록 및 설명과 제작자 정보를 출력합니다.
        사용법: help

    exit
        Test Shell을 종료합니다.
        사용법: exit"""

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

        env = os.environ.copy()
        env["SUBPROCESS_CALL"] = "1"  # subprocess 호출임을 알림


        result = subprocess.run(
            ["python", "ssd.py", "R", lba_address],
            capture_output=True,
            text=True,
            env=env,
        )
        read_value = result.stdout
        print(f"[Read] LBA {lba_address.zfill(2)} : {read_value}")


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
            print(result.stdout)

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


class ScriptCommand(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)
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

    def _execute_script_2(self):
        for _ in range(30):
            write_value = generate_random_hex()
            lba_address_list = [4, 0, 3, 1, 2]
            for write_lba_address in lba_address_list:
                command_list = ["write", str(write_lba_address), write_value]
                WriteCommand(command_list).execute()

            for read_lba_address in range(5):
                if self._read_compare(read_lba_address, write_value):
                    print("PASS")
                else:
                    print("FAIL")
                    raise ExitException

    def _execute_script_3(self):
        lba_address_list = [0, 99]
        for _ in range(200):
            write_value_list = [generate_random_hex()] * 2
            for i, lba_address in enumerate(lba_address_list):
                WriteCommand(["write", lba_address, write_value_list[i]]).execute()

            for i, lba_address in enumerate(lba_address_list):
                if self._read_compare(lba_address, write_value_list[i]):
                    print("PASS")
                else:
                    print("FAIL")
                    raise ExitException

    def _read_compare(self, lba_address: int, value: str) -> bool:
        read_command = ReadCommand(["read", str(lba_address)])
        result = read_command.execute()
        return result == value
class HelpCommand(Command):
    def is_valid(self) -> bool:
        if len(self.args) != 1:
            return False
        return True

    def execute(self):
        print(HELP_TEXT)
        return
