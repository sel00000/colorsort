import numpy as np
from colorsortgui.qt.detail import DetailPage


def _rgb(peak=200):
    a = np.zeros((6, 6, 3), dtype=np.int32); a[..., 2] = peak
    return a


META = {"name": "x.png", "peak": 200, "lit": 36, "f_blue": 1.0,
        "rho_hint": 1.0, "reason_text": "pure blue", "human": None}


def test_default_view_is_corrected(qapp):
    d = DetailPage(); d.show_item(_rgb(), META, "en")
    assert d.view_mode() == "corrected"
    # γ0.35 정규화면 최댓값은 (거의) 255. A4 manual_view가 float→uint8을 truncate하고
    # 255.0/200*200 이 254.99997로 떨어져 254가 된다. A4 자신의 테스트도 ±1 LSB를
    # 허용하므로(test_auto_view_measured_value의 <=1) 같은 관용으로 맞춘다. [B] 이탈 참조.
    assert abs(int(d.current_view_array().max()) - 255) <= 1


def test_original_view_shows_raw(qapp):
    d = DetailPage(); d.show_item(_rgb(40), dict(META, peak=40), "en")
    d.set_view_mode("original")
    assert d.current_view_array().max() == 40


def test_no_signal_disables(qapp):
    d = DetailPage(); d.show_item(np.zeros((6, 6, 3), dtype=np.int32),
                                  dict(META, peak=0), "en")
    assert not d.gamma_slider.isEnabled() and not d.save_btn.isEnabled()
    # 창을 show()하지 않은 위젯의 자식은 isVisible()==False라 의도(오버레이를 켬)를
    # isHidden()으로 검사한다 — Qt 테스트 이식성 문제. detail.py는 무변경. [B] 이탈 참조.
    assert not d.overlay.isHidden()


def test_buttons_emit(qapp):
    d = DetailPage(); d.show_item(_rgb(), META, "en")
    got = []
    d.to_blue.connect(lambda: got.append("b")); d.blue_btn.click()
    d.to_green.connect(lambda: got.append("g")); d.green_btn.click()
    assert got == ["b", "g"]


def test_probe_updates_line_and_ruler(qapp):
    d = DetailPage(); d.show_item(_rgb(), META, "en")
    d.on_probe(2, 3)
    assert "ρ 1.0" in d.probe_label.text()
    assert d.ruler.rho == 1.0
