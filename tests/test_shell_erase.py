import io
import sys

import pytest
from pytest_mock import MockerFixture

from src.constants import INVALID_COMMAND
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
