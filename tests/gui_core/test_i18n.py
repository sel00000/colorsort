import re
from colorsortgui.i18n import LANGS, T, tr

def test_langs_and_default():
    assert LANGS == ("en", "ko")

def test_same_keys_everywhere():
    assert set(T["en"].keys()) == set(T["ko"].keys())

def test_same_placeholders_everywhere():
    pat = re.compile(r"{(\w+)}")
    for key in T["en"]:
        assert set(pat.findall(T["en"][key])) == set(pat.findall(T["ko"][key])), key

def test_tr_formats():
    assert tr("stat.scanned", "en") == "Scanned"
    assert "196" in tr("msg.progress", "en", done=196, total=196)

def test_unknown_key_raises():
    try:
        tr("no.such.key", "en"); assert False
    except KeyError:
        pass

def test_no_photos_key_replaces_no_png():
    assert "err.no_photos" in T["en"] and "err.no_photos" in T["ko"]
    assert "err.no_png" not in T["en"] and "err.no_png" not in T["ko"]

def test_all_excluded_formats_count():
    assert "5" in tr("err.all_excluded", "en", n=5)
    assert "5" in tr("err.all_excluded", "ko", n=5)
