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
