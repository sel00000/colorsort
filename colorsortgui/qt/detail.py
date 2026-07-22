"""크게 보기: 왼쪽 큰 사진, 오른쪽 검사관 카드. 계기판 패널을 VENOM 옷으로 입힌 화면."""
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QButtonGroup, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QPushButton, QSlider, QVBoxLayout, QWidget)

from colorsort.config import DEFAULT_CONFIG
from colorsortgui.enhance import (auto_gain, channel_view, judgment_view,
                                  manual_view, probe)
from colorsortgui.i18n import tr
from .imageview import ZoomView
from .widgets import RhoRuler

_MODES = ("original", "corrected", "judgment", "green_only", "blue_only")


class DetailPage(QWidget):
    to_blue = Signal(); to_green = Signal(); undone = Signal(); back = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rgb = None
        self._meta = {}
        self._lang = "en"
        root = QHBoxLayout(self)

        left = QVBoxLayout()
        self.view = ZoomView()
        self.view.probed.connect(self.on_probe)
        self.overlay = QLabel("", self.view)
        self.overlay.setAlignment(Qt.AlignCenter)
        self.overlay.setProperty("class", "overlay")   # 크기·색은 테마 QSS가 배율까지 관리
        self.overlay.hide()
        self.probe_label = QLabel(" ")
        self.probe_label.setProperty("class", "probe")
        left.addWidget(self.view, 1)
        left.addWidget(self.probe_label)
        root.addLayout(left, 3)

        card = QFrame(); card.setProperty("class", "card")
        side = QVBoxLayout(card)
        self.title = QLabel(""); self.title.setProperty("class", "k")
        side.addWidget(self.title)

        seg = QHBoxLayout(); self._mode_group = QButtonGroup(self)
        self._mode_btns = {}
        for mode in _MODES:
            b = QPushButton(); b.setCheckable(True); b.setProperty("class", "tab")
            self._mode_group.addButton(b); seg.addWidget(b)
            self._mode_btns[mode] = b
            b.clicked.connect(lambda _=False, m=mode: self.set_view_mode(m))
        side.addLayout(seg)

        grid = QGridLayout()
        self._rows = {}
        for row, key in enumerate(("insp.peak", "insp.view", "insp.lit",
                                   "insp.blue_share", "insp.reason")):
            k = QLabel(); k.setProperty("class", "mut")
            v = QLabel(); v.setProperty("class", "mono")
            grid.addWidget(k, row, 0); grid.addWidget(v, row, 1, Qt.AlignRight)
            self._rows[key] = (k, v)
        side.addLayout(grid)

        self.ruler = RhoRuler(); side.addWidget(self.ruler)

        self.bright_label = QLabel()
        self.bright_slider = QSlider(Qt.Horizontal)
        self.bright_slider.setRange(10, 40)          # auto_gain의 ×1.0 ~ ×4.0
        self.bright_slider.setValue(10)
        self.gamma_label = QLabel()
        self.gamma_slider = QSlider(Qt.Horizontal)
        self.gamma_slider.setRange(30, 100)          # γ 0.30 ~ 1.00
        self.gamma_slider.setValue(35)
        self.auto_btn = QPushButton()
        for s in (self.bright_slider, self.gamma_slider):
            s.valueChanged.connect(self._refresh_view)
        self.auto_btn.clicked.connect(self._reset_sliders)
        side.addWidget(self.bright_label); side.addWidget(self.bright_slider)
        side.addWidget(self.gamma_label); side.addWidget(self.gamma_slider)
        side.addWidget(self.auto_btn)

        self.save_btn = QPushButton()
        acts = QHBoxLayout()
        self.blue_btn = QPushButton(); self.blue_btn.setObjectName("toBlue")
        self.green_btn = QPushButton(); self.green_btn.setObjectName("toGreen")
        self.undo_btn = QPushButton()
        self.back_btn = QPushButton()
        self.blue_btn.clicked.connect(self.to_blue)
        self.green_btn.clicked.connect(self.to_green)
        self.undo_btn.clicked.connect(self.undone)
        self.back_btn.clicked.connect(self.back)
        acts.addWidget(self.blue_btn); acts.addWidget(self.green_btn)
        side.addWidget(self.save_btn)
        side.addLayout(acts)
        side.addWidget(self.undo_btn)
        side.addStretch(1)
        side.addWidget(self.back_btn)
        root.addWidget(card, 2)

        self._mode = "corrected"

    # ── 상태 ──
    def view_mode(self) -> str:
        return self._mode

    def set_view_mode(self, mode: str) -> None:
        self._mode = mode
        self._mode_btns[mode].setChecked(True)
        corrected = mode == "corrected"
        for w in (self.bright_slider, self.gamma_slider, self.auto_btn):
            w.setEnabled(corrected and self._meta.get("peak", 0) > 0)
        self._refresh_view()

    def _reset_sliders(self) -> None:
        self.bright_slider.setValue(10)
        self.gamma_slider.setValue(35)

    def show_item(self, rgb, meta: dict, lang: str) -> None:
        self._rgb, self._meta, self._lang = rgb, meta, lang
        for key, (k, _v) in self._rows.items():
            k.setText(tr(key, lang))
        self.title.setText(f"{tr('insp.title', lang).upper()} — {meta['name']}")
        for name, btn_key in (("original", "view.original"), ("corrected", "view.corrected"),
                              ("judgment", "view.judgment"), ("green_only", "view.green_only"),
                              ("blue_only", "view.blue_only")):
            self._mode_btns[name].setText(tr(btn_key, lang))
        self.auto_btn.setText(tr("btn.auto", lang))
        self.save_btn.setText(tr("btn.save_png", lang))
        self.blue_btn.setText(tr("btn.to_blue", lang))
        self.green_btn.setText(tr("btn.to_green", lang))
        self.undo_btn.setText(tr("btn.undo", lang))
        self.back_btn.setText(tr("btn.back", lang))
        self._rows["insp.peak"][1].setText(f"{meta['peak']} / 255")
        self._rows["insp.lit"][1].setText(f"{meta['lit']:,}")
        self._rows["insp.blue_share"][1].setText(f"{100 * meta['f_blue']:.1f}%")
        self._rows["insp.reason"][1].setText(meta["reason_text"])
        self.ruler.set_rho(meta["rho_hint"])
        no_signal = meta["peak"] <= 0
        self.overlay.setText(tr("msg.no_signal", lang))
        self.overlay.setVisible(no_signal)
        self.overlay.resize(self.view.size())
        self.save_btn.setEnabled(not no_signal)
        self._reset_sliders()
        self.set_view_mode("corrected")

    def _gain(self) -> float:
        return auto_gain(self._rgb) * (self.bright_slider.value() / 10.0)

    def _gamma(self) -> float:
        return self.gamma_slider.value() / 100.0

    def current_view_array(self) -> np.ndarray:
        if self._mode == "original":
            return np.clip(self._rgb, 0, 255).astype(np.uint8)
        if self._mode == "judgment":
            return judgment_view(self._rgb, DEFAULT_CONFIG)
        if self._mode == "green_only":
            return channel_view(self._rgb, "green")
        if self._mode == "blue_only":
            return channel_view(self._rgb, "blue")
        return manual_view(self._rgb, self._gain(), self._gamma())

    def _refresh_view(self) -> None:
        if self._rgb is None:
            return
        lang = self._lang
        mult = self.bright_slider.value() / 10.0
        self.bright_label.setText(
            f"{tr('slider.brightness', lang)}  ×{auto_gain(self._rgb) * mult:.1f}"
            + ("  (auto)" if mult == 1.0 else ""))
        self.gamma_label.setText(f"{tr('slider.gamma', lang)}  {self._gamma():.2f}")
        self._rows["insp.view"][1].setText(
            tr("insp.auto_view", lang, gamma=f"{self._gamma():.2f}",
               gain=f"{self._gain():.1f}"))
        self.view.set_array(self.current_view_array())

    def on_probe(self, x: int, y: int) -> None:
        if self._rgb is None:
            return
        g, b, rho = probe(self._rgb, x, y)
        self.probe_label.setText(
            tr("probe.line", self._lang, x=x, y=y, g=g, b=b, rho=rho))
        self.ruler.set_rho(rho)
