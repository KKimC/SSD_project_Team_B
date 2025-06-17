from src.ssd_file_manager import SSDFileManager


class SSD():
    def __init__(self):
        self.nand = [ 0 for _ in range(100) ]
        self.ssd_file_manager = SSDFileManager()

    def select_file_manager(self, file_manager):
        self.ssd_file_manager = file_manager

    def read(self, address):
        return self.nand[address]

    def write(self, address, value):
        pass