import platform

import boto3

from figcli.extras.s3_download_progress import S3Progress
from figcli.svcs.observability.version_tracker import FiggyVersionDetails, VersionTracker


class UpgradeManager:

    def __init__(self, s3_rsc: boto3.session.Sesseion):
        self.s3 = s3_rsc
        self.current_version: FiggyVersionDetails = VersionTracker.get_version()


    pass

    #
    # def _install_mac_onedir(self, install_path: str, latest_version: str):
    #     s3_path = f'snagcli/{latest_version}/{platform.system().lower()}/snagcli.zip'
    #
    #     try:
    #         total_bytes = self.s3.Object(CLI_BUCKET, s3_path).content_length
    #         progress = S3Progress(total=total_bytes, unit='B', unit_scale=True, miniters=1, desc='Downloading')
    #         bucket = self.get_s3_resource().Bucket(CLI_BUCKET)
    #         zip_path = f"{HOME}/.snag/snagcli.zip"
    #         install_dir = f'{HOME}/.snag/snagcli/version/{latest_version}'
    #
    #         os.makedirs(os.path.dirname(install_dir), exist_ok=True)
    #
    #         with progress:
    #             bucket.download_file(s3_path, zip_path, Callback=progress)
    #
    #         with ZipFile(zip_path, 'r') as zipObj:
    #             zipObj.extractall(install_dir)
    #
    #         if self._utils.file_exists(install_path):
    #             os.remove(install_path)
    #
    #         executable_path = f'{install_dir}/snagcli'
    #         st = os.stat(executable_path)
    #         os.chmod(executable_path, st.st_mode | stat.S_IEXEC)
    #         os.symlink(f'{install_dir}/snagcli', install_path)
    #         print(f'snagcli has been installed at path `{install_path}`.')
    #     except ClientError as e:
    #         if e.response['Error']['Code'] == "404":
    #             print("Unable to find the snagcli in S3. Something went terribly wrong! :(")
    #         else:
    #             raise

    #
    # def _perform_upgrade(self, latest_version: str) -> None:
    #     """
    #     Walks the user through the upgrade path. Supports Windows/Linux/& OSX for Windows we must rename the running
    #     binary to a different name, as we cannot overwrite the existing running binary.
    #     Args:
    #         latest_version: str: The version ot upgrade to, i.e 1.0.6
    #         mgmt_session: Session that may be leveraged for performing the upgrade by downloading the appropriate binary
    #                       from S3.
    #     """
    #     readline.parse_and_bind("tab: complete")
    #     comp = Completer()
    #     readline.set_completer_delims(' \t\n')
    #     readline.parse_and_bind("tab: complete")
    #     readline.set_completer(comp.pathCompleter)
    #     abs_path = os.path.dirname(sys.executable)
    #     install_path = input(f'Input path to your existing installation. Default: {abs_path} : ') or abs_path
    #     suffix = ".exe" if self._utils.is_windows() else ""
    #
    #     if os.path.isdir(install_path):
    #         if install_path.endswith('/'):
    #             install_path = install_path[:-1]
    #
    #         install_path = f"{install_path}/snagcli{suffix}"
    #
    #     if not self._utils.file_exists(install_path):
    #         self._utils.error_exit("Invalid install path specified, try providing the full path to the binary.")
    #
    #     print(f"Install path: {install_path}")
    #     s3_path = f'snagcli/{latest_version}/{platform.system().lower()}/snagcli{suffix}'
    #     print(f"Installing: snagcli/{latest_version}/{platform.system().lower()}/snagcli{suffix}")
    #     print(f"{self.c.fg_bl}Downloading `snagcli` version: {latest_version}{self.c.rs}")
    #
    #     old_path = f'{install_path}.OLD'
    #     temp_path = install_path + "tmp"
    #
    #     if self._utils.file_exists(old_path):
    #         os.remove(old_path)
    #     if self._utils.file_exists(temp_path):
    #         os.remove(temp_path)
    #     if self._utils.file_exists(install_path):
    #         os.rename(install_path, old_path)
    #
    #     try:
    #         total_bytes = self.get_s3_resource().Object(CLI_BUCKET, s3_path).content_length
    #         progress = S3Progress(total=total_bytes, unit='B', unit_scale=True, miniters=1, desc='Downloading')
    #         bucket = self.get_s3_resource().Bucket(CLI_BUCKET)
    #
    #         with progress:
    #             bucket.download_file(s3_path, temp_path, Callback=progress)
    #
    #     except ClientError as e:
    #         if e.response['Error']['Code'] == "404":
    #             print("Unable to find the snagcli in S3. Something went terribly wrong! :(")
    #         else:
    #             raise
    #     else:
    #         st = os.stat(temp_path)
    #         os.chmod(temp_path, st.st_mode | stat.S_IEXEC)
    #         os.rename(temp_path, install_path)
    #         print(f"{self.c.fg_gr}Installation successful! Exiting. Rerun `snagcli` "
    #               f"to use the latest version!{self.c.rs}")
    #         exit()