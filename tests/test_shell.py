import io
import re
import sys
import pytest
from pytest_mock import MockerFixture

from src.ssd_shell import SSDShell
from src.command import FullWriteAndReadCompareCommand

INVALID_COMMAND = "INVALID COMMAND"


def _do_run_and_get_result_from_buffer(shell):
    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    # Act
    shell.run()
    sys.stdout = original_stdout
    return captured_output.getvalue()


@pytest.fixture
def shell():
    return SSDShell()


def test_READ_명령어유효성검사_유효하지않은명령어(mocker: MockerFixture, shell):
    wrong_input_command = ["reead 3"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_READ_명령어유효성검사_누락(mocker: MockerFixture, shell):
    wrong_input_command = ["3"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_READ_LBA유효성검사_누락(mocker: MockerFixture, shell):
    wrong_input_command = ["read"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_READ_LBA유효성검사_100초과(mocker: MockerFixture, shell):
    wrong_input_command = ["read 999"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_READ_LBA유효성검사_음수(mocker: MockerFixture, shell):
    wrong_input_command = ["read -1"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_READ_LBA유효성검사_정수가아님(mocker: MockerFixture, shell):
    wrong_input_command = ["read abc"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_READ_SSD에서_값을_읽어오는가(mocker: MockerFixture, shell):
    pass


def test_READ_Console에_값을_출력하는가(mocker: MockerFixture, shell):
    # ex) Shell> read 3
    # [READ] LBA 03 : 0x00000000
    pass


def test_READ_비어있는_LBA에서_읽은값이_0x00000000인가(mocker: MockerFixture, shell):
    # ex) Shell> read 3
    # 0x00000000
    pass


def test_READ_txt파일이_없을때_읽은값이_0x00000000인가(mocker: MockerFixture, shell):
    # ex) Shell> read 3
    # 0x00000000
    pass


def test_READ_정상적인_값을_출력하는가(mocker: MockerFixture, shell):
    # ex) Shell> read 3
    # 0x00000000
    pass


def test_WRITE명령어_누락된인자(mocker: MockerFixture, shell):
    # Arrange
    wrong_input_command = ["write", "write 0xAAAABBBB", "write 3"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_WRITE명령어_유효하지않은인자_INVALID_COMMAND(mocker: MockerFixture, shell):
    # ex) Shell> write -1 0xAAAABBBB
    # INVALID COMMAND
    # Arrange
    mocker.patch("builtins.input", return_value="write -1 0xAAAABBBB")
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_WRITE명령어_유효하지않은인자_주소_100초과_INVALID_COMMAND(
    mocker: MockerFixture, shell
):
    # ex) Shell> write 200 0xAAAABBBB
    # INVALID COMMAND
    # Arrange
    mocker.patch("builtins.input", return_value="write 200 0xAAAABBBB")
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_WRITE명령어_유효하지않은인자_주소_정수가아님_INVALID_COMMAND(
    mocker: MockerFixture, shell
):
    # ex) Shell> write ABC 0xAAAABBBB
    # INVALID COMMAND
    mocker.patch("builtins.input", return_value="write 1.5 0xAAAABBBB")
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_WRITE명령어_유효하지않은인자_값_INVALID_COMMAND(mocker: MockerFixture, shell):
    wrong_input_command = [
        "write 3 xxAAAABBBB",  # 0x가 없는경우
        "write 3 AAAABBBB12",
        "write 3 0xXXXXYYYY",  # 허용되지 않는 문자 포함
        "write 3 0xXQWEdf12",
        "write 3 0xAAAABBBB11",  # 길이 초과
        "write 3 0x111111111111111111111",
    ]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_WRITE명령어_정상인자_기대되는출력물을만드는가(mocker: MockerFixture, shell):
    # Arrange
    mocker.patch("builtins.input", return_value="write 3 0xAAAABBBB")
    mock_subprocess = mocker.patch("src.command.subprocess.run")

    expected = "[Write] Done"

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()
    mock_subprocess.assert_called_once_with(
        ["python", "ssd.py", "W", "3", "0xAAAABBBB"],
        capture_output=True,
        text=True,
    )


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


def test_EXIT명령어_정상(mocker: MockerFixture, shell):
    # ex.
    # Shell> exit
    # exit.
    # 터미널 종료
    mocker.patch("builtins.input", return_value="exit")

    # act and assert
    shell.run()

    assert shell.is_running == False


def test_EXIT명령어_비정상_기대되는출력(mocker: MockerFixture, shell):
    # ex.
    # Shell> exit aa
    # INVALID COMMAND
    wrong_input_command = [
        "exit aa",
        "exit 123",
        "exit 5 6",
    ]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_공통_명령어_비정상인자_기대되는출력():
    # ex.
    # Shell> asd
    # INVALID COMMAND
    pass


def test_FULLWRITE명령어_정상_기대되는_출력(mocker: MockerFixture, shell):
    # ex.
    # Shell> fullwrite 0xABCDFFFF
    # 모든LBA에 값0xABCDFFF 가 적힌다
    # LBA 0~99까지 반복되며 run_ssd_command가 호출되는지 확인
    mocker.patch("builtins.input", return_value="fullwrite 0xAAAABBBB")
    expected = "[Write] Done"
    mock_subprocess = mocker.patch("src.command.subprocess.run")
    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()
    assert mock_subprocess.call_count == 100


def test_FULLWRITE명령어_비정상_짧은명령어_INVALID_COMMAND(
    mocker: MockerFixture, shell
):
    # ex.
    # Shell> fullwrite 0xABCF
    # INVALID COMMAND
    mocker.patch("builtins.input", return_value="fullwrite 0xABCF")
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_FULLWRITE명령어_비정상인자_0x없음_INVALID_COMMAND(
    mocker: MockerFixture, shell
):
    # ex.
    # Shell> fullwrite ABCF33
    # INVALID COMMAND
    mocker.patch("builtins.input", return_value="fullwrite ABCF33")
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_FULLWRITE명령어_비정상인자_특수문자_INVALID_COMMAND(
    mocker: MockerFixture, shell
):
    # ex.
    # Shell> fullwrite 0x!@#$@@@
    # INVALID COMMAND
    mocker.patch("builtins.input", return_value="fullwrite 0x!@#$@@@")
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_FULLWRITE명령어_비정상인자_공백_INVALID_COMMAND(mocker: MockerFixture, shell):
    # ex.
    # Shell> fullwrite
    # INVALID COMMAND
    mocker.patch("builtins.input", return_value="fullwrite")
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def _is_valid_8char_hex(s):
    return bool(re.fullmatch(r"0x[0-9a-fA-F]{8}", s))


def _make_100_reads():
    list_cmds = []
    for i in range(100):
        list_cmds.append(f"ssd.py R {i}")
    return list_cmds


def test_FULLREAD명령어_정상인자_기대되는_출력(mocker: MockerFixture, shell):
    mocker.patch("builtins.input", return_value="fullread")
    expected_line_num = 100
    arr_response = _do_run_and_get_result_from_buffer(shell).strip().splitlines()
    assert len(arr_response) == expected_line_num

    matched = True
    for response in arr_response:
        if _is_valid_8char_hex(response):
            continue
        matched = False
        break
    assert matched == True


def test_FULLREAD명령어_비정상인자_불필요인자_INVALID_COMMAND(
    mocker: MockerFixture, shell
):
    # ex.
    # Shell> fullread 0xABCFF
    # INVALID COMMAND
    # 뒤에 뭐 있기만 해도 에러나야함
    pass


def test_FULLWRITE_AND_READ_COMPARE_정상_PASS_100번(mocker: MockerFixture, shell):
    # Arrange
    mocker.patch("builtins.input", return_value="1_FullWriteAndReadCompare")
    mock_write = mocker.patch("src.command.WriteCommand")
    mocker.patch.object(
        FullWriteAndReadCompareCommand, "_read_compare", return_value=True
    )
    result = _do_run_and_get_result_from_buffer(shell)
    # act and assert
    assert result.replace("\n", "") == "PASS" * 100
    assert mock_write.call_count == 100


def test_FULLWRITE_AND_READ_COMPARE_실패_FAIL_1번(mocker: MockerFixture, shell):
    # Arrange
    mocker.patch("builtins.input", return_value="1_FullWriteAndReadCompare")
    mock_write = mocker.patch("src.command.WriteCommand")
    mock_read = mocker.patch("src.command.ReadCommand")
    mocker.patch.object(
        FullWriteAndReadCompareCommand, "_read_compare", return_value=False
    )
    result = _do_run_and_get_result_from_buffer(shell)
    # act and assert
    assert result.replace("\n", "") == "FAIL"
    assert mock_write.call_count == 1
