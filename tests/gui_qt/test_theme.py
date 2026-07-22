from colorsortgui.qt.theme import QSS, C


def test_tokens_exist():
    for name in ("BG0", "BG1", "CARD", "HAIR", "TEXT", "MUT",
                 "RED", "RED_H", "BLUE", "GREEN", "AMBER", "MONO"):
        assert name in C


def test_qss_uses_tokens(qapp):
    assert C["RED"] in QSS and C["CARD"] in QSS
    qapp.setStyleSheet(QSS)          # 파싱 오류 없이 적용되어야 한다
    assert qapp.styleSheet() == QSS
