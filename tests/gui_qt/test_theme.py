from colorsortgui.qt.theme import QSS, C


def test_tokens_exist():
    for name in ("BG0", "BG1", "CARD", "HAIR", "TEXT", "MUT",
                 "RED", "RED_H", "BLUE", "GREEN", "AMBER", "MONO"):
        assert name in C


def test_qss_uses_tokens(qapp):
    assert C["RED"] in QSS and C["CARD"] in QSS
    qapp.setStyleSheet(QSS)          # 파싱 오류 없이 적용되어야 한다
    assert qapp.styleSheet() == QSS


def test_qss_scales_font_sizes(qapp):
    from colorsortgui.qt.theme import qss
    assert "font-size: 24px" in qss(1.0)          # 기본 크기 (실기 피드백 값)
    assert "font-size: 36px" in qss(1.5)          # 1.5배에서 기본 글자 36px
    qapp.setStyleSheet(qss(1.5))                  # 파싱 오류 없이 적용
    qapp.setStyleSheet(qss(1.0))
