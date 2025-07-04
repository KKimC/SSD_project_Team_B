import os.path
import shutil

import pytest
import sys
import src.ssd
from src.ssd import SSD, Flush
from src.ssd_file_manager import SSDFileManager
import re

WRONG_LBA_ADDRESS = 101
VALID_LBA_ADDRESS = 10
VALID_WRITE_VAlUE = "0x00000000"
INVALID_WRITE_VALUE = "0400000000"


@pytest.fixture
def ssd_file_manager_mk(mocker):
    ssd_file_manager_mk = mocker.Mock(spec=SSDFileManager)
    return ssd_file_manager_mk


@pytest.fixture
def ssd_sut(ssd_file_manager_mk):
    ssd_sut = SSD()
    ssd_sut.select_file_manager(ssd_file_manager_mk)
    ssd_sut.flush_handler = Flush(ssd_file_manager_mk)
    ssd_sut.update_buffer(["1_empty", "2_empty", "3_empty", "4_empty", "5_empty"])
    return ssd_sut


class SSDChecker:
    def __init__(self):
        self.test_nand = [0 for _ in range(100)]
        self.expected_nand = [0 for _ in range(100)]

    def check_optimization(self, test_buffer, expected_buffer):
        self.flush(test_buffer, self.test_nand)
        self.flush(expected_buffer, self.expected_nand)
        for i in range(100):
            if self.test_nand[i] != self.expected_nand[i]:
                print(
                    i,
                    "self.test_nand[i]",
                    self.test_nand[i],
                    "self.expected_nand[i]",
                    self.expected_nand[i],
                )
                return False
        else:
            return True

    def flush(self, buffer_list, nand):
        for entry in buffer_list:
            parts = entry.split("_")
            if len(parts) < 2:  # empty case
                continue

            cmd = parts[1]
            if cmd == "W" and len(parts) == 4:
                address = int(parts[2])
                value = parts[3]
                nand[address] = value

            elif cmd == "E" and len(parts) == 4:
                address = int(parts[2])
                size = int(parts[3])
                for lba in range(address, address + size):
                    nand[lba] = "0x00000000"


def test_ssd_객체_선언_후_처음_read할때_0이_반환되는가(ssd_file_manager_mk, ssd_sut):
    ssd_file_manager_mk.read_ssd_nand.return_value = ["0x00000000" for _ in range(100)]
    assert ssd_sut.read(0) == "0x00000000"
    assert ssd_sut.read(10) == "0x00000000"
    assert ssd_sut.read(99) == "0x00000000"


def test_read가_output에_제대로_된_값을_전달하는가(ssd_file_manager_mk, ssd_sut):
    fake_nand = ["0x00000000" for _ in range(100)]
    fake_nand[1] = "0x00000001"
    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand
    ssd_sut.read(1)
    ssd_file_manager_mk.print_ssd_output.assert_called_with("0x00000001")


def test_read가_제대로_된_값을_리턴하는가(ssd_file_manager_mk, ssd_sut):
    fake_nand = ["0x00000000" for _ in range(100)]
    fake_nand[1] = "0x00000001"
    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand
    assert ssd_sut.read(1) == "0x00000001"


def test_write시_정상적인경우_file_manager의_print_ssd_output함수는_한번도_호출되면_안된다(
    ssd_file_manager_mk, ssd_sut
):
    fake_nand = ["0x00000000" for _ in range(100)]
    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand
    ssd_sut.write(1, "0x00000001")
    ssd_file_manager_mk.print_ssd_output.assert_not_called()


def test_read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가(
    ssd_file_manager_mk, ssd_sut
):
    ssd_sut.read(WRONG_LBA_ADDRESS)

    ssd_file_manager_mk.print_ssd_output.assert_called_once()


def test_read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    ssd_sut.read(WRONG_LBA_ADDRESS)

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_read명령어_기록한적없는_LBA_읽을시_0x00000000으로_읽는가(
    ssd_file_manager_mk, ssd_sut
):
    UNWRITTEN_LBA_ADDRESS = 4
    fake_nand = ["0x00000000" for _ in range(100)]
    fake_nand[1] = "0x00040001"
    fake_nand[2] = "0x00040001"

    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand
    result = ssd_sut.read(UNWRITTEN_LBA_ADDRESS)

    assert result == "0x00000000"
    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("0x00000000")


