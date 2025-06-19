import sys
import re
import os
from ssd_file_manager import SSDFileManager


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

    def erase(self, address=-1, size=0):
        MAX_ERASE_SIZE = 10
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        if not isinstance(size, int) or not (0 <= size <= MAX_ERASE_SIZE):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        LAST_LBA = address + size - 1
        if LAST_LBA > 99:
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        for lba in range(address, address + size):
            self.write(lba, "0x00000000")
        return "OK"

    def flush_write(self, address=-1, value="ERROR"):
        if not self._is_valid_lba(address) or not self._is_valid_value(value):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        nand = self.ssd_file_manager.read_ssd_nand()
        nand[address] = value
        self.ssd_file_manager.patch_ssd_nand(nand)
        return value

    def flush_erase(self, address=-1, size=0):
        MAX_ERASE_SIZE = 10
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        if not isinstance(size, int) or not (0 <= size <= MAX_ERASE_SIZE):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        LAST_LBA = address + size - 1
        if LAST_LBA > 99:
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        for lba in range(address, address + size):
            self.flush_write(lba, "0x00000000")
        return "OK"

    def flush(self):
        buffer_list = self.get_buffer()

        for entry in buffer_list:
            parts = entry.split('_')
            if len(parts) < 2: # empty case
                continue

            cmd = parts[1]
            if cmd == "W" and len(parts) == 4:
                address = int(parts[2])
                value = parts[3]
                self.flush_write(address, value)

            elif cmd == "E" and len(parts) == 4:
                address = int(parts[2])
                size = int(parts[3])
                self.flush_erase(address, size)

        updated_buffer_list = ["1_empty", "2_empty", "3_empty", "4_empty", "5_empty"]
        self.update_buffer(updated_buffer_list)

    def get_buffer(self):
        return

    def update_buffer(self, updated_buffer_list):
        pass


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

    elif command == "E" and len(sys.argv) == 4:
        size = int(sys.argv[3])
        ssd.erase(address, size)

    elif command == "F" and len(sys.argv) == 1:
        ssd.flush()

    else:
        ssd.ssd_file_manager.print_ssd_output("ERROR")


if __name__ == "__main__":
    main()
