"""썸네일 디스크 캐시. USB는 느려서 매번 원본을 다시 읽으면 시작이 굼뜨다."""
from pathlib import Path

import numpy as np
from PIL import Image

from colorsort.loading import load_image
from .enhance import auto_view

def get_thumb(cache_dir: Path, source: Path, fp: str, size: int = 144) -> Path:
    out = Path(cache_dir) / fp[:2] / f"{fp}.png"
    if out.exists():
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    rgb = load_image(Path(source)).rgb
    view = auto_view(rgb) if rgb.size else np.zeros((size, size, 3), dtype=np.uint8)
    img = Image.fromarray(view)
    w, h = img.size
    s = min(w, h)
    if s:
        img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    img = img.resize((size, size), Image.LANCZOS)
    tmp = out.with_suffix(".tmp")
    img.save(tmp, format="PNG")
    tmp.replace(out)
    return out