def test_write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가(
    ssd_file_manager_mk, ssd_sut
):
    ssd_sut.write(WRONG_LBA_ADDRESS, VALID_WRITE_VAlUE)

    ssd_file_manager_mk.print_ssd_output.assert_called_once()


def test_write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    ssd_sut.write(WRONG_LBA_ADDRESS, VALID_WRITE_VAlUE)

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_read명령어_LBA주소가_입력되지않은경우에도_정상실행되며_출력하는함수_인자에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    try:
        ssd_sut.read()
    except Exception as e:
        pytest.fail()

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_write명령어_value가_입력되지않은경우에도_정상실행되며_출력하는함수_인자에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    try:
        ssd_sut.write(VALID_LBA_ADDRESS)
    except Exception as e:
        pytest.fail()

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_write명령어에_인자가_없는경우에도_정상실행되며_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    try:
        ssd_sut.write()
    except Exception as e:
        pytest.fail()

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_write명령어_Value가_올바르지않은경우_파일매니저의_패치함수를_호출하지않아야한다(
    ssd_file_manager_mk, ssd_sut
):
    ssd_sut.write(VALID_LBA_ADDRESS, INVALID_WRITE_VALUE)

    ssd_file_manager_mk.patch_ssd_nand.assert_not_called()


def test_ssd모듈의_read함수는_cmd에서_R명령어로_정상적으로_실행되어야한다(mocker):
    test_args = ["ssd.py", "R", "2"]
    mocker.patch("sys.argv", test_args)
    ssd_read_mock = mocker.patch("src.ssd.SSD.read")
    src.ssd.main()

    ssd_read_mock.assert_called_once_with(2)


def test_ssd모듈의_write함수는_cmd에서_W명령어로_정상적으로_실행되어야한다(mocker):
    test_args = ["ssd.py", "W", "2", "0xAAAABBBB"]
    mocker.patch("sys.argv", test_args)
    ssd_write_mock = mocker.patch("src.ssd.SSD.write")
    src.ssd.main()

    ssd_write_mock.assert_called_once_with(2, "0xAAAABBBB")


def test_update_buffer_후_get_buffer_실행시_기대했던_값으로_명령어를_받아올_수_있는가(
    ssd_sut,
):
    expected_cmds = [
        "1_W_1_0x12345678",
        "2_W_2_0x12345677",
        "3_W_3_0x12345676",
        "4_E_1_10",
        "5_E_11_20",
    ]

    ssd_sut.update_buffer(expected_cmds)
    result = ssd_sut.get_buffer()
    assert result == expected_cmds


def test_erase명령어_잘못된LBA주소_입력시_print_ssd_output함수를_호출하는가(
    ssd_file_manager_mk, ssd_sut
):
    ssd_sut.erase(WRONG_LBA_ADDRESS)

    ssd_file_manager_mk.print_ssd_output.assert_called()


def test_erase명령어_잘못된LBA주소_입력시_print_ssd_output에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    ssd_sut.erase(WRONG_LBA_ADDRESS)

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_erase명령어_삭제가능한_최대size를_넘으면_print_ssd_output에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    INVALID_ERASE_SIZE = 14
    ssd_sut.erase(VALID_LBA_ADDRESS, INVALID_ERASE_SIZE)

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_erase명령어_valid하지않은_size의_경우_print_ssd_output에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    INVALID_ERASE_SIZE = -1
    ssd_sut.erase(VALID_LBA_ADDRESS, INVALID_ERASE_SIZE)

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_erase명령어는_write명령어에_올바른LBA와_올바른_value0x00000000을_제대로_전달하는가(
    mocker, ssd_file_manager_mk, ssd_sut
):
    ERASE_SIZE = 3
    fake_nand = ["0x00000000" for _ in range(100)]

    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand

    spy_write = mocker.spy(ssd_sut.flush_handler, "flush_write")
    ssd_sut.erase(VALID_LBA_ADDRESS, ERASE_SIZE)
    ssd_sut.flush()

    expected = [
        mocker.call(VALID_LBA_ADDRESS, "0x00000000"),
        mocker.call(VALID_LBA_ADDRESS + 1, "0x00000000"),
        mocker.call(VALID_LBA_ADDRESS + 2, "0x00000000"),
    ]
    spy_write.assert_has_calls(expected, any_order=False)
    assert spy_write.call_count == 3


