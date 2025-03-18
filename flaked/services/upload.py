from typing import List
from pathlib import Path
import paramiko
from .config import config_service


class UploadService:

    def __init__(self):
        self.sftp = config_service.get_config().settings.sftp

    def upload_files(self, files: List[Path], remote_path: str) -> List[Path]:
        uploaded = []
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())  # Auto accept unknown host keys

        # Connect to the SFTP server
        client.connect(self.sftp.host, self.sftp.port,
                       self.sftp.username, self.sftp.password)

        # Open an SFTP session
        sftp = client.open_sftp()

        # Ensure remote folder exists (create if necessary)
        remote_folder = self.sftp.prefix + '/' + remote_path
        self._mkdirs(sftp, remote_folder)
        try:
            sftp.stat(remote_folder)  # Check if remote folder exists
        except FileNotFoundError:
            sftp.mkdir(remote_folder)  # Create remote folder
            print(f"Created remote folder: {remote_folder}")

        # Upload all files from the local folder
        try:
            for file in files:
                remote_file_path = remote_folder + '/' + file.name
                print(f"Uploading {file} to {remote_file_path}...")
                sftp.put(str(file), remote_file_path)
                print(f"Uploaded: {file} → {remote_path}")
                uploaded.append(file)
        finally:
            # Close connections
            sftp.close()
            client.close()
        return uploaded

    def _mkdirs(self, sftp, remote_folder):
        """ Recursively create directories on the remote SFTP server """
        dirs = remote_folder.strip("/").split("/")
        current_path = ""

        for dir in dirs:
            current_path += f"/{dir}"
            try:
                sftp.stat(current_path)  # Check if directory exists
            except FileNotFoundError:
                sftp.mkdir(current_path)  # Create if it doesn't exist
                print(f"Created remote directory: {current_path}")
