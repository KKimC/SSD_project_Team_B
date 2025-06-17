import pytest
from ssd import SSD
from file_manager import FileManager

def test_ssd_객체_선언_후_처음_read할때_0이_반환되는가():
    pass

def test_read가_output에_제대로_된_값을_전달하는가():
    pass

def test_read가_제대로_된_값을_리턴하는가():
    pass

def test_write시_file_manager의_patch가_호출되는가():
    pass

def test_write시_file_manager의_print_ssd_output에_제대로_된_값이_들어가는가():
    pass

def test_write시_nand에_제대로_된_값이_들어가는가():
    pass

def test_Read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가(mocker: MockerFixture):
    file_manager: FileManager = mocker.Mock(spec=FileManager)
    ssd: SSD = SSD()
    WRONG_LBA_ADDRESS = 101
    ssd.Read(WRONG_LBA_ADDRESS)

    file_manager.print_ssd_output.assert_called_once()


def test_Read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가(mocker: MockerFixture):
    file_manager: FileManager = mocker.Mock(spec=FileManager)
    ssd: SSD = SSD()
    WRONG_LBA_ADDRESS = 101
    ssd.Read(WRONG_LBA_ADDRESS)

    file_manager.print_ssd_output.assert_called_once_with("ERROR")


def test_Read명령어_기록한적없는_LBA_읽을시_0x00000000으로_읽는가():
    ssd = SSD()
    UNWRITTEN_LBA_ADDRESS = 5
    result = ssd.Read(UNWRITTEN_LBA_ADDRESS)

    assert result == 0x00000000

def test_Write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가(mocker: MockerFixture):
    file_manager: FileManager = mocker.Mock(spec=FileManager)
    ssd: SSD = SSD()
    WRONG_LBA_ADDRESS = 101
    WRITE_VAlUE = 0x00000000
    ssd.Write(WRONG_LBA_ADDRESS, WRITE_VAlUE)

    file_manager.print_ssd_output.assert_called_once()

def test_Write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가(mocker: MockerFixture):
    file_manager: FileManager = mocker.Mock(spec=FileManager)
    ssd: SSD = SSD()
    WRONG_LBA_ADDRESS = 101
    WRITE_VAlUE = 0x00000000
    ssd.Write(WRONG_LBA_ADDRESS, WRITE_VAlUE)

    file_manager.print_ssd_output.assert_called_once_with("ERROR")

def test_Read명령어_LBA주소가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_LBA주소가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_Value가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_Value가_올바르지않은경우_파일매니저의_패치함수를_호출하지않아야한다():
    pass