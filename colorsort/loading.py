"""이미지 읽기. 이 모듈만 파일 시스템에서 이미지를 읽는다.

두 가지 함정을 여기서 막는다.
1. 팔레트 색인은 밝기가 아니다 -> 반드시 .convert("RGB")
2. 투명 픽셀은 검정으로 합성되어 '배경'으로 둔갑한다 -> 실제 사용 여부를 탐지
"""

from pathlib import Path

import numpy as np
from PIL import Image

from .models import LoadResult, Msg

_EMPTY = np.zeros((0, 0, 3), dtype=np.int32)


def _transparent_indices(info: dict) -> set[int]:
    """tRNS 정보에서 '완전 불투명이 아닌' 팔레트 색인 집합을 뽑는다."""
    t = info.get("transparency")
    if t is None:
        return set()
    if isinstance(t, int):
        return {t}
    if isinstance(t, (bytes, bytearray)):
        return {i for i, alpha in enumerate(t) if alpha < 255}
    return set()


def load_image(path: Path) -> LoadResult:
    """사진 한 장을 읽는다. PNG·JPG·BMP·GIF·WEBP 등 PIL이 여는 형식이면 무엇이든 된다.

    팔레트·투명도는 PNG 계열에만 있는 개념이라, JPG처럼 없는 형식은 아래 두 분기를
    자연히 지나쳐 곧장 RGB 변환으로 간다. 실패해도 예외를 던지지 않고 load_error에
    담아 반환한다.
    """
    path = Path(path)
    try:
        file_bytes = path.stat().st_size
    except OSError as exc:
        return LoadResult(path, _EMPTY, 0, 0, 0, False, None,
                          Msg("reason.load_error", {"error": str(exc)}))

    try:
        with Image.open(path) as img:
            img.load()
            mode = img.mode
            palette = img.getpalette()
            palette_size = len(palette) // 3 if palette else None

            has_transparent = False
            transparent = _transparent_indices(img.info)
            if transparent and mode == "P":
                # 선언만 된 것과 실제로 쓰인 것을 구분한다.
                # 실제 데이터 196장 중 191장이 '선언만' 이므로 이 구분이 없으면 대부분 오탐이 된다.
                used = set(np.unique(np.asarray(img)).tolist())
                has_transparent = bool(used & transparent)
            elif mode in ("RGBA", "LA"):
                alpha = np.asarray(img.getchannel("A"))
                has_transparent = bool((alpha < 255).any())

            # 팔레트 색인은 밝기가 아니다. 반드시 RGB로 변환해서 읽는다.
            rgb = np.asarray(img.convert("RGB")).astype(np.int32)
            height, width = rgb.shape[0], rgb.shape[1]
    except Exception as exc:  # 손상된 파일 하나가 전체 실행을 멈추면 안 된다
        return LoadResult(path, _EMPTY, 0, 0, file_bytes, False, None,
                          Msg("reason.load_error", {"error": str(exc)}))

    return LoadResult(
        path=path,
        rgb=rgb,
        width=width,
        height=height,
        file_bytes=file_bytes,
        has_transparent_pixels=has_transparent,
        palette_size=palette_size,
        load_error=None,
    )
