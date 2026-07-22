"""colorsort.ico 생성: 검은 바탕, 왼쪽 초록·오른쪽 파랑의 둥근 사각형."""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).parent

sizes = [16, 24, 32, 48, 64, 128, 256]
imgs = []
for s in sizes:
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = max(2, s // 6)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=(20, 16, 20, 255))
    pad = max(2, s // 8)
    d.rounded_rectangle([pad, pad, s // 2 - 1, s - pad], radius=max(1, r // 2),
                        fill=(84, 205, 146, 255))
    d.rounded_rectangle([s // 2 + 1, pad, s - pad, s - pad], radius=max(1, r // 2),
                        fill=(127, 165, 247, 255))
    imgs.append(im)
imgs[-1].save(HERE / "colorsort.ico", sizes=[(s, s) for s in sizes])
print(f"{HERE / 'colorsort.ico'} written")
