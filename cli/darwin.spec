# -*- mode: python ; coding: utf-8 -*-

import wcwidth
import os

block_cipher = None


a = Analysis(['figcli/__main__.py'],
             pathex=['/Users/jordanmance/workspace/figgy/figgy/cli'],
             binaries=[],
             datas=[(os.path.dirname(wcwidth.__file__), 'wcwidth')],
             hiddenimports=['configparser', 'keyrings', 'keyring.backends', 'pycryptodome', 'pkg_resources.py2_warn'],
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
