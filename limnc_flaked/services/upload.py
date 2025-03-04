from typing import List
import paramiko
from .config import config_service


class UploadService:

    def __init__(self):
        self.general_config = config_service.get_config().general
        self.sftp_config = self.general_config.sftp

    def upload_files(self, files: List[str], remote_path: str):
        uploaded = []
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())  # Auto accept unknown host keys

        # Connect to the SFTP server
        client.connect(self.sftp_config.host, self.sftp_config.port,
                       self.sftp_config.username, self.sftp_config.password)

        # Open an SFTP session
        sftp = client.open_sftp()

        # Ensure remote folder exists (create if necessary)
        remote_folder = self.sftp_config.prefix + '/' + remote_path
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