def test_erase명령어는_올바르지않은_범위인경우_print_ssd_output에_ERROR를_전달하는가(
    ssd_file_manager_mk, ssd_sut
):
    START_LBA_ADDRESS_1 = 98
    ERASE_SIZE_1 = 10

    START_LBA_ADDRESS_2 = 99
    ERASE_SIZE_2 = 1

    fake_nand = ["0x00000000" for _ in range(100)]

    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand

    ssd_sut.erase(START_LBA_ADDRESS_1, ERASE_SIZE_1)
    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")

    ssd_sut.erase(START_LBA_ADDRESS_2, ERASE_SIZE_2)
    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_erase명령어는_size가0인경우_write함수를_호출하지_않는다(
    ssd_file_manager_mk, ssd_sut
):
    START_LBA_ADDRESS = 1
    ERASE_SIZE = 0

    ssd_sut.erase(START_LBA_ADDRESS, ERASE_SIZE)

    ssd_file_manager_mk.print_ssd_output.assert_not_called()


def test_erase명령어는_size가0인경우_print_ssd_output_함수를_호출하지_않는다(
    ssd_file_manager_mk, ssd_sut
):
    START_LBA_ADDRESS = 1
    ERASE_SIZE = 0

    ssd_sut.erase(START_LBA_ADDRESS, ERASE_SIZE)

    ssd_file_manager_mk.print_ssd_output.assert_not_called()


def test_flush는_실행되고나면_update_buffer함수에_empty_다섯개를_리스트로_넘겨줘야한다(
    mocker, ssd_file_manager_mk, ssd_sut
):
    dummy_buffer = ["1_W_20_ABC", "2_E_10_1", "3_empty", "4_empty", "5_empty"]
    mocker.patch.object(ssd_sut, "get_buffer", return_value=dummy_buffer)
    ssd_file_manager_mk.read_ssd_nand.return_value = ["0x00000000"] * 100

    mock_update = mocker.patch.object(ssd_sut, "update_buffer")

    ssd_sut.flush()

    mock_update.assert_called_once_with(
        ["1_empty", "2_empty", "3_empty", "4_empty", "5_empty"]
    )


def test_flush는_실행되면_get_buffer함수를_호출해_버퍼에_담긴_파일_리스트를_받아온다(
    mocker, ssd_file_manager_mk, ssd_sut
):
    mock_get = mocker.patch.object(ssd_sut, "get_buffer", return_value=[])
    ssd_file_manager_mk.read_ssd_nand.return_value = ["0x00000000"] * 100

    ssd_sut.flush()

    mock_get.assert_called_once()


def test_flush는_리스트_순서대로_함수를_수행해야한다(
    mocker, ssd_file_manager_mk, ssd_sut
):
    buffer_list = [
        "1_W_20_ABC",  # 첫 번째는 write
        "2_E_10_1",  # 두 번째는 erase
        "3_empty",
        "4_empty",
        "5_empty",
    ]
    mocker.patch.object(ssd_sut, "get_buffer", return_value=buffer_list)

    fake_nand = ["0x00000000"] * 100
    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand

    calls = []
    mocker.patch.object(
        ssd_sut.flush_handler,
        "flush_write",
        lambda addr, val: calls.append(("W", addr, val)),
    )
    mocker.patch.object(
        ssd_sut.flush_handler,
        "flush_erase",
        lambda addr, cnt: calls.append(("E", addr, cnt)),
    )

    ssd_sut.flush()

    assert calls == [
        ("W", 20, "ABC"),
        ("E", 10, 1),
    ]


