import shutil
import sys
import re
import os
from ssd_file_manager import SSDFileManager
from typing import List

class SSD:
    def __init__(self):
        self.select_file_manager(SSDFileManager())

    def select_file_manager(self, file_manager):
        self.ssd_file_manager = file_manager

    def _is_valid_lba(self, address):
        return isinstance(address, int) and 0 <= address < 100

    def _is_valid_value(self, value):
        return bool(re.fullmatch(r'0x[0-9a-fA-F]{8}', value))

    def read(self, address=-1):
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        nand = self.ssd_file_manager.read_ssd_nand()
        value = nand[address]
        self.ssd_file_manager.print_ssd_output(value)
        return value

    def write(self, address=-1, value="ERROR"):
        if not self._is_valid_lba(address) or not self._is_valid_value(value):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        nand = self.ssd_file_manager.read_ssd_nand()
        nand[address] = value
        self.ssd_file_manager.patch_ssd_nand(nand)
        return value

    @staticmethod
    def get_buffer() -> List[str]:
        return sorted(os.listdir('buffer'))

    @staticmethod
    def update_buffer(commands: List[str]) -> None:
        if len(commands) != 5:
            return

        buffer_dir = 'buffer'

        if os.path.exists(buffer_dir):
            shutil.rmtree(buffer_dir)
        os.makedirs(buffer_dir, exist_ok=True)

        for idx, command in enumerate(commands[:5], start=1):
            file_path = os.path.join(buffer_dir, f"{idx}_temp")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(command)

            target_path = os.path.join(buffer_dir, command)
            os.replace(file_path, target_path)


def main():
    ssd = SSD()

    if len(sys.argv) < 3:
        print("Usage: python ssd.py R [LBA] or python ssd.py W [LBA] [VALUE]")
        return "ERROR"

    command = sys.argv[1]
    try:
        address = int(sys.argv[2])
    except ValueError:
        ssd.ssd_file_manager.print_ssd_output("ERROR")
        return "ERROR"

    if command == "R" and len(sys.argv) == 3:
        read_result = ssd.read(address)
        if os.getenv("SUBPROCESS_CALL") == "1":
            print(read_result)

    elif command == "W" and len(sys.argv) == 4:
        value = sys.argv[3]
        ssd.write(address, value)

    else:
        ssd.ssd_file_manager.print_ssd_output("ERROR")


if __name__ == "__main__":
    main()
