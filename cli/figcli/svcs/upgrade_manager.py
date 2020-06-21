import os
import readline
import stat
import sys
from urllib.request import urlopen

import requests
from zipfile import ZipFile

import tqdm
from figcli.extras.completer import Completer

from figcli.config import HOME, CLI_NAME
from figcli.svcs.observability.version_tracker import FiggyVersionDetails, VersionTracker
from figcli.utils.utils import Utils

class UpgradeManager:
    def __init__(self, colors_enabled: bool):
        self._utils = Utils(colors_enabled=colors_enabled)
        self.c = Utils.default_colors(enabled=colors_enabled)
        self.current_version: FiggyVersionDetails = VersionTracker.get_version()

    def download_zip(self, remote_path: str, local_path: str):
        eg_link = remote_path
        response = requests.get(eg_link, stream=True)
        with tqdm.wrapattr(open(local_path, "wb"), "write",
                           miniters=1, desc=eg_link.split('/')[-1],
                           total=int(response.headers.get('content-length', 0))) as fout:
            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)

    def download_from_url(self, url, dst):
        """
        @param: url to download file
        @param: dst place to put the file
        """
        file_size = int(urlopen(url).info().get('Content-Length', -1))
        if os.path.exists(dst):
            first_byte = os.path.getsize(dst)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
        pbar = tqdm(
            total=file_size, initial=first_byte,
            unit='B', unit_scale=True, desc=url.split('/')[-1])
        req = requests.get(url, headers=header, stream=True)
        with(open(dst, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
        pbar.close()
        return file_size

    def install_mac_onedir(self, install_path: str, latest_version: str):
        zip_path = f"{HOME}/.figgy/figgy.zip"
        install_dir = f'{HOME}/.figgy/installations/{latest_version}'
        remote_path = f'http://www.figgy.dev/releases/cli/{latest_version}/darwin/figgy.zip'
        os.makedirs(os.path.dirname(install_dir), exist_ok=True)
        self.download_from_url(remote_path, zip_path)

        with ZipFile(zip_path, 'r') as zipObj:
            zipObj.extractall(install_dir)

        if self._utils.file_exists(install_path):
            os.remove(install_path)

        executable_path = f'{install_dir}/{CLI_NAME}'
        st = os.stat(executable_path)
        os.chmod(executable_path, st.st_mode | stat.S_IEXEC)
        os.symlink(f'{install_dir}/{CLI_NAME}', install_path)
        print(f'{CLI_NAME} has been installed at path `{install_path}`.')

    def get_install_path(self) -> str:
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
