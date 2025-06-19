import random


def generate_random_hex() -> str:
    value = random.randint(0, 0xFFFFFFFF)  # 32비트 범위 (8자리)
    return f"0x{value:08X}"  # 대문자, 0으로 패딩


def adjust_lba_and_count(start_lba: int, size: int) -> tuple[int, int]:
    """
    start_lba: 기준 LBA (0~max_lba)
    size:     양수면 오른쪽 크기, 음수면 왼쪽 크기
    returns:  (adjusted_start_lba, count)
    """
    max_lba = 99
    if size == 0:
        return start_lba, 0

    if size > 0:
        adjusted_size = min(size, max_lba - start_lba + 1)
        return start_lba, adjusted_size

    # size < 0
    end_lba = max(0, start_lba + size + 1)  # +1 because end is inclusive
    count = start_lba - end_lba + 1
    return end_lba, count


def normalize_lba_range(lba1: int, lba2: int) -> tuple[int, int]:
    """
    두 LBA 값에서 시작 LBA와 개수(total count)를 반환합니다.

    Args:
        lba1 (int): 첫 번째 LBA 값
        lba2 (int): 두 번째 LBA 값

    Returns:
        tuple[int, int]: (adjusted_start_lba, total_count)
    """
    start = min(lba1, lba2)
    end = max(lba1, lba2)
    total = end - start + 1
    return start, total
