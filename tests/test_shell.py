import io
import re
import sys
import pytest
from pytest_mock import MockerFixture
from src.ssd_shell import SsdShell


def test_READ_명령어유효성검사_유효하지않은명령어():
    sut = SsdShell()
    command = "reead 3"
    ret = sut.run(command)

    assert ret == "INVALID COMMAND"


def test_READ_명령어유효성검사_누락():
    sut = SsdShell()
    command = "3"
    ret = sut.run_read(command)

    assert ret == "INVALID COMMAND"


def test_READ_LBA유효성검사_누락():
    # ex) Shell> read
    # INVALID COMMAND
    pass


def test_READ_LBA유효성검사_100초과():
    # ex) Shell> read 999
    # INVALID COMMAND
    pass


def test_READ_LBA유효성검사_음수():
    # ex) Shell> read -1
    # INVALID COMMAND
    pass


def test_READ_LBA유효성검사_정수가아님():
    # ex) Shell> read ABD
    # INVALID COMMAND
    pass


def test_READ_SSD에서_값을_읽어오는가():
    pass


def test_READ_Console에_값을_출력하는가():
    # ex) Shell> read 3
    # [READ] LBA 03 : 0x00000000
    pass


def test_READ_비어있는_LBA에서_읽은값이_0x00000000인가():
    # ex) Shell> read 3
    # 0x00000000
    pass


def test_READ_txt파일이_없을때_읽은값이_0x00000000인가():
    # ex) Shell> read 3
    # 0x00000000
    pass


def test_READ_정상적인_값을_출력하는가():
    # ex) Shell> read 3
    # 0x00000000
    pass


def test_WRITE명령어_정상인자_시스템콜명령어를잘만드는가():
    pass


def test_WRITE명령어_시스템콜명령어를잘만드는가():

    # ex. ssd.py write 3 0xAAAABBBB 의 CLI 명령어를 잘 만드는지
    pass


def test_WRITE명령어_누락된인자(mocker: MockerFixture):
    # Arrange
    wrong_input_command = ["write", "write 0xAAAABBBB", "write 3"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)

    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    expected = "INVALID COMMAND"
    shell = SsdShell()
    # Act
    shell.run()
    sys.stdout = original_stdout
    output = captured_output.getvalue()
    # Assert
    assert output.strip() == expected.strip()


def test_WRITE명령어_유효하지않은인자_INVALID_COMMAND(mocker: MockerFixture):
    # ex) Shell> write -1 0xAAAABBBB
    # INVALID COMMAND
    # Arrange
    mocker.patch("builtins.input", return_value="write -1 0xAAAABBBB")

    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    expected = "INVALID COMMAND"
    shell = SsdShell()
    # Act
    shell.run()
    sys.stdout = original_stdout
    output = captured_output.getvalue()
    # Assert
    assert output.strip() == expected.strip()


def test_WRITE명령어_유효하지않은인자_주소_100초과_INVALID_COMMAND(
    mocker: MockerFixture,
):
    # ex) Shell> write 200 0xAAAABBBB
    # INVALID COMMAND
    # Arrange
    mocker.patch("builtins.input", return_value="write 200 0xAAAABBBB")

    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    expected = "INVALID COMMAND"
    shell = SsdShell()
    # Act
    shell.run()
    sys.stdout = original_stdout
    output = captured_output.getvalue()
    # Assert
    assert output.strip() == expected.strip()


def test_WRITE명령어_유효하지않은인자_주소_정수가아님_INVALID_COMMAND(
    mocker: MockerFixture,
):
    # ex) Shell> write ABC 0xAAAABBBB
    # INVALID COMMAND
    mocker.patch("builtins.input", return_value="write 1.5 0xAAAABBBB")

    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    expected = "INVALID COMMAND"
    shell = SsdShell()
    # Act
    shell.run()
    sys.stdout = original_stdout
    output = captured_output.getvalue()
    # Assert
    assert output.strip() == expected.strip()


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


def test_WRITE명령어_정상인자_기대되는출력물을만드는가(mocker: MockerFixture):
    # ex.
    # Shell> write 3 0xAAAABBBB
    # [Write] Done
    # Arrange
    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    mocker.patch("builtins.input", return_value="write 3 0xAAAABBBB")
    shell = SsdShell()

    expected = "[Write] Done"
    # Act
    shell.run()
    sys.stdout = original_stdout
    output = captured_output.getvalue()

    # Assert
    assert output.strip() == expected.strip()


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


def _is_valid_8char_hex(s):
    return bool(re.fullmatch(r"0x[0-9a-fA-F]{8}", s))


def _make_100_reads():
    list_cmds = []
    for i in range(100):
        list_cmds.append(f"ssd.py R {i}")
    return list_cmds


# @pytest.mark.skip
def test_FULLREAD명령어_정상인자_기대되는_출력(mocker: MockerFixture):
    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    mocker.patch("builtins.input", return_value="fullread")

    # override make_commmand
    fullread_method = mocker.patch("ssd.shell.SsdShell.make_command")
    fullread_method.side_effect = _make_100_reads

    shell = SsdShell()

    expected_line_num = 100
    # Act
    shell.run()
    sys.stdout = original_stdout
    output = captured_output.getvalue()

    # Assert
    arr_response = output.strip().splitlines()
    assert len(arr_response) == expected_line_num
    matched = True
    for response in arr_response:
        if _is_valid_8char_hex(response):
            matched = False
            break
    assert matched == True


def test_FULLREAD명령어_비정상인자_불필요인자_INVALID_COMMAND():
    # ex.
    # Shell> fullread 0xABCFF
    # INVALID COMMAND
    # 뒤에 뭐 있기만 해도 에러나야함
    pass