def test_flush는_명령어가_W인경우_flush_write함수에_올바른_인자를_전달한다(
    mocker, ssd_file_manager_mk, ssd_sut
):
    buffer_list = ["1_W_20_ABC", "2_empty", "3_empty", "4_empty", "5_empty"]
    mocker.patch.object(ssd_sut, "get_buffer", return_value=buffer_list)

    fake_nand = ["0x00000000" for _ in range(100)]
    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand

    spy_flush_write = mocker.spy(ssd_sut.flush_handler, "flush_write")
    ssd_sut.flush()

    spy_flush_write.assert_called_once_with(20, "ABC")


def test_flush는_명령어가_E인경우_flush_erase함수에_올바른_인자를_전달한다(
    mocker, ssd_file_manager_mk, ssd_sut
):
    buffer_list = ["1_W_20_ABC", "2_E_10_1", "3_empty", "4_empty", "5_empty"]
    mocker.patch.object(ssd_sut, "get_buffer", return_value=buffer_list)

    fake_nand = ["0x00000000"] * 100
    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand

    spy_flush_erase = mocker.spy(ssd_sut.flush_handler, "flush_erase")

    ssd_sut.flush()

    spy_flush_erase.assert_called_once_with(10, 1)


def test_flush_에_들어오는_bufferlist_안이_전부_emtpy_인경우_아무_작업을_수행하지_않는다(
    mocker, ssd_file_manager_mk, ssd_sut
):
    buffer_list = ["1_empty", "2_empty", "3_empty", "4_empty", "5_empty"]
    mocker.patch.object(ssd_sut, "get_buffer", return_value=buffer_list)

    fake_nand = ["0x00000000"] * 100
    ssd_file_manager_mk.read_ssd_nand.return_value = fake_nand

    spy_flush_write = mocker.spy(ssd_sut.flush_handler, "flush_write")
    spy_flush_erase = mocker.spy(ssd_sut.flush_handler, "flush_erase")

    ssd_sut.flush()

    spy_flush_write.assert_not_called()
    spy_flush_erase.assert_not_called()


def test_buffer(mocker):
    test_args = ["ssd.py", "W", "2", "0xAAAABBBB"]
    mocker.patch("sys.argv", test_args)
    ssd = SSD()
    src.ssd.main()
    ssd.flush()


def test_optimization_ignore_compare_nand(mocker, ssd_file_manager_mk, ssd_sut):
    test_buffer = ["1_E_1_2", "2_E_4_1", "3_W_3_0xAAAAAAAA", "4_empty", "5_empty"]
    result_buffer = ["1_E_1_4", "2_W_3_0xAAAAAAAA", "3_empty", "4_empty", "5_empty"]
    # optimized_buffer = [x for x in ssd_sut.optimization(test_buffer) if 'empty' not in x]
    optimized_buffer = ssd_sut.optimization(test_buffer)
    ssd_checker = SSDChecker()
    assert ssd_checker.check_optimization(optimized_buffer, result_buffer) == True


def test_optimization_ignore_compare_command(mocker, ssd_file_manager_mk, ssd_sut):
    test_buffer = ["1_E_1_2", "2_E_4_1", "3_W_3_0xAAAAAAAA", "4_empty", "5_empty"]
    result_buffer = ["1_E_1_4", "2_W_3_0xAAAAAAAA", "3_empty", "4_empty", "5_empty"]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


def test_optimization_ignore_compare_command_overwrite(ssd_file_manager_mk, ssd_sut):
    test_buffer = [
        "1_W_20_0xABCDABCD",
        "2_W_21_0x12341234",
        "3_W_20_0xEEEEFFFF",
        "4_empty",
        "5_empty",
    ]
    result_buffer = [
        "1_W_21_0x12341234",
        "2_W_20_0xEEEEFFFF",
        "3_empty",
        "4_empty",
        "5_empty",
    ]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


