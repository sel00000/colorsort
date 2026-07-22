from PySide6.QtGui import QPixmap
from colorsortgui.qt.widgets import RhoRuler, StatCard


def test_rho_ruler_renders(qapp):
    w = RhoRuler(); w.set_rho(0.97); w.resize(220, 30)
    pix = QPixmap(w.size()); w.render(pix)
    img = pix.toImage()
    colors = {img.pixelColor(x, 12).name() for x in range(0, 220, 7)}
    assert len(colors) > 2                      # 초록·회색·파랑 구간이 실제로 칠해졌다


def test_rho_ruler_clamps(qapp):
    w = RhoRuler(); w.set_rho(1.7)
    assert w.rho == 1.0


def test_stat_card_text(qapp):
    c = StatCard("SCANNED", accent="#FFFFFF")
    c.set_value(196)
    assert c.value_label.text() == "196"
