from enum import Enum


class TestScriptType(Enum):
    FULL_WRITE_AND_READ = "1_FullWriteAndReadCompare"
    PARTIAL_LBA_WRITE = "2_PartialLBAWrite"
    WRITE_READ_AGING = "3_WriteReadAging"
    ERASE_AND_AGING = "4_EraseAndWriteAging"


EMPTY_VALUE = "0x00000000"
INVALID_COMMAND = "INVALID COMMAND"
MAX_ERASE_SIZE = 10
HELP_TEXT = """
AUTHOR
    팀명: 25년 CRA B긴어게인
    제작자(팀원): 김성현, 강태윤, 임동혁, 김남민, 김기웅, 정보람, 김민규

NAME
    Test Shell - SSD 가상 장치 테스트용 커맨드 라인 셸

SYNOPSIS
    write [LBA] [VALUE]
    read [LBA]
    fullwrite [VALUE]
    fullread
    erase [LBA] [SIZE]
    erase_range [START_LBA] [END_LBA]
    flush 
    help
    exit
    TEST 스크립트 수행
    

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

    erase
        지정한 LBA 주소에서 해당하는 SIZE를 삭제합니다.
        사용법: erase [LBA] [SIZE]
        예시: erase 1 5
        
    erase_range
        START_LBA 부터 END_LBA 까지 내용을 삭제한다.
        사용법: erase_range [START_LBA] [END_LBA]
        예시: erase_range 1 23
        
    flush
        Command Buffer 를 Flush 한다
        사용법: flush
        
    help
        명령어 목록 및 설명과 제작자 정보를 출력합니다.
        사용법: help

    exit
        Test Shell을 종료합니다.

        사용법: exit
     
    TEST 스크립트 수행
        과제에 제시된 X(1~4)번 스크립트를 수행한다.    
        사용법: • Test Shell 에서 “X_WriteReadAging” 라고 입력한다.
                • Test Shell 에서 “X_” 만 입력해도 실행 가능하다.
                
        예시: 1_WriteReadAging
             1_
        """