def test_optimization_ignore_compare_command_2(ssd_file_manager_mk, ssd_sut):
    test_buffer = [
        "1_E_18_3",
        "2_W_21_0x12341234",
        "3_E_18_5",
        "4_empty",
        "5_empty",
    ]
    result_buffer = [
        "1_E_18_5",
        "2_empty",
        "3_empty",
        "4_empty",
        "5_empty",
    ]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


def test_optimization_merge_erase(ssd_file_manager_mk, ssd_sut):
    test_buffer = [
        "1_W_20_0xABCDABCD",
        "2_E_10_4",
        "3_E_12_3",
        "4_empty",
        "5_empty",
    ]
    result_buffer = [
        "1_W_20_0xABCDABCD",
        "2_E_10_5",
        "3_empty",
        "4_empty",
        "5_empty",
    ]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


def test_optimization_0으로_write_하는경우_nand(mocker, ssd_file_manager_mk, ssd_sut):
    test_buffer = [
        "1_W_1_0x00000000",
        "2_W_2_0x00000000",
        "3_empty",
        "4_empty",
        "5_empty",
    ]
    result_buffer = ["1_E_1_2", "2_empty", "3_empty", "4_empty", "5_empty"]
    # optimized_buffer = [x for x in ssd_sut.optimization(test_buffer) if 'empty' not in x]
    optimized_buffer = ssd_sut.optimization(test_buffer)
    ssd_checker = SSDChecker()
    assert ssd_checker.check_optimization(optimized_buffer, result_buffer) == True


def test_optimization_0으로_write_하는경우_command(
    mocker, ssd_file_manager_mk, ssd_sut
):
    test_buffer = [
        "1_W_1_0x00000000",
        "2_W_2_0x00000000",
        "3_empty",
        "4_empty",
        "5_empty",
    ]
    result_buffer = ["1_E_1_2", "2_empty", "3_empty", "4_empty", "5_empty"]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


def test_optimization_0으로_write_하고_덮어쓰기_nand(
    mocker, ssd_file_manager_mk, ssd_sut
):
    test_buffer = [
        "1_W_1_0x00000000",
        "2_W_2_0x00000000",
        "3_W_1_0x12345678",
        "4_empty",
        "5_empty",
    ]
    result_buffer = ["1_E_2_1", "2_W_1_0x12345678", "3_empty", "4_empty", "5_empty"]
    # optimized_buffer = [x for x in ssd_sut.optimization(test_buffer) if 'empty' not in x]
    optimized_buffer = ssd_sut.optimization(test_buffer)
    ssd_checker = SSDChecker()
    assert ssd_checker.check_optimization(optimized_buffer, result_buffer) == True


def test_optimization_0으로_write_하고_덮어쓰기_command(
    mocker, ssd_file_manager_mk, ssd_sut
):
    test_buffer = [
        "1_W_1_0x00000000",
        "2_W_2_0x00000000",
        "3_W_1_0x12345678",
        "4_empty",
        "5_empty",
    ]
    result_buffer = ["1_E_2_1", "2_W_1_0x12345678", "3_empty", "4_empty", "5_empty"]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


def test_optimization_한번에_erase가능한_범위안에_write_된경우_nand(
    mocker, ssd_file_manager_mk, ssd_sut
):
    test_buffer = [
        "1_W_2_0x12345678",
        "2_E_3_4",
        "3_W_5_0x12345678",
        "4_E_1_4",
        "5_empty",
    ]
    result_buffer = ["1_E_1_6", "2_W_5_0x12345678", "3_empty", "4_empty", "5_empty"]
    # optimized_buffer = [x for x in ssd_sut.optimization(test_buffer) if 'empty' not in x]
    optimized_buffer = ssd_sut.optimization(test_buffer)
    ssd_checker = SSDChecker()
    assert ssd_checker.check_optimization(optimized_buffer, result_buffer) == True


def test_optimization_한번에_erase가능한_범위안에_write_된경우_command(
    mocker, ssd_file_manager_mk, ssd_sut
):
    test_buffer = [
        "1_W_2_0x12345678",
        "2_E_3_4",
        "3_W_5_0x12345678",
        "4_E_1_4",
        "5_empty",
    ]
    result_buffer = ["1_E_1_6", "2_W_5_0x12345678", "3_empty", "4_empty", "5_empty"]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


