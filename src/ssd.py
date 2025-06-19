import sys
import re
import os
from ssd_file_manager import SSDFileManager


class SSD:
    def __init__(self):
        self.select_file_manager(SSDFileManager())

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

        #optimazing
        fast_read_value = self.fast_read(address)
        if fast_read_value != '':
            return fast_read_value

        nand = self.ssd_file_manager.read_ssd_nand()
        value = nand[address]
        self.ssd_file_manager.print_ssd_output(value)
        return value

    def flush(self):
        print('flush done')

    def write(self, address=-1, value="ERROR"):
        if not self._is_valid_lba(address) or not self._is_valid_value(value):
            self.ssd_file_manager.print_ssd_output("ERROR")
            return "ERROR"

        # optimizing
        buffer_list = self.get_buffer()
        if len(buffer_list) == 5:
            self.flush()
        else:
            self.optimization()
        self.insert_command(self.get_buffer(), f'w_{address}_{value}')

        # 얘는 flush에 들어가야 되는 부분
        # nand = self.ssd_file_manager.read_ssd_nand()
        # nand[address] = value
        # self.ssd_file_manager.patch_ssd_nand(nand)

        return value

    def get_buffer(self):
        # return ['1_e_1_3', '2_e_2_5', '3_w_3_0x00000001', '4_e_4_8', '5_e_6_10']
        # return ['1_e_18_3', '2_w_21_0x12341234', '3_e_18_5', '4_empty', '5_empty']
        return ['1_w_20_0xABCDABCD', '2_w_21_0x12341234', '3_w_20_0xEEEEFFFF', '4_empty', '5_empty']

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

        for lba in range(address, address + size):
            self.write(lba, "0x00000000")
        return "OK"


    def update_buffer(self, command_list):
        print('update done, list : ', command_list)

    def fast_read(self, address):
        buffer = self.get_buffer()
        result = self.process_commands_in_order(buffer)
        return result[address] # 만약에 fast_read값이 없으면 '' return

    def optimization(self):
        buffer = self.get_buffer()
        result = self.process_commands_in_order(buffer)
        result_cmd = self.buffer_to_commands(result)
        print(result_cmd)
        self.update_buffer(result)

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
            if op == 'e':
                count = int(val_str)
                for i in range(addr, min(addr + count, 100)):
                    buffer_memory[i] = '0x00000000'
            elif op == 'w':
                buffer_memory[addr] = val_str
        return buffer_memory

    def buffer_to_commands(self, buffer):
        commands = []
        i = 0
        size = len(buffer)
        while i < size:
            val = buffer[i]
            prefix = 1
            if val == '0x00000000':
                start = i
                count = 0
                while i < size and buffer[i] == '0x00000000' and count < 10:
                    count += 1
                    i += 1
                commands.append(f"{prefix}_e_{start}_{count}")
                prefix += 1

            elif val != '':
                commands.append(f"{prefix}_w_{i}_{val}")
                prefix += 1
                i += 1
            else:
                i += 1
        return commands

    def insert_command(self, command_list, command_string):
        for i, cmd in enumerate(command_list):
            if cmd.endswith("empty"):
                prefix = cmd.split('_')[0]
                new_cmd = f"{prefix}_{command_string}"
                command_list[i] = new_cmd
                break
        self.update_buffer(command_list)

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

    elif command == "F":
        pass
        ## Flush

    else:
        ssd.ssd_file_manager.print_ssd_output("ERROR")

if __name__ == "__main__":
    main()
