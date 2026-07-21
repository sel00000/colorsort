from pathlib import Path

import numpy as np

from colorsort.config import DEFAULT_CONFIG
from colorsort.measure import measure
from colorsort.models import LoadResult


def _load(rgb: np.ndarray, file_bytes: int = 1000, transparent: bool = False) -> LoadResult:
    """측정용 가짜 LoadResult. 파일 시스템을 쓰지 않는다."""
    return LoadResult(
        path=Path("fake.png"),
        rgb=rgb.astype(np.int32),
        width=rgb.shape[1],
        height=rgb.shape[0],
        file_bytes=file_bytes,
        has_transparent_pixels=transparent,
        palette_size=None,
    )


def _solid(color, size=(10, 10)) -> np.ndarray:
    a = np.zeros((size[0], size[1], 3), dtype=np.int32)
    a[..., 0], a[..., 1], a[..., 2] = color
    return a


def test_pure_blue_pixels_counted_as_blue():
    """실제 파랑 LUT 색 (0,0,17). rho = 17/17 = 1.0 >= 0.90"""
    m = measure(_load(_solid((0, 0, 17))), DEFAULT_CONFIG)
    assert m.gate_used == 5
    assert m.n_gated == 100
    assert m.n_blue == 100
    assert m.n_green == 0
    assert m.n_intermediate == 0
    assert m.f_blue == 1.0


def test_pure_green_pixels_counted_as_green():
    """실제 초록 LUT 색 (0,17,2). rho = 2/19 = 0.105 <= 0.35"""
    m = measure(_load(_solid((0, 17, 2))), DEFAULT_CONFIG)
    assert m.gate_used == 5
    assert m.n_green == 100
    assert m.n_blue == 0
    assert m.f_blue == 0.0


def test_mixed_image_counts_both():
    a = np.zeros((10, 20, 3), dtype=np.int32)
    a[:, :10, 2] = 17           # 왼쪽 절반 파랑
    a[:, 10:, 1] = 17           # 오른쪽 절반 초록
    a[:, 10:, 2] = 2
    m = measure(_load(a), DEFAULT_CONFIG)
    assert m.n_blue == 100
    assert m.n_green == 100
    assert m.f_blue == 0.5


def test_intermediate_colour_counted_separately():
    """청록 (0,10,10). rho = 0.5 이므로 파랑도 초록도 아니다."""
    m = measure(_load(_solid((0, 10, 10))), DEFAULT_CONFIG)
    assert m.n_intermediate == 100
    assert m.n_blue == 0
    assert m.n_green == 0


def test_gate_relaxes_when_signal_is_dim():
    """최댓값 4인 사진. 게이트 5로는 0개, 게이트 2로 내려가야 잡힌다.

    실제 데이터의 36-green.png가 정확히 이 경우다.
    """
    a = _solid((0, 4, 0), size=(10, 10))
    m = measure(_load(a), DEFAULT_CONFIG)
    assert m.gate_used == 2
    assert m.is_low_confidence is True
    assert m.n_gated == 100
    assert m.n_green == 100


def test_gate_falls_all_the_way_to_the_bottom_rung():
    """최댓값 1인 사진. 게이트 5도 2도 0개를 잡으므로 마지막 게이트 1까지 내려간다.

    intensity = max(G,B) = 1 이므로 intensity >= 5 는 0개, intensity >= 2 도 0개다.
    둘 다 n_min=30 에 못 미쳐 게이트 1(100개)이 선택된다.
    """
    a = _solid((0, 1, 0), size=(10, 10))
    m = measure(_load(a), DEFAULT_CONFIG)
    assert m.peak == 1
    assert m.gate_used == 1
    assert m.is_low_confidence is True
    assert m.n_gated == 100
    assert m.n_green == 100


def test_no_gate_reached_when_too_few_lit_pixels():
    """밝은 픽셀이 30개 미만이면 어떤 게이트로도 판정하지 않는다."""
    a = np.zeros((10, 10, 3), dtype=np.int32)
    a[0, :5, 2] = 17            # 밝은 픽셀 5개뿐
    m = measure(_load(a), DEFAULT_CONFIG)
    assert m.gate_used is None
    assert m.n_lit_1 == 5
    assert m.n_gated == 0


def test_completely_black_image():
    m = measure(_load(np.zeros((10, 10, 3), dtype=np.int32)), DEFAULT_CONFIG)
    assert m.gate_used is None
    assert m.n_lit_1 == 0
    assert m.peak == 0


def test_empty_array_from_failed_load_does_not_raise():
    """읽기에 실패한 파일은 (0,0,3) 빈 배열로 온다. 파이프라인은 load_error를 보기 전에
    measure를 먼저 부르므로, 여기서 죽으면 실행 전체가 첫 손상 파일에서 멈춘다.
    """
    m = measure(_load(np.zeros((0, 0, 3), dtype=np.int32)), DEFAULT_CONFIG)
    assert m.n_pixels == 0
    assert m.gate_used is None


def test_red_channel_is_recorded():
    """빨강은 실제 데이터에서 항상 0이다. 0이 아니면 예상 밖 입력이므로 기록해둔다."""
    a = _solid((50, 0, 17))
    m = measure(_load(a), DEFAULT_CONFIG)
    assert m.max_red == 50


def test_energy_weighting_uses_brightness():
    """밝은 파랑 30px + 어두운 초록 70px. 개수로는 초록이 많지만 밝기로는 파랑이 세다."""
    a = np.zeros((10, 10, 3), dtype=np.int32)
    a[:3, :, 2] = 100           # 파랑 30px, 밝기 100
    a[3:, :, 1] = 10            # 초록 70px, 밝기 10
    a[3:, :, 2] = 2
    m = measure(_load(a), DEFAULT_CONFIG)
    assert m.n_blue == 30
    assert m.n_green == 70
    assert m.energy_blue == 3000
    assert m.energy_green == 700
    assert m.f_blue < 0.5, "개수 비율은 파랑이 소수"
    assert m.f_blue_energy > 0.5, "밝기 비율은 파랑이 다수"


def test_passthrough_fields():
    m = measure(_load(_solid((0, 0, 17)), file_bytes=4242, transparent=True), DEFAULT_CONFIG)
    assert m.file_bytes == 4242
    assert m.has_transparent_pixels is True
    assert m.n_pixels == 100
