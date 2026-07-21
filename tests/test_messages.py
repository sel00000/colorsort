import re
import string

import pytest

from colorsort.messages import (
    CATALOG, CSV_COLUMNS, DEFAULT_LANG, LANG_NAMES, SUPPORTED_LANGS, render, t,
)
from colorsort.models import Msg


def test_every_supported_language_has_a_catalog_and_a_name():
    for lang in SUPPORTED_LANGS:
        assert lang in CATALOG
        assert lang in LANG_NAMES


def test_both_catalogs_have_exactly_the_same_keys():
    """열쇠가 어긋나면 한 언어에서만 문장이 깨진다. 이 테스트가 그걸 막는다."""
    ko = set(CATALOG["ko"])
    en = set(CATALOG["en"])
    assert ko == en, (
        f"한국어에만 있음: {sorted(ko - en)} / 영어에만 있음: {sorted(en - ko)}"
    )


def _placeholders(template: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(template) if f}


def test_both_languages_use_the_same_format_arguments():
    """같은 열쇠인데 인자가 다르면 한쪽에서 KeyError가 난다."""
    mismatches = []
    for key in CATALOG["ko"]:
        ko = _placeholders(CATALOG["ko"][key])
        en = _placeholders(CATALOG["en"][key])
        if ko != en:
            mismatches.append((key, sorted(ko), sorted(en)))
    assert mismatches == [], f"인자 불일치: {mismatches}"


def test_csv_columns_all_resolve_in_every_language():
    for lang in SUPPORTED_LANGS:
        for key in CSV_COLUMNS:
            assert t(key, lang) != key, f"{lang} 에 {key} 가 없다"


def test_csv_column_names_differ_between_languages():
    ko = [t(k, "ko") for k in CSV_COLUMNS]
    en = [t(k, "en") for k in CSV_COLUMNS]
    assert ko != en
    assert "판정" in ko
    assert "verdict" in en


def test_render_fills_in_numbers():
    msg = Msg("reason.no_signal",
              {"needed": 30, "found": 0, "peak": 0, "file_bytes": 267})
    ko = render(msg, "ko")
    en = render(msg, "en")
    assert "30" in ko and "0개" in ko and "267" in ko
    assert "30" in en and "267" in en
    assert ko != en


def test_no_signal_message_never_asserts_emptiness():
    """'완전 검정'이라고 단정하지 않는다. 두 언어 모두에서 지켜야 한다."""
    msg = Msg("reason.no_signal",
              {"needed": 30, "found": 0, "peak": 0, "file_bytes": 267})
    assert "완전" not in render(msg, "ko")
    assert "completely" not in render(msg, "en").lower()
    assert "empty" not in render(msg, "en").lower()


def test_unknown_language_falls_back_to_default():
    msg = Msg("summary.total", {"n": 5})
    assert render(msg, "xx") == render(msg, DEFAULT_LANG)


def test_unknown_key_returns_the_key_itself():
    """조용히 빈 문자열을 돌려주면 누락을 못 찾는다. 열쇠를 그대로 노출한다."""
    assert t("no.such.key", "ko") == "no.such.key"


def test_verdict_labels_are_not_translated():
    """BLUE/GREEN 같은 판정 값은 기계용이므로 카탈로그에 없어야 한다."""
    for lang in SUPPORTED_LANGS:
        assert "BLUE" not in CATALOG[lang]
        assert "GREEN" not in CATALOG[lang]
