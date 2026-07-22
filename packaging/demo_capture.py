"""데모 GIF용 프레임 캡처. Windows py -3.12 + offscreen으로 실제 앱을 구동해 찍는다.

실사진(A/B)을 build/demo/corpus 로 복사해 쓰므로 저장소 원본·결과를 건드리지 않는다.
"""
import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.name == "nt":
    # Windows offscreen 플랫폼은 폰트 폴더를 스스로 찾지 못한다 — 지정해야 글자가 나온다.
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication, QFrame  # noqa: E402

from colorsortgui.qt.mainwindow import MainWindow    # noqa: E402
from colorsortgui.qt.theme import qss                # noqa: E402

DEMO = ROOT / "build" / "demo"
FRAMES = DEMO / "frames"


def _pump(app, n=20):
    for _ in range(n):
        app.processEvents()


def _grab(app, w, name):
    _pump(app)
    w.grab().save(str(FRAMES / f"{name}.png"))
    print("frame", name)


def main() -> int:
    corpus = DEMO / "corpus"
    if corpus.exists():
        shutil.rmtree(corpus)
    skip = shutil.ignore_patterns("results")
    shutil.copytree(ROOT / "A", corpus / "A", ignore=skip)
    shutil.copytree(ROOT / "B", corpus / "B", ignore=skip)
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()

    app = QApplication([])
    w = MainWindow(lang="ko", settings={})
    w.resize(1480, 920)
    w.show()
    _pump(app)
    w._rescale()                                   # 실제 비례 배율(1.5) 상태로 찍는다
    _pump(app)
    _grab(app, w, "01-start")

    w.open_folder(corpus)                          # 분류 (동기 완료)
    _pump(app, 60)
    w._pool.waitForDone(120000)                    # 썸네일 전부
    _pump(app, 60)
    _grab(app, w, "02-sorted")

    w.set_tab("review")
    _grab(app, w, "03-review")

    idx = next(i for i, it in enumerate(w._items) if it.path.name == "4-blue.png")
    w._open_detail(w.grid.item(idx))
    _pump(app, 30)
    w.detail.set_view_mode("original")
    _grab(app, w, "04-original")
    w.detail.set_view_mode("corrected")
    _grab(app, w, "05-corrected")
    w.detail.set_view_mode("judgment")
    _grab(app, w, "06-judgment")

    ridx = next(i for i, it in enumerate(w._items)
                if it.effective_sub.startswith("review"))
    w._current = w._items[ridx]
    w._set_human("BLUE")                           # corpus 사본만 이동한다
    w.set_tab("all")
    _pump(app, 30)
    _grab(app, w, "07-confirmed")

    print("frames:", len(list(FRAMES.glob("*.png"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
