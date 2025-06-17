import pytest

class test_Read와Write_예외경우:
def test_Read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가():
    pass

def test_Read명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가():
    pass

def test_Read명령어_기록한적없는_LBA_읽을시_0x00000000으로_읽는가():
    pass

def test_Write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수를_한번_호출하는가():
    pass

def test_Write명령어_잘못된_LBA범위_입력시_파일매니저의_출력하는함수_인자에_ERROR를_전달하는가():
    pass

def test_Read명령어_LBA주소가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_LBA주소가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_Value가_입력되지않은경우에도_종료되지않고_정상실행되는가():
    pass

def test_Write명령어_Value가_올바르지않은경우_파일매니저의_패치함수를_호출하지않아야한다():
    pass