"""실제 196장에 대한 회귀 테스트.

기대값은 설계 단계에서 독립적인 픽셀 대수로 검증한 것이다.
    파랑 99장 (G가 전부 0), 초록 96장 (G>0인 픽셀 있음), 신호없음 1장
이 숫자가 바뀌면 판정 로직이 달라졌다는 뜻이므로 반드시 확인해야 한다.
"""

from collections import Counter
from pathlib import Path

import numpy as np
import pytest

from colorsort.config import DEFAULT_CONFIG
from colorsort.loading import load_image
from colorsort.measure import measure
from colorsort.messages import render
from colorsort.rules import decide

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIRS = [PROJECT_ROOT / "A", PROJECT_ROOT / "B"]

pytestmark = pytest.mark.skipif(
    not all(d.is_dir() for d in IMAGE_DIRS),
    reason="실제 사진 폴더(A, B)가 없으면 건너뜁니다",
)


def _all_pngs() -> list[Path]:
    out = []
    for d in IMAGE_DIRS:
        out.extend(sorted(p for p in d.rglob("*.png") if p.is_file()))
    return out


def _content_truth(path: Path) -> str:
    """파일명을 쓰지 않는 독립 정답. 순수 픽셀 대수로만 만든다."""
    rgb = np.asarray(load_image(path).rgb)
    g, b = rgb[..., 1], rgb[..., 2]
    if g.max() == 0 and b.max() == 0:
        return "empty"
    return "blue" if g.max() == 0 else "green"


def test_finds_all_196_images():
    assert len(_all_pngs()) == 196


def test_classification_matches_independent_content_truth():
    """판정 결과가 독립적으로 만든 내용 기준 정답과 완전히 일치해야 한다."""
    expected = {"blue": "BLUE", "green": "GREEN", "empty": "ABSTAIN"}
    mismatches = []
    for path in _all_pngs():
        loaded = load_image(path)
        d = decide(measure(loaded, DEFAULT_CONFIG), DEFAULT_CONFIG)
        truth = _content_truth(path)
        if d.label != expected[truth]:
            mismatches.append((path.name, truth, d.label))
    assert mismatches == [], f"불일치 {len(mismatches)}건: {mismatches[:5]}"


def test_label_distribution_is_stable():
    counts = Counter()
    for path in _all_pngs():
        loaded = load_image(path)
        counts[decide(measure(loaded, DEFAULT_CONFIG), DEFAULT_CONFIG).label] += 1
    assert counts["BLUE"] == 99
    assert counts["GREEN"] == 96
    assert counts["ABSTAIN"] == 1
    assert counts["HYBRID"] == 0, "현재 데이터에는 하이브리드가 없어야 한다"


def test_only_one_image_needs_the_relaxed_gate():
    """36-green.png만 게이트 완화가 필요하다. 완화 로직이 없으면 이 파일을 놓친다."""
    relaxed = [p.name for p in _all_pngs()
               if measure(load_image(p), DEFAULT_CONFIG).is_low_confidence]
    assert relaxed == ["36-green.png"]


def test_no_image_uses_transparency_today():
    """지금은 투명 픽셀을 쓰는 파일이 없다. 생기면 로직을 재검토해야 한다."""
    transparent = [p.name for p in _all_pngs() if load_image(p).has_transparent_pixels]
    assert transparent == []


def test_red_channel_is_zero_everywhere():
    """이 전제가 깨지면 rho 기반 접근 전체를 다시 봐야 한다."""
    with_red = [p.name for p in _all_pngs()
                if measure(load_image(p), DEFAULT_CONFIG).max_red > 0]
    assert with_red == []


def test_the_empty_file_gets_an_honest_reason():
    """'완전 검정'이라고 단정하지 않고 얼마나 찾았는지 밝혀야 한다. 두 언어 모두에서."""
    empty = [p for p in _all_pngs() if _content_truth(p) == "empty"]
    assert len(empty) == 1
    d = decide(measure(load_image(empty[0]), DEFAULT_CONFIG), DEFAULT_CONFIG)
    assert d.reason_code == "no_signal"

    ko, en = render(d.reason, "ko"), render(d.reason, "en")
    assert "0개" in ko
    assert "완전" not in ko
    assert "completely" not in en.lower()
    assert "30" in ko and "30" in en, "필요한 픽셀 수를 밝혀야 한다"


def test_every_verdict_renders_in_both_languages():
    """열쇠를 빠뜨리면 문장 대신 'reason.xxx' 가 그대로 나온다. 실제 데이터로 확인한다."""
    unrendered = []
    for path in _all_pngs():
        d = decide(measure(load_image(path), DEFAULT_CONFIG), DEFAULT_CONFIG)
        for lang in ("ko", "en"):
            text = render(d.reason, lang)
            if text == d.reason.key or text.startswith("reason."):
                unrendered.append((path.name, lang, d.reason.key))
    assert unrendered == [], f"렌더링 실패: {unrendered[:5]}"


def test_no_korean_leaks_into_english_output():
    """영어를 골랐는데 한국어가 섞여 나오면 안 된다."""
    import re
    hangul = re.compile(r"[가-힣]")
    leaks = []
    for path in _all_pngs():
        d = decide(measure(load_image(path), DEFAULT_CONFIG), DEFAULT_CONFIG)
        text = render(d.reason, "en")
        if hangul.search(text):
            leaks.append((path.name, text))
    assert leaks == [], f"영어 출력에 한국어 혼입: {leaks[:3]}"
