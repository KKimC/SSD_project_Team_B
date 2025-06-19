import io
import sys

import pytest
from pytest_mock import MockerFixture

from src.command import EraseCommand
from src.constants import INVALID_COMMAND, MAX_ERASE_SIZE
from src.ssd_shell import SSDShell


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
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_ERASE_인자개수는올바르지만_LBA주소가유효하지않음(mocker: MockerFixture, shell):
    wrong_input_command = ["erase -1 100", "erase 100 100", "erase aa 100"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def test_ERASE_인자개수올바르지만_SIZE가정수가아님(mocker: MockerFixture, shell):
    wrong_input_command = ["erase 1 1.5", "erase 1 aaa"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


def _check_erase_commands_format(lba, mock_subprocess, num_cmds, shell, total):
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
    num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)

    # act and assert
    _check_erase_commands_format(lba, mock_subprocess, num_cmds, shell, total)


@pytest.mark.parametrize("start, size", [(3, -2)])
def test_ERASE_명령어정합성_음수크기(
    mocker: MockerFixture, mock_subprocess, shell, start, size
):
    # arrange
    lba = int(start)
    _size = int(size)
    lba += _size + 1 if _size >= 0 else 0
    total = abs(_size)
    mocker.patch("builtins.input", return_value=f"erase {start} {total}")
    num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)

    # act and assert
    _check_erase_commands_format(lba, mock_subprocess, num_cmds, shell, total)


def test_ERASERANGE_인자개수안맞을때(mocker: MockerFixture, shell):
    wrong_input_command = ["erase_range", "erase_range 1 5 3"]
    mocker.patch("builtins.input", side_effect=wrong_input_command)
    expected = INVALID_COMMAND

    # act and assert
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


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
    assert _do_run_and_get_result_from_buffer(shell).strip() == expected.strip()


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
    num_cmds = int((total + MAX_ERASE_SIZE - 1) / MAX_ERASE_SIZE)

    # act and assert
    _check_erase_commands_format(lba, mock_subprocess, num_cmds, shell, total)
