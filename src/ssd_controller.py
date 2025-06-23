import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SSD_FILE_PATH = os.path.join(SCRIPT_DIR, "ssd.py")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
SSD_OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, "ssd_output.txt")


class SSDController:
    def write(self, lba: str, hex_val: str):
        subprocess.run(["python", SSD_FILE_PATH, "W", lba, hex_val])

    def read(self, lba: str):
        subprocess.run(["python", SSD_FILE_PATH, "R", lba])

        with open(SSD_OUTPUT_FILE_PATH, "r") as f:
            read_value = f.read().strip()

        return read_value

    def erase(self, lba: str, size: str):
        subprocess.run(["python", SSD_FILE_PATH, "E", lba, size])

    def flush(self):
        subprocess.run(["python", SSD_FILE_PATH, "F"])
