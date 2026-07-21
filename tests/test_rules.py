from pathlib import Path

from colorsort.config import DEFAULT_CONFIG
from colorsort.messages import render
from colorsort.models import Decision, FileResult, Measurements, Msg
from colorsort.rules import crosscheck_file_sizes, decide


def _m(**kw) -> Measurements:
    """기본값이 채워진 Measurements. 필요한 필드만 덮어쓴다."""
    base = dict(
        n_pixels=10000, max_red=0, peak=17, n_lit_1=1000, gate_used=5, n_gated=1000,
        n_blue=1000, n_green=0, n_intermediate=0, energy_blue=17000, energy_green=0,
        file_bytes=7000, has_transparent_pixels=False,
    )
    base.update(kw)
    return Measurements(**base)


def test_rules_never_produce_human_sentences():
    """판정 로직에 문장이 들어가면 언어를 바꿀 수 없다. 열쇠만 나와야 한다."""
    d = decide(_m(), DEFAULT_CONFIG)
    assert d.reason.key.startswith("reason.")
    assert " " not in d.reason.key


def test_pure_blue():
    d = decide(_m(), DEFAULT_CONFIG)
    assert d.label == "BLUE"
    assert d.folder(DEFAULT_CONFIG) == "blue"
    assert d.low_confidence is False
    assert d.reason.key == "reason.pure_blue"
    assert "파랑" in render(d.reason, "ko")
    assert "Blue" in render(d.reason, "en")


def test_pure_green():
    d = decide(_m(n_blue=0, n_green=1000, energy_blue=0, energy_green=17000), DEFAULT_CONFIG)
    assert d.label == "GREEN"
    assert d.folder(DEFAULT_CONFIG) == "green"
    assert d.reason.key == "reason.pure_green"
    assert "초록" in render(d.reason, "ko")
    assert "Green" in render(d.reason, "en")


def test_stray_pixels_do_not_flip_a_pure_image():
    """파랑 1000개에 초록 10개가 섞여도 파랑이다. 소수파 하한 50 미만이므로."""
    d = decide(_m(n_blue=1000, n_green=10, energy_blue=17000, energy_green=170), DEFAULT_CONFIG)
    assert d.label == "BLUE"


def test_minority_floor_demotes_an_image_the_fraction_calls_pure():
    """비율과 하한이 엇갈릴 때 하한이 이긴다.

    파랑 5000 : 초록 60 이면 f_blue = 5000/5060 = 0.9881 이라 순수 기준 0.98을 넘는다.
    비율만 보면 파랑이지만 초록 60개가 하한 50 이상이라 순수가 아니고,
    min(5000, 60) = 60 >= 50 이므로 하이브리드로 내려간다.

    밝기를 픽셀당 17로 맞춰 f_blue_energy도 같은 0.9881이 되게 했다. 갈린 이유가
    일관성 검사(gap = 0)가 아니라 소수파 하한임을 분명히 하기 위해서다.
    """
    d = decide(_m(n_blue=5000, n_green=60, n_gated=5060, n_lit_1=5060,
                  energy_blue=85000, energy_green=1020), DEFAULT_CONFIG)
    assert d.label == "HYBRID", "비율이 순수라고 해도 소수파 하한을 넘으면 순수가 아니다"


def test_enough_minority_pixels_makes_it_hybrid():
    """초록이 60개면 하한 50을 넘으므로 하이브리드다."""
    d = decide(_m(n_blue=1000, n_green=60, energy_blue=17000, energy_green=1020), DEFAULT_CONFIG)
    assert d.label == "HYBRID"
    assert d.folder(DEFAULT_CONFIG) == "review"
    assert d.reason.key == "reason.mixed"
    assert "하이브리드" in render(d.reason, "ko")
    assert "hybrid" in render(d.reason, "en").lower()


def test_balanced_mix_is_hybrid():
    d = decide(_m(n_blue=500, n_green=500, energy_blue=8500, energy_green=8500), DEFAULT_CONFIG)
    assert d.label == "HYBRID"


