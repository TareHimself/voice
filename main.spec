# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Taree/PycharmProjects/voice/venv/Lib/site-packages/vosk','./vosk'),
    ('C:/Users/Taree/PycharmProjects/voice/venv/Lib/site-packages/torch','./torch'),
    ('C:/Users/Taree/PycharmProjects/voice/venv/Lib/site-packages/torchaudio','./torchaudio'),
    ('C:/Users/Taree/PycharmProjects/voice/venv/Lib/site-packages/torchvision','./torchvision')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
to_remove = ["_AES", "_ARC4", "_DES", "_DES3", "_SHA256", "_counter","_C","_C_flatbuffer"]
for b in a.binaries:
    found = any(
        f'{crypto}.cp39-win_amd64.pyd' in b[1]
        for crypto in to_remove
    )
    if found:
        print(f"Removing {b[1]}")
        a.binaries.remove(b)


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
