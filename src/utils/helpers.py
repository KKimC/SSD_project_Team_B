import random


def generate_random_hex() -> str:
    value = random.randint(0, 0xFFFFFFFF)  # 32비트 범위 (8자리)
    return f"0x{value:08X}"  # 대문자, 0으로 패딩
