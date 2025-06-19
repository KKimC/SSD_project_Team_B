import os
import functools
import glob
from datetime import datetime


class Logger:
    LOG_DIR = "../logs"
    LATEST_LOG = "latest.log"
    MAX_SIZE = 10 * 1024  # 10KB

    def __init__(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        self.log_path = os.path.join(self.LOG_DIR, self.LATEST_LOG)

    def _rotate_log_if_needed(self):
        # 2. latest.log 파일이 10KB 초과되면 회전
        if (
            os.path.exists(self.log_path)
            and os.path.getsize(self.log_path) > self.MAX_SIZE
        ):
            # 3. until_날짜_시간.log 이름으로 변경
            now = datetime.now()
            timestamp = now.strftime("until_%y%m%d_%Hh_%Mm_%Ss")
            rotated_name = f"{timestamp}.log"
            rotated_path = os.path.join(self.LOG_DIR, rotated_name)
            os.rename(self.log_path, rotated_path)

        # 4. until_*.log 파일이 2개 이상이면 가장 오래된 것을 압축 (5. 파일명만 변경)
        log_files = glob.glob(os.path.join(self.LOG_DIR, "until_*.log"))
        if len(log_files) >= 2:
            # 생성 시간 기준 정렬
            log_files.sort(key=lambda f: os.path.getctime(f))
            oldest = log_files[0]
            zip_path = oldest.replace(".log", ".zip")

            # 5. 실제 압축 없이 파일명만 변경 (이미 .zip 이면 생략)
            if not os.path.exists(zip_path) and oldest.endswith(".log"):
                os.rename(oldest, zip_path)

    def _write_to_file(self, text: str):
        self._rotate_log_if_needed()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def print(self, func_name: str, message: str):
        timestamp = datetime.now().strftime("[%y.%m.%d %H:%M]")
        left = f"{timestamp} {func_name}"
        aligned = f"{left:<45}: {message}"  # 좌측 정렬, 총 45칸 맞춤
        print(aligned)
        self._write_to_file(aligned)

    def log_decorator(self, message):  # message 받으려면 두번감싸야함
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = f"{func.__qualname__}()"
                self.print(func_name, message)
                # 예외 처리 원할 경우 아래 주석 해제
                # try:
                #     result = func(*args, **kwargs)
                #     self.print(func_name, "성공적으로 종료됨")
                #     return result
                # except Exception as e:
                #     self.print(func_name, f" 예외 발생 - {e}")
                #     raise

            return wrapper

        return decorator
