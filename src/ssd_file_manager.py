import os

class SSDFileManager():
    def __init__(self):
        if not os.path.exists('ssd_nand.txt'):
            with open('ssd_nand.txt', 'w', encoding='utf-8') as f:
                f.writelines(["\n"] * 100)
            self.patch_ssd_nand(["0x00000000" for _ in range(100)])

        if not os.path.exists('ssd_output.txt'):
            with open('ssd_output.txt', 'w', encoding='utf-8') as f:
                f.write("")

    def read_ssd_nand(self):
        with open('ssd_nand.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return [line.rstrip('\n') for line in lines[:100]]

    def patch_ssd_nand(self, nand_list):
        with open('ssd_nand.txt', 'w', encoding='utf-8') as file:
            for line in nand_list:
                file.write(f"{line}\n")

    def print_ssd_output(self, string):
        with open('ssd_output.txt', 'w', encoding='utf-8') as file:
            file.write(string)