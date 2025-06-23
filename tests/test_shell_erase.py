import io
import sys

import pytest
from pytest_mock import MockerFixture

from src.command import EraseCommand, ScriptCommand
from src.constants import INVALID_COMMAND, MAX_ERASE_SIZE, TestScriptType
from src.ssd_controller import SSDController
from src.ssd_shell import SSDShell
from src.utils.helpers import adjust_lba_and_count, normalize_lba_range


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


def test_ERASE_인자개수안맞을떄(mocker: MockerFixture, shell):
    wrong_input_command = ["erase 1 3 5", "erase", "erase 5"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    result = _do_run_and_get_result_from_buffer(shell).strip()
    assert expected in result


def test_ERASE_인자개수는올바르지만_LBA주소가유효하지않음(mocker: MockerFixture, shell):
    wrong_input_command = ["erase -1 100", "erase 100 100", "erase aa 100"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    result = _do_run_and_get_result_from_buffer(shell).strip()
    assert expected in result


def test_ERASE_인자개수올바르지만_SIZE가정수가아님(mocker: MockerFixture, shell):
    wrong_input_command = ["erase 1 1.5", "erase 1 aaa"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    result = _do_run_and_get_result_from_buffer(shell).strip()
    assert expected in result


def _check_erase_commands_format(lba, mock_subprocess, shell, total):
    num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)
    _do_run_and_get_result_from_buffer(shell)
    for i in range(num_cmds):
        if total < MAX_ERASE_SIZE:
            size = total
            total = 0
        else:
            size = MAX_ERASE_SIZE
            total -= MAX_ERASE_SIZE
        expected_cmd = ["python", "ssd.py", "E", f"{lba}", f"{size}"]
        actual_call = mock_subprocess.call_args_list[i]
        actual_args = actual_call.args[0]
        assert actual_args == expected_cmd, f"LBA {i} 에서 명령어 불일치: {actual_args}"
        lba += MAX_ERASE_SIZE


@pytest.fixture
def mock_subprocess(mocker: MockerFixture):
    return mocker.patch("src.ssd_controller.subprocess.run")


@pytest.mark.parametrize("start,size", [(3, 5), (3, 10)])
def test_ERASE_명령어정합성_기본(
    mocker: MockerFixture, mock_subprocess, shell, start, size
):
    # arrange
    mocker.patch("builtins.input", return_value=f"erase {start} {size}")
    lba = int(start)
    total = int(size)

    # act and assert
    _check_erase_commands_format(lba, mock_subprocess, shell, total)


def _get_lba_total_with_minus_size(size, start):
    lba = int(start) + (int(size) if int(size) < 0 else 0)
    total = abs(int(size))
    return lba, total


@pytest.mark.parametrize("start,size,lba,total", [(3, -2, 2, 2)])
def test_ERASE_명령어정합성_음수크기(
    mocker: MockerFixture, mock_subprocess, shell, start, size, lba, total
):
    # arrange
    mocker.patch("builtins.input", return_value=f"erase {start} {size}")

    # act and assert
    _check_erase_commands_format(lba, mock_subprocess, shell, total)


@pytest.mark.parametrize(
    "start,size,lba,total", [(1, -2, 0, 2), (2, -5, 0, 3), (98, 5, 98, 2)]
)
# @pytest.mark.parametrize("start,size,lba,total", [(98, 5, 98, 2)])
def test_ERASE_명령어정합성_바운더리(
    mocker: MockerFixture, mock_subprocess, shell, start, size, lba, total
):
    # arrange
    mocker.patch("builtins.input", return_value=f"erase {start} {size}")

    # act and assert
    _check_erase_commands_format(lba, mock_subprocess, shell, total)


def test_ERASERANGE_인자개수안맞을때(mocker: MockerFixture, shell):
    wrong_input_command = ["erase_range", "erase_range 1 5 3"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    result = _do_run_and_get_result_from_buffer(shell).strip()
    assert expected in result


def test_ERASERANGE_인자개수는올바르지만_LBA주소가유효하지않음(
    mocker: MockerFixture, shell
):
    wrong_input_command = [
        "erase_range 3.5 123.5",
        "erase_range 1 aaa",
        "erase_range aaa 10",
        "erase_range aaa bbb",
    ]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    result = _do_run_and_get_result_from_buffer(shell).strip()
    assert expected in result


def test_ERASE_AND_WRITE_AGING_정상_WRITE_60번_ERASERANGE_30번(mocker: MockerFixture):
    # Arrange
    mocker.patch("builtins.input", return_value=TestScriptType.ERASE_AND_AGING.value)
    mock_receiver = mocker.Mock(spec=SSDController)
    shell = SSDShell(receiver=mock_receiver)

    mock_read_compare = mocker.patch("src.command_script._read_compare")
    mock_read_compare.return_value = True
    shell.run()
    # act and assert
    assert mock_receiver.write.call_count == 60
    assert mock_receiver.erase.call_count == 30


def test_ERASE_AND_WRITE_AGING_바로실패_WRITE_2번_ERASERANGE_1번(mocker: MockerFixture):
    # Arrange
    mocker.patch("builtins.input", return_value=TestScriptType.ERASE_AND_AGING.value)
    mock_receiver = mocker.Mock(spec=SSDController)
    shell = SSDShell(receiver=mock_receiver)

    mock_read_compare = mocker.patch("src.command_script._read_compare")
    mock_read_compare.return_value = False
    shell.run()
    # act and assert
    assert mock_receiver.write.call_count == 2
    assert mock_receiver.erase.call_count == 1


@pytest.mark.parametrize("start, end", [(3, 5), (3, 20), (20, 3)])
def test_ERASERANGE_명령어정합성_기본(
    mocker: MockerFixture, mock_subprocess, shell, start, end
):
    # arrange
    mocker.patch("builtins.input", return_value=f"erase_range {start} {end}")
    lba_1 = int(start)
    lba_2 = int(end)
    lba = lba_1 if lba_1 < lba_2 else lba_2
    end_lba = lba_1 if lba_1 > lba_2 else lba_2
    total = end_lba - lba + 1

    # act and assert
    _check_erase_commands_format(lba, mock_subprocess, shell, total)


@pytest.mark.parametrize(
    "start_lba, size, expected",
    [
        (80, 100, (80, 20)),
        (0, 100, (0, 100)),
        (50, -1, (50, 1)),
        (50, -10, (41, 10)),
        (10, -20, (0, 11)),
    ],
)
def test_ERASE_LBA_SIZE조정하는헬퍼함수검증(start_lba, size, expected):
    result = adjust_lba_and_count(start_lba, size)
    assert result == expected


@pytest.mark.parametrize(
    "start_lba, end_lba, expected",
    [
        (30, 35, (30, 6)),
        (40, 20, (20, 21)),
        (99, 99, (99, 1)),
    ],
)
def test_ERASERANGE_두LBA로부터_시작LBA_SIZE도출하는헬퍼함수검증(
    start_lba, end_lba, expected
):
    result = normalize_lba_range(start_lba, end_lba)
    assert result == expected
