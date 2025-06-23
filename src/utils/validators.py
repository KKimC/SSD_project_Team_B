import re


def is_int(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_valid_lba_address(string: str) -> bool:
    if is_int(string):
        num = int(string)
        return 0 <= num <= 99
    return False


def is_valid_8char_hex(write_value_str: str) -> bool:
    return bool(re.fullmatch(r"0x[0-9a-fA-F]{8}", write_value_str))


def is_right_script_name(command_str: str, script_name: str):
    return re.match(r"\d+_", command_str) and command_str in script_name
