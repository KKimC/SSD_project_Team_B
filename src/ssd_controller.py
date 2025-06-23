import os
import subprocess


class SSDController:
    def write(self, lba: str, hex_val: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))

        ssd_file_path = os.path.join(script_dir, "ssd.py")
        subprocess.run(["python", ssd_file_path, "W", lba, hex_val])

    def read(self, lba: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))

        ssd_file_path = os.path.join(script_dir, "ssd.py")
        subprocess.run(["python", ssd_file_path, "R", lba])

        output_file_path = os.path.join(script_dir, "ssd_output.txt")
        with open(output_file_path, "r") as f:
            read_value = f.read().strip()

        return read_value

    def erase(self, lba: str, size: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ssd_file_path = os.path.join(script_dir, "ssd.py")

        subprocess.run(["python", ssd_file_path, "E", lba, size])

    def flush(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ssd_file_path = os.path.join(script_dir, "ssd.py")
        subprocess.run(["python", ssd_file_path, "F"])
