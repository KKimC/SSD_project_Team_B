def test_WRITE명령어_시스템콜명령어를잘만드는가():
    # ex. ssd.py write 3 0xAAAABBBB 의 CLI 명령어를 잘 만드는지
    pass

def test_WRITE명령어_정상인자_기대되는출력물을만드는가():
    # ex.
    # Shell> write 3 0xAAAABBBB
    # [Write] Done
    pass

def test_WRITE명령어_누락된인자1_주소_INVALIDCOMMAND():
    # ex) Shell> write 0xAAAABBBB
    # INVALID COMMAND
    pass

def test_WRITE명령어_누락된인자2_값_INVALIDCOMMAND():
    # ex) Shell> write 3
    # INVALID COMMAND
    pass

def test_WRITE명령어_누락된인자_ALL_INVALID_COMMAND():
    # ex) Shell> write
    # INVALID COMMAND
    pass

def test_WRITE명령어_유효하지않은인자_주소_음수_INVALID_COMMAND():
    # ex) Shell> write -1 0xAAAABBBB
    # INVALID COMMAND
    pass
def test_WRITE명령어_유효하지않은인자_주소_100초과_INVALID_COMMAND():
    # ex) Shell> write 200 0xAAAABBBB
    # INVALID COMMAND
    pass

def test_WRITE명령어_유효하지않은인자_주소_정수가아님_INVALID_COMMAND():
    # ex) Shell> write ABC 0xAAAABBBB
    # INVALID COMMAND
    pass

def test_WRITE명령어_유효하지않은인자_값_길이10초과_INVALID_COMMAND():
    # ex) Shell> write 3 0xAAAABBBBCC
    # INVALID COMMAND
    pass
def test_WRITE명령어_유효하지않은인자_값_0x가앞에없음_INVALID_COMMAND():
    # ex) Shell> write 3 AAAABBBB
    # INVALID COMMAND
    pass
def test_WRITE명령어_유효하지않은인자_허용되지않은문자포함_INVALID_COMMAND():
    # ex) Shell> write 3 0xXXXXYYYY
    # INVALID COMMAND
    pass

def test_WRITE명령어_정상동작시_실제로파일에저장되는가():
    pass