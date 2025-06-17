from src.ssd_file_manager import SSDFileManager

class SSD():
    def __init__(self):
        self.nand = [0 for _ in range(100)]
        self.ssd_file_manager = SSDFileManager()

    def select_file_manager(self, file_manager):
        self.ssd_file_manager = file_manager

    def _is_valid_lba(self, address):
        return isinstance(address, int) and 0 <= address < 100

    def _is_valid_value(self, value):
        return isinstance(value, str) and value.startswith("0x") and len(value) == 10

    def Read(self, address):
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return

        nand = self.ssd_file_manager.read_ssd_nand()
        value = nand[address] if address < len(nand) else 0x00000000

        if value == 0:
            self.ssd_file_manager.print_ssd_output("0x00000000")
            return 0x00000000

        self.ssd_file_manager.print_ssd_output(hex(value))
        return value

    def Write(self, address, value):
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return

        if not self._is_valid_value(value):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return

        self.nand[address] = int(value, 16)
        self.ssd_file_manager.patch_ssd_nand(self.nand)
        self.ssd_file_manager.print_ssd_output(value)

    def read(self, address):
        if 0 <= address < len(self.nand):
            return self.nand[address]
        return 0  # out-of-bound read 기본 처리
