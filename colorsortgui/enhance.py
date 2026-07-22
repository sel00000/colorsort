"""화면 표시 전용 변환. 판정에는 절대 닿지 않는다.

자동 보정 공식은 2026-07-21 실측으로 확정: 밝기 정규화 + 감마 0.35.
판정 색칠은 반드시 원본 값의 rho로 칠한다 — 보정 버퍼에서 다시 계산하면
실제 판정과 어긋난다(시각화 설계 문서의 경고).
"""
import numpy as np

AUTO_GAMMA = 0.35
JUDGE_BLUE = (43, 109, 229)
JUDGE_GREEN = (52, 168, 107)
JUDGE_INTER = (128, 128, 128)

def peak_of(rgb) -> int:
    if rgb.size == 0:
        return 0
    return int(np.maximum(rgb[..., 1], rgb[..., 2]).max())

def auto_gain(rgb) -> float:
    peak = peak_of(rgb)
    return 255.0 / peak if peak > 0 else 1.0

def manual_view(rgb, gain: float, gamma: float) -> np.ndarray:
    g = rgb[..., 1].astype(np.float64)
    b = rgb[..., 2].astype(np.float64)
    inten = np.maximum(g, b)
    out = np.zeros(rgb.shape[:2] + (3,), dtype=np.uint8)
    if inten.max() <= 0:
        return out
    x = np.clip(inten * gain / 255.0, 0.0, 1.0)
    disp = 255.0 * np.power(x, gamma)
    scale = np.divide(disp, inten, out=np.zeros_like(disp), where=inten > 0)
    out[..., 1] = np.clip(g * scale, 0, 255).astype(np.uint8)
    out[..., 2] = np.clip(b * scale, 0, 255).astype(np.uint8)
    return out

def auto_view(rgb) -> np.ndarray:
    return manual_view(rgb, auto_gain(rgb), AUTO_GAMMA)

def judgment_masks(rgb, config):
    """measure()와 같은 게이트 선택·같은 경계로 픽셀 소속을 돌려준다."""
    g = rgb[..., 1]
    b = rgb[..., 2]
    inten = np.maximum(g, b)
    gate_used, mask = None, None
    for gate in config.gates:
        candidate = inten >= gate
        if int(candidate.sum()) >= config.n_min:
            gate_used, mask = gate, candidate
            break
    shape = inten.shape
    if gate_used is None:
        empty = np.zeros(shape, dtype=bool)
        return empty, empty, empty, None
    denom = (g + b).astype(np.float64)
    rho = np.divide(b, denom, out=np.zeros_like(denom), where=denom > 0)
    mask_blue = mask & (rho >= config.rho_blue)
    mask_green = mask & (rho <= config.rho_green)
    mask_inter = mask & ~mask_blue & ~mask_green
    return mask_blue, mask_green, mask_inter, gate_used

def judgment_view(rgb, config) -> np.ndarray:
    mb, mg, mi, _ = judgment_masks(rgb, config)
    out = np.zeros(rgb.shape[:2] + (3,), dtype=np.uint8)
    out[mb] = JUDGE_BLUE
    out[mg] = JUDGE_GREEN
    out[mi] = JUDGE_INTER
    return out

def channel_view(rgb, channel: str) -> np.ndarray:
    idx = 1 if channel == "green" else 2
    ch = rgb[..., idx].astype(np.float64)
    out = np.zeros(rgb.shape[:2] + (3,), dtype=np.uint8)
    peak = ch.max()
    if peak <= 0:
        return out
    disp = 255.0 * np.power(np.clip(ch / peak, 0.0, 1.0), AUTO_GAMMA)
    out[..., idx] = disp.astype(np.uint8)
    return out

def probe(rgb, x: int, y: int) -> tuple[int, int, float]:
    g = int(rgb[y, x, 1]); b = int(rgb[y, x, 2])
    rho = b / (g + b) if (g + b) > 0 else 0.0
    return g, b, round(rho, 4)
