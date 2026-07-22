from colorsortgui.qt.langdialog import LanguageDialog


def test_default_is_english(qapp):
    d = LanguageDialog()
    assert d.selected() == "en"                 # 기본 English (요구사항)


def test_korean_selectable(qapp):
    d = LanguageDialog()
    d.ko.setChecked(True)
    assert d.selected() == "ko"
