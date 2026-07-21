from colorsort import RULES_VERSION, __version__
from colorsort.config import DEFAULT_CONFIG, Config
from colorsort.models import Decision, Msg


def test_default_thresholds_are_the_verified_values():
    c = DEFAULT_CONFIG
    assert c.rho_blue == 0.90
    assert c.rho_green == 0.35
    assert c.gates == (5, 2, 1)
    assert c.n_min == 30
    assert c.minority_floor == 50
    assert c.max_intermediate_frac == 0.10
    assert c.purity_eps == 0.02
    assert c.consistency_max == 0.10


def test_strictest_gate_matches_the_value_hardcoded_in_is_low_confidence():
    """models.py 의 Measurements.is_low_confidence 가 이 값을 상수 5로 박아 두고 있다.

    Measurements 는 Config 를 들고 있지 않아 gates 를 참조할 방법이 없다. 그래서
    gates 를 (8, 4, 1) 로 바꾸면 가장 엄격한 게이트로 통과한 파일까지 전부 '신뢰도
    낮음'으로 표시되는데, 판정 자체는 멀쩡하므로 눈에 띄지 않는다.

    gates[0] 을 바꾸려면 models.py 의 is_low_confidence 도 함께 고칠 것.
    """
    assert DEFAULT_CONFIG.gates[0] == 5


def test_config_is_immutable():
    import dataclasses
    import pytest

    with pytest.raises(dataclasses.FrozenInstanceError):
        DEFAULT_CONFIG.rho_blue = 0.5


def test_rho_thresholds_leave_room_around_the_measured_luts():
    """초록 실측 rho 0.154, 파랑 1.0. 경계가 그 사이에 여유 있게 있어야 한다."""
    c = Config()
    assert 0.154 < c.rho_green, "초록 실측값이 초록 경계 안에 들어와야 한다"
    assert c.rho_blue <= 1.0
    assert c.rho_green < c.rho_blue, "두 경계가 뒤집히면 안 된다"


def test_decision_folder_mapping():
    c = DEFAULT_CONFIG
    assert Decision("BLUE", Msg("reason.pure_blue"), False).folder(c) == "blue"
    assert Decision("GREEN", Msg("reason.pure_green"), False).folder(c) == "green"
    assert Decision("HYBRID", Msg("reason.mixed"), False).folder(c) == "review"
    assert Decision("ABSTAIN", Msg("reason.no_signal"), True).folder(c) == "review"


def test_folder_names_are_configurable():
    """한글 폴더명을 원하면 설정으로 바꿀 수 있어야 한다."""
    c = Config(folder_review="확인필요")
    assert Decision("ABSTAIN", Msg("reason.no_signal"), True).folder(c) == "확인필요"


def test_reason_code_strips_the_namespace():
    assert Decision("ABSTAIN", Msg("reason.no_signal"), True).reason_code == "no_signal"


def test_versions_present():
    assert __version__
    assert RULES_VERSION
