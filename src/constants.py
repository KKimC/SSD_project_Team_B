from enum import Enum


class TestScriptType(Enum):
    FULL_WRITE_AND_READ = "1_FullWriteAndReadCompare"
    PARTIAL_LBA_WRITE = "2_PartialLBAWrite"
    WRITE_READ_AGING = "3_WriteReadAging"
    ERASE_AND_AGING = "4_EraseAndWriteAging"


EMPTY_VALUE = "0x00000000"
INVALID_COMMAND = "INVALID COMMAND"
HELP_TEXT = """
AUTHOR
    비긴어게인 팀 제작자: 김성현, 강태윤, 임동혁, 김남민, 김기웅, 정보람, 김민규

NAME
    Test Shell - SSD 가상 장치 테스트용 커맨드 라인 셸

SYNOPSIS
    write [LBA] [VALUE]
    read [LBA]
    fullwrite [VALUE]
    fullread
    help
    exit

DESCRIPTION

    write
        지정한 LBA 주소에 값을 기록합니다.
        사용법: write [LBA 번호] [저장할 값]
        예시:  write 3 0xAAAABBBB

    read
        지정한 LBA 주소에서 값을 읽어 출력합니다.
        사용법: read [LBA 번호]
        예시:  read 3

    fullwrite
        전체 LBA(0~99)에 동일한 값을 기록합니다.
        사용법: fullwrite [저장할 값]
        예시:  fullwrite 0xABCDFFFF

    fullread
        전체 LBA(0~99)에서 값을 읽어 순차적으로 출력합니다.
        사용법: fullread

    help
        명령어 목록 및 설명과 제작자 정보를 출력합니다.
        사용법: help

    exit
        Test Shell을 종료합니다.
        사용법: exit"""
