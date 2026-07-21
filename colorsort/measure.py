"""픽셀 측정. 순수 함수이며 파일 시스템을 모른다.

핵심 아이디어: 빨강이 0이므로 모든 픽셀을 (초록, 파랑) 두 값의 비율 하나로 압축한다.
    rho = B / (G + B)
초록 LUT은 rho 약 0.154, 파랑 LUT은 정확히 1.0. 두 값이 멀어 경계를 넉넉히 잡을 수 있다.
"""

import numpy as np

from .config import Config
from .models import LoadResult, Measurements


def measure(load: LoadResult, config: Config) -> Measurements:
    """이미지 한 장의 색 구성을 측정한다. 판정은 하지 않는다."""
    rgb = load.rgb
    if rgb.size == 0:
        return Measurements(
            n_pixels=0, max_red=0, peak=0, n_lit_1=0, gate_used=None, n_gated=0,
            n_blue=0, n_green=0, n_intermediate=0, energy_blue=0, energy_green=0,
            file_bytes=load.file_bytes, has_transparent_pixels=load.has_transparent_pixels,
        )

    red = rgb[..., 0]
    green = rgb[..., 1]
    blue = rgb[..., 2]
    intensity = np.maximum(green, blue)

    n_pixels = int(intensity.size)
    max_red = int(red.max())
    peak = int(intensity.max())
    n_lit_1 = int((intensity >= 1).sum())

    # 게이트를 위에서부터 시도하고, 픽셀이 부족하면 완화한다.
    # 완화가 필요했다는 사실 자체가 저신뢰 신호이므로 gate_used에 남긴다.
    gate_used = None
    mask = None
    for gate in config.gates:
        candidate = intensity >= gate
        if int(candidate.sum()) >= config.n_min:
            gate_used = gate
            mask = candidate
            break

    if gate_used is None:
        return Measurements(
            n_pixels=n_pixels, max_red=max_red, peak=peak, n_lit_1=n_lit_1,
            gate_used=None, n_gated=0, n_blue=0, n_green=0, n_intermediate=0,
            energy_blue=0, energy_green=0,
            file_bytes=load.file_bytes, has_transparent_pixels=load.has_transparent_pixels,
        )

    g = green[mask]
    b = blue[mask]
    i = intensity[mask]

    # 게이트를 통과했으므로 max(G,B) >= 1, 따라서 G+B >= 1 이고 0으로 나눌 일은 없다.
    # 그래도 방어적으로 where를 쓴다.
    denom = (g + b).astype(np.float64)
    rho = np.divide(b, denom, out=np.zeros_like(denom), where=denom > 0)

    is_blue = rho >= config.rho_blue
    is_green = rho <= config.rho_green
    is_intermediate = ~is_blue & ~is_green

    return Measurements(
        n_pixels=n_pixels,
        max_red=max_red,
        peak=peak,
        n_lit_1=n_lit_1,
        gate_used=gate_used,
        n_gated=int(mask.sum()),
        n_blue=int(is_blue.sum()),
        n_green=int(is_green.sum()),
        n_intermediate=int(is_intermediate.sum()),
        energy_blue=int(i[is_blue].sum()),
        energy_green=int(i[is_green].sum()),
        file_bytes=load.file_bytes,
        has_transparent_pixels=load.has_transparent_pixels,
    )
