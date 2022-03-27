import os
import logging

from ftplib import FTP, error_perm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FTPClient:
    def __init__(self, host: str, port: int, user: str, password: str, path: str):
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.path: str = path

        self.size: int = int()
        self.block: int = int()
        self.last_percent: int = int()

    def upload_progress(self, block):
        self.block += len(block)
        percent = self.block / (self.size * .01)
        if self.last_percent != percent:
            self.last_percent = percent
            logger.debug(f"{self.block} / {self.size} - {self.last_percent:.0f}%")

    def upload(self, file_path: str):
        with FTP() as ftp:
            ftp.connect(self.host, self.port)
            ftp.login(self.user, self.password)

            try:
                ftp.mkd("uploaded")
            except error_perm as e:
                if e.__str__() == "550 File exists.":
                    pass
                else:
                    logger.error(f"MAKE DIR: {e}")
                    return 1

            self.size = os.path.getsize(file_path)
            self.block = 0
            with open(file_path, "rb") as f:
                ftp.storbinary(f"STOR uploaded/{file_path}", f, blocksize=16384, callback=self.upload_progress)