def test_neither_pure_nor_hybrid_abstains_as_ambiguous():
    """양쪽 기준에 모두 못 미치면 마지막 분기인 기권으로 떨어진다.

    파랑 1000 : 초록 45 면 f_blue = 1000/1045 = 0.9569 라 순수 기준 0.98에 못 미치고,
    min(1000, 45) = 45 라 하이브리드 하한 50에도 못 미친다. 남는 것은 기권뿐이다.
    """
    d = decide(_m(n_blue=1000, n_green=45, n_gated=1045, n_lit_1=1045,
                  energy_blue=17000, energy_green=765), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "ambiguous"


def test_no_signal_reports_how_much_was_looked_for():
    """단정하지 않고 얼마나 찾았는지 수치를 낸다. 두 언어 모두에서."""
    d = decide(_m(gate_used=None, n_gated=0, n_blue=0, n_green=0, peak=0, n_lit_1=0,
                  energy_blue=0, energy_green=0, file_bytes=267), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "no_signal"
    assert d.folder(DEFAULT_CONFIG) == "review"

    ko, en = render(d.reason, "ko"), render(d.reason, "en")
    for text in (ko, en):
        assert "30" in text, "필요한 픽셀 수를 밝혀야 한다"
        assert "267" in text, "파일 크기를 밝혀야 한다"
    assert "0개" in ko, "실제 찾은 수를 밝혀야 한다"
    assert "완전" not in ko, "단정하는 표현을 쓰지 않는다"
    assert "completely" not in en.lower()


def test_near_miss_signal_reports_the_actual_count():
    d = decide(_m(gate_used=None, n_gated=0, n_blue=0, n_green=0, peak=3, n_lit_1=12,
                  energy_blue=0, energy_green=0), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason.params["found"] == 12
    assert "12개" in render(d.reason, "ko")
    assert "12" in render(d.reason, "en")


def test_transparency_abstains_before_anything_else():
    """투명 픽셀은 검정으로 합성되어 배경으로 둔갑한다. 다른 판정보다 먼저 걸러야 한다."""
    d = decide(_m(has_transparent_pixels=True), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "transparent"
    assert "투명" in render(d.reason, "ko")
    assert "transparent" in render(d.reason, "en").lower()


def test_transparency_wins_when_another_check_would_also_fire():
    """투명과 색 공간이 동시에 걸리면 투명이 이긴다.

    앞 시험은 다른 검사가 하나도 걸리지 않는 사진을 쓰므로 순서를 증명하지 못한다.
    투명 검사를 색 공간 아래로 옮겨도 그대로 통과한다. 빨강을 섞어 두 검사가 모두
    걸리게 해야 위쪽이 아래쪽을 가린다는 것이 드러난다.
    """
    d = decide(_m(has_transparent_pixels=True, max_red=50), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "transparent", "투명이 색 공간보다 먼저 걸러져야 한다"


def test_red_channel_abstains():
    d = decide(_m(max_red=50), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "colorspace"
    assert d.reason.params["max_red"] == 50
    assert "빨" in render(d.reason, "ko")
    assert "red" in render(d.reason, "en").lower()


def test_too_much_intermediate_colour_abstains():
    """전부 청록인 사진은 하이브리드가 아니라 제3의 색이다."""
    d = decide(_m(n_blue=0, n_green=0, n_intermediate=1000,
                  energy_blue=0, energy_green=0), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "intermediate"


def test_no_blue_and_no_green_abstains_instead_of_quietly_becoming_green():
    """파랑도 초록도 0이면 기권한다. 이 가드는 장식이 아니다.

    f_blue는 분모가 0일 때 0.0을 돌려준다. 그래서 이 가드를 지우면
    0.0 <= purity_eps 가 참이 되어, 초록 픽셀이 하나도 없는 사진이 GREEN으로 분류된다.
    터지지 않고 조용히 틀린다. 실제 measure() 출력으로는 닿기 어렵다는 이유로
    지우면 안 되는 까닭이 이것이다.
    """
    d = decide(_m(n_gated=1000, n_blue=0, n_green=0, n_intermediate=0,
                  energy_blue=0, energy_green=0), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "all_intermediate"


def test_relaxed_gate_marks_low_confidence():
    d = decide(_m(gate_used=2, n_green=1000, n_blue=0, energy_blue=0, energy_green=4000),
               DEFAULT_CONFIG)
    assert d.label == "GREEN"
    assert d.low_confidence is True


def test_consistency_check_applies_to_pure_only():
    """순수 분기에서 개수 비율과 밝기 비율이 크게 어긋나면 기권한다."""
    d = decide(_m(n_blue=1000, n_green=0, energy_blue=0, energy_green=17000), DEFAULT_CONFIG)
    assert d.label == "ABSTAIN"
    assert d.reason_code == "inconsistent"


def test_consistency_check_never_applies_to_hybrid():
    """밝기비가 심하게 치우친 진짜 하이브리드를 억제하면 안 된다.

    이 검사를 하이브리드에 걸면 밝기비 4:1 하이브리드의 85%가 억제된다.
    """
    d = decide(_m(n_blue=500, n_green=500, energy_blue=40000, energy_green=1000),
               DEFAULT_CONFIG)
    assert d.label == "HYBRID", "하이브리드는 일관성 검사로 기권시키지 않는다"


def test_crosscheck_flags_empty_file_that_is_suspiciously_large():
    """픽셀은 비었는데 파일이 크면 뭔가 놓쳤을 가능성이 있다."""
    empty_small = FileResult(Path("a.png"),
                             _m(gate_used=None, n_blue=0, n_green=0, n_lit_1=0, file_bytes=267),
                             Decision("ABSTAIN", Msg("reason.no_signal"), True))
    empty_big = FileResult(Path("b.png"),
                           _m(gate_used=None, n_blue=0, n_green=0, n_lit_1=0, file_bytes=9000),
                           Decision("ABSTAIN", Msg("reason.no_signal"), True))
    normal = FileResult(Path("c.png"), _m(file_bytes=7000),
                        Decision("BLUE", Msg("reason.pure_blue"), False))

    out = crosscheck_file_sizes([empty_small, empty_big, normal], DEFAULT_CONFIG)
    assert out[0].decision.warnings == ()
    assert [w.key for w in out[1].decision.warnings] == ["warn.empty_but_large"]
    assert "파일 크기" in render(out[1].decision.warnings[0], "ko")
    assert "File size" in render(out[1].decision.warnings[0], "en")
    assert out[2].decision.warnings == ()


def test_crosscheck_is_noop_without_empty_files():
    normal = FileResult(Path("c.png"), _m(), Decision("BLUE", Msg("reason.pure_blue"), False))
    out = crosscheck_file_sizes([normal], DEFAULT_CONFIG)
    assert out[0].decision.warnings == ()
