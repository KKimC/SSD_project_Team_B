import sys
from src.ssd_file_manager import SSDFileManager

class SSD():
    def __init__(self):
        self.nand = ["0x00000000" for _ in range(100)]
        self.ssd_file_manager = SSDFileManager()

    def select_file_manager(self, file_manager):
        self.ssd_file_manager = file_manager

    def _is_valid_lba(self, address):
        return isinstance(address, int) and 0 <= address < 100

    def _is_valid_value(self, value):
        return isinstance(value, str) and value.startswith("0x") and len(value) == 10

    def read(self, address=-1):
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        nand = self.ssd_file_manager.read_ssd_nand()
        value = nand[address]
        print(value)
        self.ssd_file_manager.print_ssd_output(value)
        return value

    def write(self, address=-1, value="ERROR"):
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        if not self._is_valid_value(value):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        self.nand[address] = int(value, 16)
        self.ssd_file_manager.patch_ssd_nand(self.nand)
        self.ssd_file_manager.print_ssd_output(value)
        return value

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
        ssd.read(address)

    elif command == "W" and len(sys.argv) == 4:
        value = sys.argv[3]
        ssd.write(address, value)

    else:
        ssd.ssd_file_manager.print_ssd_output("ERROR")

if __name__ == '__main__':
    main()