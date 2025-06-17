from src.ssd_file_manager import SSDFileManager


class SSD():
    def __init__(self):
        self.nand = [ 0 for _ in range(100) ]
        self.ssd_file_manager = SSDFileManager()

    def select_file_manager(self):
        self.ssd_file_manager = SSDFileManager()

    def read(self, add):
        return self.nand[add]

    def write(self):
        pass