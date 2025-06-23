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
        env = os.environ.copy()
        env["SUBPROCESS_CALL"] = "1"  # subprocess 호출임을 알림

        result = subprocess.run(
            ["python", "ssd.py", "E", lba, size],
            capture_output=True,
            text=True,
            env=env,
        )
        read_value = result.stdout
      
    def flush(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ssd_file_path = os.path.join(script_dir, "ssd.py")
        subprocess.run(["python", ssd_file_path, "F"])

