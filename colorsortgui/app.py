"""부팅: 설정 → (첫 실행이면) 언어 대화상자 → 테마 → 메인 윈도우.
--selftest: 화면 없이 가짜 사진 3장을 분류해 exe가 온전한지 스스로 검사한다."""
import sys
import tempfile
from pathlib import Path


def _selftest() -> int:
    import numpy as np
    from PIL import Image
    from colorsortgui.project import apply_copies, open_project
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name, g, b in (("b.png", 0, 200), ("g.png", 200, 0), ("dark.png", 0, 0)):
            arr = np.zeros((8, 8, 3), dtype=np.uint8)
            arr[..., 1] = g; arr[..., 2] = b
            Image.fromarray(arr).save(root / name)
        state = open_project(root, root / "results")
        copied, errors = apply_copies(state)
        c = state.counts()
        assert (c["blue"], c["green"], c["no-signal"]) == (1, 1, 1), c
        assert copied == 3 and not errors
    print("SELFTEST OK")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()

    from PySide6.QtWidgets import QApplication
    from colorsortgui.i18n import DEFAULT_LANG
    from colorsortgui.settings import load_settings, save_settings
    from colorsortgui.qt.langdialog import LanguageDialog
    from colorsortgui.qt.mainwindow import MainWindow
    from colorsortgui.qt.theme import QSS

    app = QApplication(argv)
    app.setApplicationName("Colorsort")
    # 첫 실행의 언어 대화상자도 테마를 입어야 하므로 대화상자보다 먼저 적용한다.
    app.setStyleSheet(QSS)
    settings = load_settings()
    lang = settings.get("lang")
    if lang not in ("en", "ko"):
        dlg = LanguageDialog()
        dlg.exec()
        lang = dlg.selected() or DEFAULT_LANG
        settings["lang"] = lang
        save_settings(settings)
    win = MainWindow(lang=lang, settings=settings)
    win.show()
    code = app.exec()
    save_settings(settings)          # 종료 시 창 geometry 등 창 상태를 디스크에 남긴다
    return code
