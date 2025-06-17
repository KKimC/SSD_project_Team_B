import pytest
from ssd import SSD
from file_manager import SSDFileManager

@pytest.fixture
def ssd_file_manager_mk(mocker):
    ssd_file_manager_mk = mocker.Mock(spec=SSDFileManager)
    return ssd_file_manager_mk

@pytest.fixture
def ssd_sut(ssd_file_manager_mk):
    ssd_sut = SSD()
    ssd_sut.select_file_manager(ssd_file_manager_mk)
    return ssd_sut

def test_ssd_객체_선언_후_처음_read할때_0이_반환되는가(ssd_file_manager_mk, ssd_sut):
    assert ssd_sut.read(1) == 0
    assert ssd_sut.read(10) == 0
    assert ssd_sut.read(100) == 0

def test_read가_output에_제대로_된_값을_전달하는가(ssd_file_manager_mk, ssd_sut):
    pass

def test_read가_제대로_된_값을_리턴하는가():
    pass

def test_write시_file_manager의_patch가_호출되는가():
    pass

def test_write시_file_manager의_print_ssd_output에_제대로_된_값이_들어가는가():
    pass

def test_write시_nand에_제대로_된_값이_들어가는가():
    pass

def test_Read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가(ssd_file_manager_mk, ssd_sut):
    WRONG_LBA_ADDRESS = 101
    ssd_sut.Read(WRONG_LBA_ADDRESS)

    ssd_file_manager_mk.print_ssd_output.assert_called_once()


def test_Read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가(ssd_file_manager_mk, ssd_sut):
    WRONG_LBA_ADDRESS = 101
    ssd_sut.Read(WRONG_LBA_ADDRESS)

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")


def test_Read명령어_기록한적없는_LBA_읽을시_0x00000000으로_읽는가(ssd_file_manager_mk, ssd_sut):
    UNWRITTEN_LBA_ADDRESS = 4
    ssd_file_manager_mk.read_ssd_nand.side_effect = [0x00000000, 0x00040001, 0x00040001, 0x00000000, 0x00000000]
    result = ssd_sut.Read(UNWRITTEN_LBA_ADDRESS)

    assert result == 0x00000000

def test_Write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가(ssd_file_manager_mk, ssd_sut):
    WRONG_LBA_ADDRESS = 101
    WRITE_VAlUE = 0x00000000
    ssd_sut.Write(WRONG_LBA_ADDRESS, WRITE_VAlUE)

    ssd_file_manager_mk.print_ssd_output.assert_called_once()

def test_Write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가(ssd_file_manager_mk, ssd_sut):
    WRONG_LBA_ADDRESS = 101
    WRITE_VAlUE = 0x00000000
    ssd_sut.Write(WRONG_LBA_ADDRESS, WRITE_VAlUE)

    ssd_file_manager_mk.print_ssd_output.assert_called_once_with("ERROR")

def test_Read명령어_LBA주소가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_LBA주소가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_Value가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_Value가_올바르지않은경우_파일매니저의_패치함수를_호출하지않아야한다(ssd_file_manager_mk, ssd_sut):
    LBA = 10
    INVALID_VALUE = "0400000000"

    ssd_sut.Write(LBA, INVALID_VALUE)

    ssd_file_manager_mk.patch_ssd_nand.assert_not_called()