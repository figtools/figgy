# -*- mode: python ; coding: utf-8 -*-

import wcwidth
import os
import platform

# Plaform Constants
LINUX = "Linux"
MAC = "Darwin"
WINDOWS = "Windows"

block_cipher = None
cwd = os.getcwd()
mac_hidden = ['configparser', 'keyrings', 'keyring.backends', 'pkg_resources.py2_warn']
linux_hidden = ['configparser', 'keyrings', 'keyring.backends', 'pkg_resources.py2_warn']
windows_hidden = ['configparser', 'pyreadline', 'win32timezone', 'keyrings', 'pkg_resources.py2_warn', 'keyring.backends']


if platform.system() == MAC:
    hidden_imports = mac_hidden
elif platform.system() == LINUX:
    hidden_imports = linux_hidden
elif platform.system() == WINDOWS:
    hidden_imports = windows_hidden


a = Analysis(['figcli/__main__.py'],
             pathex=[cwd],
             binaries=[],
             datas=[(os.path.dirname(wcwidth.__file__), 'wcwidth')],
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='__main__',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='__main__')


