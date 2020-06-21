import platform
import readline
import urllib.request
import tqdm
import boto3
import os
import stat
import sys

from extras.completer import Completer
from botocore.exceptions import ClientError

from figcli.config import HOME, CLI_NAME
from figcli.extras.s3_download_progress import S3Progress
from figcli.svcs.observability.version_tracker import FiggyVersionDetails, VersionTracker
from figcli.utils.utils import Utils
from zipfile import ZipFile


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


class UpgradeManager:
    def __init__(self, colors_enabled: bool):
        self._utils = Utils(colors_enabled=colors_enabled)
        self.c = Utils.default_colors(enabled=colors_enabled)
        self.current_version: FiggyVersionDetails = VersionTracker.get_version()

    def download_url(self, url, output_path):
        with DownloadProgressBar(unit='B', unit_scale=True,
                                 miniters=1, desc=url.split('/')[-1]) as t:
            urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)

    def _install_mac_onedir(self, install_path: str, latest_version: str):
        s3_path = f'figgy/{latest_version}/{platform.system().lower()}/figgy.zip'
        zip_path = f"{HOME}/.snag/figgy.zip"
        install_dir = f'{HOME}/.snag/figgy/version/{latest_version}'
        remote_path = f'http://www.figgy.dev/releases/cli/{latest_version}/darwin/figgy.zip'
        os.makedirs(os.path.dirname(install_dir), exist_ok=True)
        self.download_url(remote_path, zip_path)

        with ZipFile(zip_path, 'r') as zipObj:
            zipObj.extractall(install_dir)

        if self._utils.file_exists(install_path):
            os.remove(install_path)

        executable_path = f'{install_dir}/figgy'
        st = os.stat(executable_path)
        os.chmod(executable_path, st.st_mode | stat.S_IEXEC)
        os.symlink(f'{install_dir}/figgy', install_path)
        print(f'figgy has been installed at path `{install_path}`.')

    def _perform_upgrade(self, latest_version: str) -> None:
        """
        Walks the user through the upgrade path. Supports Windows/Linux/& OSX for Windows we must rename the running
        binary to a different name, as we cannot overwrite the existing running binary.
        Args:
            latest_version: str: The version ot upgrade to, i.e 1.0.6
            mgmt_session: Session that may be leveraged for performing the upgrade by downloading the appropriate binary
                          from S3.
        """
        readline.parse_and_bind("tab: complete")
        comp = Completer()
        readline.set_completer_delims(' \t\n')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(comp.pathCompleter)
        abs_path = os.path.dirname(sys.executable)
        install_path = input(f'Input path to your existing installation. Default: {abs_path} : ') or abs_path
        suffix = ".exe" if self._utils.is_windows() else ""

        if os.path.isdir(install_path):
            if install_path.endswith('/'):
                install_path = install_path[:-1]

            install_path = f"{install_path}/snagcli{suffix}"

        if not self._utils.file_exists(install_path):
            self._utils.error_exit("Invalid install path specified, try providing the full path to the binary.")

        print(f"Install path: {install_path}")
        print(f"Installing: snagcli/{latest_version}/{platform.system().lower()}/snagcli{suffix}")
        print(f"{self.c.fg_bl}Downloading `snagcli` version: {latest_version}{self.c.rs}")

        old_path = f'{install_path}.OLD'
        temp_path = install_path + "tmp"

        if self._utils.file_exists(old_path):
            os.remove(old_path)
        if self._utils.file_exists(temp_path):
            os.remove(temp_path)
        if self._utils.file_exists(install_path):
            os.rename(install_path, old_path)

        if Utils.is_mac():
            print("Performing auto-upgrade for MAC installation.")
            self._install_mac_onedir(f'{install_path}', latest_version)

            print(f"{self.c.fg_gr}Installation successful! Exiting. Rerun `{CLI_NAME}` "
                  f"to use the latest version!{self.c.rs}")
            exit()
