import shutil
import sys
import re
import os
from ssd_file_manager import SSDFileManager
from typing import List


class Flush:
    def __init__(self, file_manager: SSDFileManager):
        self.ssd_file_manager = file_manager

    def flush_write(self, address=-1, value="ERROR"):
        nand = self.ssd_file_manager.read_ssd_nand()
        nand[address] = value
        self.ssd_file_manager.patch_ssd_nand(nand)
        return value

    def flush_erase(self, address=-1, size=-1):
        for lba in range(address, address + size):
            self.flush_write(lba, "0x00000000")
        return "OK"

    def flush(self, buffer_list: List[str]) -> List[str]:
        for entry in buffer_list:
            parts = entry.split('_')
            if len(parts) < 2: # empty case
                continue

            cmd = parts[1]
            if cmd == "W" and len(parts) == 4:
                address = int(parts[2])
                value = parts[3]
                self.flush_write(address, value)

            elif cmd == "E" and len(parts) == 4:
                address = int(parts[2])
                size = int(parts[3])
                self.flush_erase(address, size)

        return [f"{i+1}_empty" for i in range(5)]


class SSD:
    def __init__(self):
        self.select_file_manager(SSDFileManager())
        self.flush_handler = Flush(self.ssd_file_manager)

    def select_file_manager(self, file_manager):
        self.ssd_file_manager = file_manager

    def _is_valid_lba(self, address):
        return isinstance(address, int) and 0 <= address < 100

    def _is_valid_value(self, value):
        return bool(re.fullmatch(r'0x[0-9a-fA-F]{8}', value))

    def read(self, address=-1):
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        # optimazing
        fast_read_value = self.fast_read(address)
        if fast_read_value != '':
            value = fast_read_value
        else:
            nand = self.ssd_file_manager.read_ssd_nand()
            value = nand[address]
            self.ssd_file_manager.print_ssd_output(value)

        return value

    def write(self, address=-1, value="ERROR"):
        if not self._is_valid_lba(address) or not self._is_valid_value(value):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        # optimizing
        buffer_list = [x for x in self.get_buffer() if 'empty' not in x]
        if len(buffer_list) == 5:
            self.flush()
        else:
            self.optimization()
        self.insert_command(self.get_buffer(), f'W_{address}_{value}')

        # 얘는 flush에 들어가야 되는 부분
        # nand = self.ssd_file_manager.read_ssd_nand()
        # nand[address] = value
        # self.ssd_file_manager.patch_ssd_nand(nand)

        return value

    def get_buffer(self) -> List[str]:
        return sorted(os.listdir('buffer'))

    def update_buffer(self, commands: List[str]) -> None:
        if len(commands) != 5:
            return

        buffer_dir = 'buffer'

        if os.path.exists(buffer_dir):
            shutil.rmtree(buffer_dir)
        os.makedirs(buffer_dir, exist_ok=True)

        for idx, command in enumerate(commands[:5], start=1):
            file_path = os.path.join(buffer_dir, f"{idx}_temp")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(command)

            target_path = os.path.join(buffer_dir, command)
            os.replace(file_path, target_path)

    def erase(self, address=-1, size=0):
        MAX_ERASE_SIZE = 10
        if not self._is_valid_lba(address):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        if not isinstance(size, int) or not (0 <= size <= MAX_ERASE_SIZE):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        LAST_LBA = address + size - 1
        if LAST_LBA > 99:
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        # optimizing
        buffer_list = [x for x in self.get_buffer() if 'empty' not in x]
        print(self.get_buffer(), buffer_list)
        if len(buffer_list) == 5:
            self.flush()
        else:
            self.optimization()
        self.insert_command(self.get_buffer(), f'E_{address}_{size}')

        return "OK"

    def flush(self):
        buffer_list = self.get_buffer()
        initialized_buffer = self.flush_handler.flush(buffer_list)
        self.update_buffer(initialized_buffer)

    def fast_read(self, address):
        buffer = self.get_buffer()
        result = self.process_commands_in_order(buffer)
        return result[address] # 만약에 fast_read값이 없으면 '' return

    def optimization(self, buffer=None):
        if buffer is None:
            buffer = self.get_buffer()
        result = self.process_commands_in_order(buffer)
        result_cmd = self.buffer_to_commands(result)
        self.update_buffer(result_cmd)
        return result_cmd

    def process_commands_in_order(self, commands):
        buffer_memory = ['' for _ in range(100)]
        def get_prefix(_cmd):
            return int(_cmd.split('_')[0])
        sorted_cmds = sorted(commands, key=get_prefix)
        for cmd in sorted_cmds:
            parts = cmd.split('_')
            if len(parts) != 4:
                continue
            _, op, addr_str, val_str = parts
            addr = int(addr_str)
            if op == 'E':
                count = int(val_str)
                for i in range(addr, min(addr + count, 100)):
                    buffer_memory[i] = '0x00000000'
            elif op == 'W':
                buffer_memory[addr] = val_str
        return buffer_memory

    def buffer_to_commands(self, buffer):
        commands = []
        i = 0
        prefix = 1
        size = len(buffer)
        while i < size:
            val = buffer[i]
            if val == '0x00000000':
                start = i
                count = 0
                while i < size and buffer[i] != '' and count < 10:
                    count += 1
                    i += 1
                commands.append(f"{prefix}_E_{start}_{count}")
                prefix += 1
            else:
                i += 1
        i = 0
        while i < size:
            val = buffer[i]
            if (val != '0x00000000') and (val != ''):
                commands.append(f"{prefix}_W_{i}_{val}")
                prefix += 1
                i += 1
            else:
                i += 1

        while len(commands) < 5:
            commands.append(f'{prefix}_empty')
            prefix += 1
        return commands

    def insert_command(self, command_list, command_string):
        for i, cmd in enumerate(command_list):
            if cmd.endswith("empty"):
                prefix = cmd.split('_')[0]
                new_cmd = f"{prefix}_{command_string}"
                command_list[i] = new_cmd
                break
        self.update_buffer(command_list)

    def test_write(self, add, val):
        a = self.write(add, val)
        self.flush()
        return a

    def test_read(self):
        return self.read

    def test_erase(self, add, ran):
        a = self.erase(add, ran)
        self.flush()
        return a


def main():
    ssd = SSD()

    if len(sys.argv) < 3:
        print("Usage: python ssd.py R [LBA] or python ssd.py W [LBA] [VALUE]")
        return "ERROR"

    command = sys.argv[1]
    try:
        address = int(sys.argv[2])
    except ValueError:
        ssd.ssd_file_manager.print_ssd_output("ERROR")
        return "ERROR"

    if command == "R" and len(sys.argv) == 3:
        read_result = ssd.read(address)
        if os.getenv("SUBPROCESS_CALL") == "1":
            print(read_result)

    elif command == "W" and len(sys.argv) == 4:
        value = sys.argv[3]
        ssd.write(address, value)

    elif command == "E" and len(sys.argv) == 4:
        size = int(sys.argv[3])
        ssd.erase(address, size)

    elif command == "F" and len(sys.argv) == 1:
        ssd.flush()

    else:
        ssd.ssd_file_manager.print_ssd_output("ERROR")

if __name__ == "__main__":
    main()
