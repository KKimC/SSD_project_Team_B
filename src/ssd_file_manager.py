import os

class SSDFileManager():
    def __init__(self):
        if not os.path.exists('ssd_nand.txt'):
            with open('ssd_nand.txt', 'w', encoding='utf-8') as f:
                f.writelines(["\n"] * 100)

        if not os.path.exists('ssd_output.txt'):
            with open('ssd_output.txt', 'w', encoding='utf-8') as f:
                f.write("")

    def read_ssd_nand(self):
        with open('ssd_nand.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return [line.rstrip('\n') for line in lines[:100]]

    def patch_ssd_nand(self, nand_list):
        if len(nand_list) != 100:
            raise ValueError("입력 리스트는 100개의 문자열을 포함해야 합니다.")
        with open('ssd_nand.txt', 'w', encoding='utf-8') as file:
            for line in nand_list:
                file.write(f"{line}\n")

    def print_ssd_output(self, string):
        with open('ssd_output.txt', 'w', encoding='utf-8') as file:
            file.write(string)


sfm = SSDFileManager()
nand = sfm.read_ssd_nand()
nand[1] = "0x00000001"
sfm.patch_ssd_nand(nand)
print(sfm.read_ssd_nand()[1])
sfm.print_ssd_output("nand")

