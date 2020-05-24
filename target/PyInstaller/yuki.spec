# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:\\Users\\hao.long\\yuki\\src\\main\\python\\app.py'],
             pathex=['C:\\Users\\hao.long\\yuki\\target\\PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=['yuki.headers.thumbnail', 'yuki.headers.duration', 'yuki.headers.fps', 'yuki.headers.resolution', 'yuki.headers.frame_range'],
             hookspath=['c:\\users\\hao.long\\yuki\\venv\\lib\\site-packages\\fbs\\freeze\\hooks'],
             runtime_hooks=['C:\\Users\\hao.long\\yuki\\target\\PyInstaller\\fbs_pyinstaller_hook.py'],
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
          name='yuki',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True , icon='C:\\Users\\hao.long\\yuki\\src\\main\\icons\\Icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='yuki')
