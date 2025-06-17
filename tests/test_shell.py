def test_READ_명령어유효성검사_유효한명령어():
    # ex) Shell> reead 3
    # INVALID COMMAND
    ...


def test_READ_명령어유효성검사_누락():
    # ex) Shell> 3
    # INVALID COMMAND
    ...


def test_READ_LBA유효성검사_누락():
    # ex) Shell> read
    # INVALID COMMAND
    ...


def test_READ_LBA유효성검사_100초과():
    # ex) Shell> read 999
    # INVALID COMMAND
    ...


def test_READ_LBA유효성검사_음수():
    # ex) Shell> read -1
    # INVALID COMMAND
    ...


def test_READ_LBA유효성검사_정수가아님():
    # ex) Shell> read ABD
    # INVALID COMMAND
    ...


def test_READ_SSD에서_값을_읽어오는가(): ...


def test_READ_Console에_값을_출력하는가():
    # ex) Shell> read 3
    # [READ] LBA 03 : 0x00000000
    ...


def test_READ_비어있는_LBA에서_읽은값이_0x00000000인가():
    # ex) Shell> read 3
    # 0x00000000
    ...


def test_READ_txt파일이_없을때_읽은값이_0x00000000인가():
    # ex) Shell> read 3
    # 0x00000000
    ...


def test_READ_정상적인_값을_출력하는가():
    # ex) Shell> read 3
    # 0x00000000
    ...
