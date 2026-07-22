import numpy as np
from colorsort.config import DEFAULT_CONFIG
from colorsortgui import enhance

def _img(g, b, shape=(4, 4)):
    rgb = np.zeros((*shape, 3), dtype=np.int32)
    rgb[..., 1] = g; rgb[..., 2] = b
    return rgb

def test_auto_view_measured_value():
    # 실측 근거: 값 1, 최대 9 → γ0.35에서 표시값 118 (요구사항의 그 사진)
    rgb = _img(0, 1); rgb[0, 0, 2] = 9          # peak=9
    out = enhance.auto_view(rgb)
    assert abs(int(out[1, 1, 2]) - 118) <= 1
    assert out.dtype == np.uint8

def test_manual_view_gain1_gamma1_is_identity():
    rgb = _img(0, 40)
    out = enhance.manual_view(rgb, gain=1.0, gamma=1.0)
    assert int(out[0, 0, 2]) == 40 and int(out[0, 0, 1]) == 0

def test_view_preserves_hue_ratio():
    rgb = _img(30, 10)                           # rho = 10/40 = 0.25
    out = enhance.auto_view(rgb).astype(float)
    g, b = out[0, 0, 1], out[0, 0, 2]
    assert abs(b / (g + b) - 0.25) < 0.02        # 보정해도 색 비율 보존

def test_peak_zero_all_black():
    out = enhance.auto_view(_img(0, 0))
    assert out.sum() == 0 and enhance.peak_of(_img(0, 0)) == 0

def test_judgment_masks_match_measure_counts():
    rgb = np.zeros((10, 10, 3), dtype=np.int32)
    rgb[:5, :, 2] = 200                          # 파랑 50픽셀 (rho 1.0)
    rgb[5:, :, 1] = 200; rgb[5:, :, 2] = 30      # 초록 50픽셀 (rho≈0.13)
    from colorsort.measure import measure
    from colorsort.models import LoadResult as LR
    from pathlib import Path
    m = measure(LR(Path("x"), rgb, 10, 10, 1, False, None), DEFAULT_CONFIG)
    mb, mg, mi, gate = enhance.judgment_masks(rgb, DEFAULT_CONFIG)
    assert int(mb.sum()) == m.n_blue and int(mg.sum()) == m.n_green
    assert int(mi.sum()) == m.n_intermediate and gate == m.gate_used

def test_judgment_view_colors():
    # 계획서는 (4,4)=16픽셀이나 n_min=30에 못 미쳐 게이트가 안 열린다.
    # judgment_masks는 measure()와 동일 게이트라 빈 마스크→검정이 되어 계획서
    # 기대(파랑)와 어긋난다. 실측으로 확인해 6x6=36픽셀로 키운다([A] 이탈 기록).
    rgb = _img(0, 200, shape=(6, 6))
    out = enhance.judgment_view(rgb, DEFAULT_CONFIG)
    assert tuple(out[0, 0]) == (43, 109, 229)    # 파랑으로 센 픽셀

def test_channel_view_isolates():
    rgb = _img(120, 80)
    g_only = enhance.channel_view(rgb, "green")
    assert g_only[..., 2].sum() == 0 and g_only[..., 1].sum() > 0
    b_only = enhance.channel_view(rgb, "blue")
    assert b_only[..., 1].sum() == 0 and b_only[..., 2].sum() > 0

def test_probe():
    rgb = _img(30, 10)
    assert enhance.probe(rgb, 0, 0) == (30, 10, 0.25)
    assert enhance.probe(_img(0, 0), 0, 0) == (0, 0, 0.0)
