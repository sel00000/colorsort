# 빌드는 Windows 파이썬 3.12로 한다 (PySide6 휠 지원 범위 — 이탈 D4·리스크표 참조).
# 실행: py -3.12 -m PyInstaller packaging\colorsort.spec --noconfirm
a = Analysis(
    ["../colorsortgui/__main__.py"],
    pathex=[".."],
    datas=[],
    hiddenimports=[],
    excludes=["tkinter", "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick",
              "PySide6.QtWebEngineCore", "PySide6.Qt3DCore"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="Colorsort",
    console=False,                # 검은 창 금지 — GUI 전용
    icon="colorsort.ico",
    upx=False,                    # UPX는 백신 오탐을 늘린다
    onefile=True,
)
