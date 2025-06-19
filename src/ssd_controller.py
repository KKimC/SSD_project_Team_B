import os
import subprocess


class SSDController:
    def write(self, lba_address: str, hex_val: str):
        result = subprocess.run(
            ["python", "ssd.py", "W", lba_address, hex_val],
            capture_output=True,
            text=True,
        )

    def read(self, lba_address: str):
        env = os.environ.copy()
        env["SUBPROCESS_CALL"] = "1"  # subprocess 호출임을 알림

        result = subprocess.run(
            ["python", "ssd.py", "R", lba_address],
            capture_output=True,
            text=True,
            env=env,
        )
        read_value = result.stdout

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

