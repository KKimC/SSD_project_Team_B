def test_WRITE명령어_정상인자_시스템콜명령어를잘만드는가():
    # ex. ssd.py write 3 0xAAAABBBB 의 CLI 명령어를 잘 만드는지
    pass

def test_WRITE명령어_정상인자_기대되는출력물을만드는가():
    # ex.
    # Shell> write 3 0xAAAABBBB
    # [Write] Done
    pass

def test_HELP명령어_정상_기대되는출력():
    # ex.
    # Shell> help
    # 제작자: 김성현, 강태윤, 임동혁, 김기웅, 김남민, 정보람, 김민규
    # write command - write 200 0xaaaabbbb ...등등
    pass
def test_HELP명령어_비정상_기대되는출력():
    # ex.
    # Shell> help aa
    # INVALID COMMAND
    pass
def test_EXIT명령어_정상_기대되는출력():
    # ex.
    # Shell> exit
    # exit.
    # 터미널 종료
    pass

def test_EXIT명령어_비정상_기대되는출력():
    # ex.
    # Shell> exit aa
    # INVALID COMMAND
    pass

def test_공통_명령어_비정상인자_기대되는출력():
    # ex.
    # Shell> asd
    # INVALID COMMAND
    pass

def test_FULLWRITE명령어_정상_기대되는_출력():
    # ex.
    # Shell> fullwrite 0xABCDFFFF
    # 모든LBA에 값0xABCDFFF 가 적힌다
    #
    pass
def test_FULLWRITE명령어_비정상_짧은명령어_INVALID_COMMAND():
    # ex.
    # Shell> fullwrite 0xABCF
    # INVALID COMMAND
    pass
def test_FULLWRITE명령어_비정상인자_0x없음_INVALID_COMMAND():
    # ex.
    # Shell> fullwrite ABCF33
    # INVALID COMMAND
    pass
def test_FULLWRITE명령어_비정상인자_특수문자_INVALID_COMMAND():
    # ex.
    # Shell> fullwrite 0x!@#$@@@
    # INVALID COMMAND
    pass
def test_FULLWRITE명령어_비정상인자_공백_INVALID_COMMAND():
    # ex.
    # Shell> fullwrite 
    # INVALID COMMAND
    pass
def test_FULLWRITE명령어_정상인자_실제로파일저장확인():
    # ex.
    # Shell> fullwrite 0xABCDFFFF
    # 모든LBA에 값0xABCDFFF 가 적힌다
    # 전체 일지 확인 가능한지 0~100 0xABCDFFFF
    pass

def test_FULLREAD명령어_정상인자_기대되는_출력():
    # ex.
    # Shell> fullread
    # 모든 값 화면 출력...
    # 0
    # 0xABCDABCD
    # 1
    # 0xABCDABCD
    # 2
    # 0xABCDABCD
    # ... 100까지
    pass
def test_FULLREAD명령어_비정상인자_불필요인자_INVALID_COMMAND():
    # ex.
    # Shell> fullread 0xABCFF
    # INVALID COMMAND
    # 뒤에 뭐 있기만 해도 에러나야함
    pass



