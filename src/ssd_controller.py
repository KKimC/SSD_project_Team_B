import os
import subprocess


class SSDController:
    def write(self, lba: str, hex_val: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))

        ssd_file_path = os.path.join(script_dir, "ssd.py")
        subprocess.run(["python", ssd_file_path, "W", lba, hex_val])
        print("[Write] Done")

    def read(self, lba: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))

        ssd_file_path = os.path.join(script_dir, "ssd.py")
        subprocess.run(["python", ssd_file_path, "R", lba])

        output_file_path = os.path.join(script_dir, "ssd_output.txt")
        with open(output_file_path, "r") as f:
            read_value = f.read().strip()

        print(f"[Read] LBA {lba.zfill(2)} : {read_value}")
        return read_value

    def full_read(self):
        for lba in range(100):
            self.read(str(lba))

    def full_write(self, hex_val: str):
        for lba in range(100):
            self.write(str(lba), hex_val)