def test_optimization_write된값이_모두_erase_된경우_nand(
    mocker, ssd_file_manager_mk, ssd_sut
):
    test_buffer = [
        "1_W_0_0x12345678",
        "2_W_1_0x12345678",
        "3_W_2_0x12345678",
        "4_E_0_3",
        "5_empty",
    ]
    result_buffer = ["1_E_0_3", "2_empty", "3_empty", "4_empty", "5_empty"]
    # optimized_buffer = [x for x in ssd_sut.optimization(test_buffer) if 'empty' not in x]
    optimized_buffer = ssd_sut.optimization(test_buffer)
    ssd_checker = SSDChecker()
    assert ssd_checker.check_optimization(optimized_buffer, result_buffer) == True


def test_optimization_write된값이_모두_erase_된경우_command(
    mocker, ssd_file_manager_mk, ssd_sut
):
    test_buffer = [
        "1_W_0_0x12345678",
        "2_W_1_0x12345678",
        "3_W_2_0x12345678",
        "4_E_0_3",
        "5_empty",
    ]
    result_buffer = ["1_E_0_3", "2_empty", "3_empty", "4_empty", "5_empty"]
    optimized_length = len(
        [x for x in ssd_sut.optimization(test_buffer) if "empty" not in x]
    )
    result_length = len([x for x in result_buffer if "empty" not in x])
    assert optimized_length <= result_length


