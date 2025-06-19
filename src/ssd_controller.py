import os
import subprocess

from src.constants import MAX_ERASE_SIZE


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
        print(f"[Erase] LBA {lba.zfill(2)}, size:{size}")

    def eraserange(self, _lba_1: str, _lba_2: str):
        lba_1, lba_2 = int(_lba_1), int(_lba_2)
        lba = lba_1 if lba_1 < lba_2 else lba_2
        end_lba = lba_1 if lba_1 > lba_2 else lba_2
        total = end_lba - lba + 1
        num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)
        for i in range(num_cmds):
            if total < MAX_ERASE_SIZE:
                size = total
                total = 0
            else:
                size = MAX_ERASE_SIZE
                total -= MAX_ERASE_SIZE
            result = subprocess.run(
                ["python", "ssd.py", "E", f"{lba}", f"{size}"],
                capture_output=True,
                text=True,
            )
            lba += MAX_ERASE_SIZE
        print("[eraserange] Done")
