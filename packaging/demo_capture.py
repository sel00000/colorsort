"""데모 캡처 — Windows py -3.12 + offscreen으로 실제 앱을 영어 UI로 구동해 찍는다.

말뭉치는 실행할 때마다 numpy로 **합성**한다(검은 바탕 + 한 색 점 구름).
실제 사진 폴더는 절대 읽지 않는다 — 어떤 프레임에도 실데이터가 담기면 안 된다.
끝나면 frames/*.png 와 데모 GIF(build/demo/colorsort-demo.gif)가 남는다.
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

import numpy as np                                    # noqa: E402
from PIL import Image                                 # noqa: E402
from PySide6.QtWidgets import QApplication, QFrame    # noqa: E402

from colorsortgui.qt.mainwindow import MainWindow     # noqa: E402
from colorsortgui.qt.theme import qss                 # noqa: E402

DEMO = ROOT / "build" / "demo"
FRAMES = DEMO / "frames"
GIF = DEMO / "colorsort-demo.gif"

GREEN, BLUE = 1, 2                                    # RGB 채널 번호


def _synth(path: Path, channel, dots: int, seed: int) -> None:
    """검은 바탕에 한 색의 점 구름을 뿌린 합성 사진. channel=None이면 전부 검정."""
    rng = np.random.default_rng(seed)
    img = np.zeros((480, 640, 3), np.uint8)
    if channel is not None:
        xs = rng.integers(30, 610, dots)
        ys = rng.integers(30, 450, dots)
        for x, y in zip(xs, ys):
            img[y - 1:y + 2, x - 1:x + 2, channel] = int(rng.integers(110, 255))
    Image.fromarray(img).save(path)


def _build_corpus(dst: Path) -> None:
    """sample-01..24(홀수 파랑, 짝수 초록) + sample-25(전부 검정 → review)."""
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for i in range(1, 25):
        _synth(dst / f"sample-{i:02d}.png", BLUE if i % 2 else GREEN,
               dots=1500 + 130 * i, seed=i)
    _synth(dst / "sample-25.png", None, 0, seed=99)


def _pump(app, n=20):
    for _ in range(n):
        app.processEvents()


def _grab(app, w, name):
    _pump(app)
    w.grab().save(str(FRAMES / f"{name}.png"))
    print("frame", name)


def _make_gif() -> None:
    """프레임 7장을 960px 폭으로 줄여 한 장짜리 흐름 GIF로 묶는다."""
    paths = sorted(FRAMES.glob("*.png"))
    frames = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im = im.resize((960, round(im.height * 960 / im.width)), Image.LANCZOS)
        frames.append(im.quantize(colors=128, dither=Image.Dither.NONE))
    durs = {"01": 1600, "02": 2600, "03": 1800, "04": 1800,
            "05": 1800, "06": 2600, "07": 2400}
    durations = [durs.get(p.name[:2], 2000) for p in paths]
    frames[0].save(GIF, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print("gif", GIF, GIF.stat().st_size, "bytes")


def main() -> int:
    corpus = DEMO / "corpus"
    _build_corpus(corpus)
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()

    app = QApplication([])
    w = MainWindow(lang="en", settings={})
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

    idx = next(i for i, it in enumerate(w._items) if it.path.name == "sample-07.png")
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
    w._set_human("BLUE")                           # 합성 말뭉치의 사본만 이동한다
    w.set_tab("all")
    _pump(app, 30)
    _grab(app, w, "07-confirmed")

    print("frames:", len(list(FRAMES.glob("*.png"))))
    _make_gif()
    return 0


if __name__ == "__main__":
    sys.exit(main())
