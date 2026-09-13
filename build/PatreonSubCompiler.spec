"""PyInstaller build definition for the standalone Windows app."""
from pathlib import Path


project_root = Path(SPECPATH).parent.parent
a = Analysis(
    [str(project_root / "src" / "Run.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[
        (str(project_root / "data"), "data"),
        (str(project_root / "LICENSE"), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PatreonSubCompiler",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
