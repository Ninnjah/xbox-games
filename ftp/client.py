import os
import pathlib
from pathlib import Path
import logging

from ftplib import FTP, error_perm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FTPClient:
    def __init__(self, host: str, port: int, user: str, password: str, games_dir: Path, host_path: Path):
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.host_path: Path = host_path
        self.games_dir: Path = games_dir

        self.size: int = int()
        self.block: int = int()
        self.last_percent: int = int()

    def get_files(self, ftp: FTP, path: Path, prev_path: Path = Path("")):
        path_name: str = str(path).replace(str(self.games_dir), str(self.host_path))
        files: dict = {path_name: []}
        sum_size: int = int()

        print(path_name)
        try:
            ftp.mkd(path_name)
        except error_perm as e:
            if e.__str__() == "550 File exists.":
                pass
            else:
                logger.error(f"MAKE DIR: {e}")
                return 1

        for obj in path.iterdir():
            if obj.is_file():
                name = str(prev_path / obj.name).replace(str(self.games_dir), "")
                files.get(path_name).append({"name": name, "path": obj})
                sum_size += obj.stat().st_size

                self.size = obj.stat().st_size
                self.block = 0
                with open(obj, "rb") as f:
                    logger.info(f"STOR {str(Path(path_name) / Path(obj.name))}")
                    ftp.storbinary(
                        f"STOR {str(Path(path_name) / Path(obj.name))}", f,
                        blocksize=8192, callback=self.upload_progress
                    )

            else:
                other_dir = self.get_files(ftp, obj, Path(prev_path / Path(path.name)))
                files.get(path_name).append(other_dir[0])
                sum_size += other_dir[1]

        return files, sum_size

    def upload_progress(self, block):
        self.block += len(block)
        percent = round(self.block / (self.size * .01))
        if self.last_percent != percent:
            self.last_percent = percent
            logger.debug(f"{self.block} / {self.size} - {self.last_percent}%")

    def upload(self, file_path: Path, dest_path: str):
        with FTP() as ftp:
            ftp.connect(self.host, self.port)
            ftp.login(self.user, self.password)

            try:
                ftp.mkd(dest_path)
            except error_perm as e:
                if e.__str__() == "550 File exists.":
                    pass
                else:
                    logger.error(f"MAKE DIR: {e}")
                    return 1

            self.size = file_path.stat().st_size
            self.block = 0
            with open(file_path, "rb") as f:
                ftp.storbinary(f"STOR {dest_path}", f, blocksize=16384, callback=self.upload_progress)

    def upload_dir(self):
        with FTP() as ftp:
            ftp.connect(self.host, self.port)
            ftp.login(self.user, self.password)

            for game in self.games_dir.iterdir():
                self.get_files(ftp, game)
