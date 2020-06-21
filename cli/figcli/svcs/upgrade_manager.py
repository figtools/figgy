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

    def install_mac_onedir(self, install_path: str, latest_version: str):
        zip_path = f"{HOME}/.figgy/figgy.zip"
        install_dir = f'{HOME}/.figgy/installations/{latest_version}'
        remote_path = f'http://www.figgy.dev/releases/cli/{latest_version}/darwin/figgy.zip'
        os.makedirs(os.path.dirname(install_dir), exist_ok=True)
        self.download_url(remote_path, zip_path)

        with ZipFile(zip_path, 'r') as zipObj:
            zipObj.extractall(install_dir)

        if self._utils.file_exists(install_path):
            os.remove(install_path)

        executable_path = f'{install_dir}/{CLI_NAME}'
        st = os.stat(executable_path)
        os.chmod(executable_path, st.st_mode | stat.S_IEXEC)
        os.symlink(f'{install_dir}/{CLI_NAME}', install_path)
        print(f'{CLI_NAME} has been installed at path `{install_path}`.')

    def get_install_path(self) -> None:
        """
        Prompts the user to get their local installation path.
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

            install_path = f"{install_path}/{CLI_NAME}{suffix}"

        if not self._utils.file_exists(install_path):
            self._utils.error_exit("Invalid install path specified, try providing the full path to the binary.")

        return install_path
