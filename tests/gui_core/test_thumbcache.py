import numpy as np
from PIL import Image
from colorsortgui.thumbcache import get_thumb

def _png(path, w=64, h=32, b=120):
    arr = np.zeros((h, w, 3), dtype=np.uint8); arr[..., 2] = b
    Image.fromarray(arr).save(path)

def test_creates_square_thumb(tmp_path):
    src = tmp_path / "x.png"; _png(src)
    p = get_thumb(tmp_path / ".thumbs", src, "ab" + "0" * 62, size=32)
    assert p.exists() and p.parent.name == "ab"
    with Image.open(p) as im:
        assert im.size == (32, 32)               # 정사각 중앙 크롭

def test_reuses_existing(tmp_path):
    src = tmp_path / "x.png"; _png(src)
    p1 = get_thumb(tmp_path / ".thumbs", src, "cd" + "0" * 62, size=32)
    first = p1.stat().st_mtime_ns
    p2 = get_thumb(tmp_path / ".thumbs", src, "cd" + "0" * 62, size=32)
    assert p1 == p2 and p2.stat().st_mtime_ns == first   # 두 번째는 재생성 안 함

def test_dark_source_gets_brightened(tmp_path):
    src = tmp_path / "dark.png"; _png(src, b=5)          # peak 5 — 원본은 안 보임
    p = get_thumb(tmp_path / ".thumbs", src, "ef" + "0" * 62, size=16)
    with Image.open(p) as im:
        assert max(im.convert("RGB").getextrema()[2]) >= 200   # 보정돼 밝다