@pytest.mark.parametrize(
    "test_buffer,result_buffer",
    [
        # 1) simple merge of two erases
        (
            ["1_E_10_4", "2_E_12_3", "3_empty", "4_empty", "5_empty"],
            ["1_E_10_5", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 2) merge erases but keep a write
        (
            ["1_W_20_0x12345678", "2_E_10_4", "3_E_12_3", "4_empty", "5_empty"],
            ["1_W_20_0x12345678", "2_E_10_5", "3_empty", "4_empty", "5_empty"],
        ),
        # 3) merge forbidden because union size > 10
        (
            ["1_E_0_7", "2_E_7_8", "3_empty", "4_empty", "5_empty"],
            ["1_E_0_7", "2_E_7_8", "3_empty", "4_empty", "5_empty"],
        ),
        # 4) overlapping erases merge
        (
            ["1_E_5_3", "2_E_7_2", "3_empty", "4_empty", "5_empty"],
            ["1_E_5_4", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 5) chain-merge three erases
        (
            ["1_E_1_2", "2_E_3_4", "3_E_7_3", "4_empty", "5_empty"],
            ["1_E_1_9", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 6) erase-merge + drop overlapping write
        (
            ["1_W_10_0x12345678", "2_E_8_3", "3_E_10_5", "4_empty", "5_empty"],
            ["1_E_8_7", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 7) ignore duplicate writes only
        (
            [
                "1_W_1_0x12345678",
                "2_W_2_0x12345678",
                "3_W_1_0x12345678",
                "4_empty",
                "5_empty",
            ],
            ["1_W_2_0x12345678", "2_W_1_0x12345678", "3_empty", "4_empty", "5_empty"],
        ),
        # 8) merge adjacent erases, no writes
        (
            ["1_E_2_4", "2_E_6_3", "3_empty", "4_empty", "5_empty"],
            ["1_E_2_7", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 9) merge disjoint erases into a single range
        (
            ["1_W_0_0x12345678", "2_E_2_5", "3_W_5_0x12345678", "4_E_7_2", "5_empty"],
            ["1_W_0_0x12345678", "2_E_2_7", "3_W_5_0x12345678", "4_empty", "5_empty"],
        ),
        # 10) capacity=5, both algos: merge erases, keep latest write
        (
            [
                "1_W_1_0x12345678",
                "2_W_2_0x12345678",
                "3_E_1_3",
                "4_E_3_3",
                "5_W_2_0x12345678",
            ],
            ["1_E_1_5", "2_W_2_0x12345678", "3_empty", "4_empty", "5_empty"],
        ),
        # 10-1) same as 10 but last write is 0x00000000
        (
            [
                "1_W_1_0x12345678",
                "2_W_2_0x12345678",
                "3_E_1_3",
                "4_E_3_3",
                "5_W_2_0x00000000",
            ],
            ["1_E_1_5", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 10-2) write then overwrite before erase
        (
            ["1_W_1_0x12345678", "2_W_1_0x00000000", "3_E_1_3", "4_empty", "5_empty"],
            ["1_E_1_3", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 10-3) multiple overwrites, keep last
        (
            [
                "1_W_1_0x00000000",
                "2_W_1_0x00000000",
                "3_W_1_0x00000001",
                "4_empty",
                "5_empty",
            ],
            ["1_W_1_0x00000001", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 11) merge forbidden by size, drop overlapping write
        (
            ["1_E_0_6", "2_E_6_6", "3_W_8_0x12345678", "4_empty", "5_empty"],
            ["1_E_0_8", "2_E_9_3", "3_W_8_0x12345678", "4_empty", "5_empty"],
        ),
        # 12) nested erases merge into the larger one
        (
            ["1_E_4_5", "2_E_5_3", "3_empty", "4_empty", "5_empty"],
            ["1_E_4_5", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 13) overlap+merge erases, drop both writes
        (
            ["1_W_6_0x12345678", "2_E_4_4", "3_W_5_0x12345678", "4_E_6_2", "5_empty"],
            ["1_E_4_4", "2_W_5_0x12345678", "3_empty", "4_empty", "5_empty"],
        ),
        # 14) no-op: single erase and writes far away
        (
            ["1_W_9_0x12345678", "2_E_0_1", "3_W_3_0x12345678", "4_empty", "5_empty"],
            ["1_W_9_0x12345678", "2_E_0_1", "3_W_3_0x12345678", "4_empty", "5_empty"],
        ),
        # 15) boundary merge at high addresses
        (
            ["1_E_95_5", "2_E_99_1", "3_empty", "4_empty", "5_empty"],
            ["1_E_95_5", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 16) boundary disjoint, no merge
        (
            ["1_E_90_10", "2_E_80_5", "3_empty", "4_empty", "5_empty"],
            ["1_E_90_10", "2_E_80_5", "3_empty", "4_empty", "5_empty"],
        ),
        # 17) ignore+boundary merge drop write at 99
        (
            ["1_W_99_0x12345678", "2_E_95_5", "3_E_99_1", "4_empty", "5_empty"],
            ["1_E_95_5", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 18) small boundary merge at end
        (
            ["1_E_97_3", "2_E_98_1", "3_empty", "4_empty", "5_empty"],
            ["1_E_97_3", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 19) all empty
        (
            ["1_empty", "2_empty", "3_empty", "4_empty", "5_empty"],
            ["1_empty", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
        # 20) all writes to same LBA, keep last
        (
            [
                "1_W_42_0xAAAAAAAA",
                "2_W_42_0xBBBBBBBB",
                "3_W_42_0xCCCCCCCC",
                "4_W_42_0xDDDDDDDD",
                "5_W_42_0xEEEEEEEE",
            ],
            ["1_W_42_0xEEEEEEEE", "2_empty", "3_empty", "4_empty", "5_empty"],
        ),
    ],
)
def test_optimization_test_case_들에_대하여_command_length가_적절하며_nand_결과를_동일하게_만드는지(
    ssd_file_manager_mk, ssd_sut, test_buffer, result_buffer
):
    optimized_buffer = ssd_sut.optimization(test_buffer)
    optimized = [cmd for cmd in ssd_sut.optimization(test_buffer) if "empty" not in cmd]
    optimized_length = len(optimized)
    expected_length = len([cmd for cmd in result_buffer if "empty" not in cmd])

    ssd_checker = SSDChecker()

    assert optimized_length <= expected_length
    assert ssd_checker.check_optimization(optimized_buffer, result_buffer) == True
