import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
SSD_NAND_FILE_PATH = os.path.join(OUTPUT_DIR, "ssd_nand.txt")
SSD_OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, "ssd_output.txt")


class SSDFileManager:
    def __init__(self):
        if not os.path.exists(SSD_NAND_FILE_PATH):
            with open(SSD_NAND_FILE_PATH, "w", encoding="utf-8") as f:
                f.writelines(["\n"] * 100)
            self.patch_ssd_nand(["0x00000000" for _ in range(100)])

        if not os.path.exists(SSD_OUTPUT_FILE_PATH):
            with open(SSD_OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
                f.write("")

        buffer_dir = "buffer"
        if not os.path.exists(buffer_dir):
            os.makedirs(buffer_dir)

        existing_files = os.listdir(buffer_dir)
        existing_prefixes = {filename.split("_")[0] for filename in existing_files}

        for i in range(1, 6):
            if str(i) not in existing_prefixes:
                buffer_file = os.path.join(buffer_dir, f"{i}_empty")
                with open(buffer_file, "w", encoding="utf-8") as f:
                    f.write("")

    def read_ssd_nand(self):
        with open(SSD_NAND_FILE_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return [line.rstrip("\n") for line in lines[:100]]

    def patch_ssd_nand(self, nand_list):
        with open(SSD_NAND_FILE_PATH, "w", encoding="utf-8") as file:
            for line in nand_list:
                file.write(f"{line}\n")

    def print_ssd_output(self, string):
        with open(SSD_OUTPUT_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(string)
