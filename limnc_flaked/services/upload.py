from typing import List
import pysftp
from .config import config_service


class UploadService:

    def __init__(self):
        self.general_config = config_service.get_config().general

    def upload_files(self, files: List[str], remote_path: str):
        uploaded = []
        try:
            sftp_config = self.general_config.sftp
            remote_folder = sftp_config.prefix + '/' + remote_path
            with pysftp.Connection(sftp_config.host, username=sftp_config.username, password=sftp_config.password, port=sftp_config.port) as sftp:
                print("Connection established.")
                for file in files:
                    remote_file_path = remote_folder + '/' + file.name
                    print(f"Uploading {file} to {remote_file_path}...")
                    # Upload a file
                    sftp.put(file, remote_file_path)
                    uploaded.append(file)
                    print(f"File uploaded to {remote_file_path}.")
        except Exception as e:
            raise e
        return uploaded
