import shutil
import sys
import re
import os
from ssd_file_manager import SSDFileManager
from typing import List

class Optimizer:
    def optimization(self, buffer=None):
        result = self.process_commands_in_order(buffer)
        result_cmd = self.buffer_to_commands(result)
        return result_cmd

    def fast_read(self, buffer, address):
        result = self.process_commands_in_order(buffer)
        return result[address] # 만약에 fast_read값이 없으면 '' return

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
            if val != '':
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
        self.optimizer = Optimizer()

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
        buffer = self.get_buffer()
        fast_read_value = self.optimizer.fast_read(buffer, address)
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

    def insert_command(self, command_list, command_string):
        for i, cmd in enumerate(command_list):
            if cmd.endswith("empty"):
                prefix = cmd.split('_')[0]
                new_cmd = f"{prefix}_{command_string}"
                command_list[i] = new_cmd
                break
        self.update_buffer(command_list)

    def optimization(self, buffer=None):
        if buffer is None:
            buffer = self.get_buffer()
        result_cmd = self.optimizer.optimization(buffer)
        self.update_buffer(result_cmd)
        return result_cmd

class CommandInvoker:
    def __init__(self, ssd):
        self.ssd = ssd

    def execute(self, args: List[str]):
        if not args or len(args) < 2:
            print("Usage: python ssd.py [R|W|E|F] [LBA] [VALUE or SIZE]")
            return "ERROR"

        command = args[1].upper()

        if command == "F" and len(args) == 2:
            return self.ssd.flush()

        if len(args) < 3:
            return self._error()

        try:
            address = int(args[2])
        except ValueError:
            return self._error()

        if command == "R" and len(args) == 3:
            return self.ssd.read(address)

        elif command == "W" and len(args) == 4:
            return self.ssd.write(address, args[3])

        elif command == "E" and len(args) == 4:
            try:
                size = int(args[3])
                return self.ssd.erase(address, size)
            except ValueError:
                return self._error()

        else:
            return self._error()

    def _error(self):
        self.ssd.ssd_file_manager.print_ssd_output("ERROR")
        return "ERROR"


def main():
    ssd = SSD()
    invoker = CommandInvoker(ssd)
    invoker.execute(sys.argv)

if __name__ == "__main__":
    main()
