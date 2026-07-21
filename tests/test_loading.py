from pathlib import Path

import numpy as np
from PIL import Image

from colorsort.loading import load_image


def _make_palette_png(tmp_path: Path, name: str, palette_rgb, pixel_indices, size,
                      transparency=None) -> Path:
    """팔레트 PNG를 정확히 통제해서 만든다."""
    img = Image.new("P", size)
    flat = []
    for rgb in palette_rgb:
        flat.extend(rgb)
    flat.extend([0, 0, 0] * (256 - len(palette_rgb)))
    img.putpalette(flat)
    img.putdata(pixel_indices)
    p = tmp_path / name
    if transparency is None:
        img.save(p)
    else:
        img.save(p, transparency=transparency)
    return p


def test_palette_index_is_not_brightness(tmp_path):
    """색인 0이 밝고 색인 1이 검정인 팔레트. 색인을 그대로 읽으면 밝기가 거꾸로 나온다."""
    p = _make_palette_png(
        tmp_path, "trap.png",
        palette_rgb=[(0, 0, 19), (0, 0, 0)],   # index 0 = 밝은 파랑, index 1 = 검정
        pixel_indices=[0, 0, 1, 1],
        size=(2, 2),
    )

    # 함정: 색인을 그대로 읽으면 밝은 픽셀이 0, 어두운 픽셀이 1로 뒤집힌다
    raw_indices = np.asarray(Image.open(p))
    assert raw_indices.sum() == 2, "색인 합은 밝기와 무관하다 (이것이 함정)"

    # 로더는 올바르게 처리해야 한다
    result = load_image(p)
    assert result.rgb.shape == (2, 2, 3)
    assert result.rgb[..., 2].max() == 19, "파랑 최댓값이 19여야 한다"
    assert int((result.rgb.sum(axis=2) > 0).sum()) == 2, "밝은 픽셀이 2개여야 한다"


def test_detects_actually_used_transparency(tmp_path):
    """투명 픽셀이 실제로 쓰이면 탐지해야 한다. convert('RGB')는 이를 검정으로 합성해버린다."""
    p = _make_palette_png(
        tmp_path, "transparent.png",
        palette_rgb=[(0, 0, 0), (0, 30, 5)],
        pixel_indices=[1, 1, 0, 0],
        size=(2, 2),
        transparency=1,          # 밝은 초록 색인을 투명으로 지정
    )
    result = load_image(p)
    assert result.has_transparent_pixels is True


def test_declared_but_unused_transparency_is_not_flagged(tmp_path):
    """투명도가 선언만 되고 실제로 쓰이지 않으면 플래그를 세우지 않는다.

    실제 데이터 196장 중 191장이 이 경우다. 여기서 플래그를 세우면 대부분이 오탐이 된다.
    """
    p = _make_palette_png(
        tmp_path, "declared_only.png",
        palette_rgb=[(0, 0, 0), (0, 30, 5), (0, 0, 0)],
        pixel_indices=[1, 1, 0, 0],   # 색인 2를 아무도 쓰지 않음
        size=(2, 2),
        transparency=2,               # 그 안 쓰이는 색인을 투명으로 지정
    )
    result = load_image(p)
    assert result.has_transparent_pixels is False


def test_records_file_size_and_dimensions(tmp_path):
    p = _make_palette_png(
        tmp_path, "meta.png",
        palette_rgb=[(0, 0, 0), (0, 0, 17)],
        pixel_indices=[0, 1] * 8,
        size=(4, 4),
    )
    result = load_image(p)
    assert result.width == 4
    assert result.height == 4
    assert result.file_bytes == p.stat().st_size
    assert result.file_bytes > 0
    assert result.palette_size is not None


def test_unreadable_file_returns_error_not_exception(tmp_path):
    """읽을 수 없는 파일에서 예외를 던지지 않는다. 한 장 때문에 전체가 멈추면 안 된다."""
    p = tmp_path / "broken.png"
    p.write_bytes(b"this is not a png")
    result = load_image(p)
    assert result.load_error is not None
    assert result.load_error.key == "reason.load_error"
    assert result.rgb.size == 0


def test_rgb_dtype_is_int32(tmp_path):
    """uint8이면 뺄셈에서 음수가 감기고, float이면 느리다. int32로 고정한다."""
    p = _make_palette_png(
        tmp_path, "dtype.png",
        palette_rgb=[(0, 0, 0), (0, 0, 17)],
        pixel_indices=[0, 1, 0, 1],
        size=(2, 2),
    )
    assert load_image(p).rgb.dtype == np.int32
