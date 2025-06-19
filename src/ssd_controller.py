import os
import subprocess


class SSDController:
    def write(self, lba_address: str, hex_val: str):
        result = subprocess.run(
            ["python", "ssd.py", "W", lba_address, hex_val],
            capture_output=True,
            text=True,
        )
        print("[Write] Done")

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
        print(f"[Read] LBA {lba_address.zfill(2)} : {read_value}")
        return read_value

    def full_read(self):
        for lba_address in range(100):
            self.read(str(lba_address))

    def full_write(self, hex_val: str):
        for lba_address in range(100):
            self.write(str(lba_address), hex_val)
