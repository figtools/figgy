# -*- mode: python -*-

block_cipher = None


a = Analysis(['extras/export_credentials.py'],
             pathex=['/Users/jordan.mance/workspace/devops/devops.ci/support'],
             binaries=[],
             datas=[],
             hiddenimports=['configparser'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='export_credentials',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
