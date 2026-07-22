"""검사관 패널의 ρ 눈금자와 첫 화면 통계 카드."""
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from .theme import C


class RhoRuler(QWidget):
    """rho(0=초록 … 1=파랑)가 경계 어디에 떨어지는지 보여준다. 경계: 0.35 / 0.90."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rho = 0.0
        self.setMinimumHeight(26)

    def set_rho(self, value: float) -> None:
        self.rho = max(0.0, min(1.0, float(value)))
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        w, mid = self.width(), 10

        def seg(a, b, color):
            p.fillRect(int(a * w), mid, int((b - a) * w) + 1, 6, QColor(color))

        seg(0.00, 0.35, C["GREEN"])
        seg(0.35, 0.90, "#3A4A5A")
        seg(0.90, 1.00, C["BLUE"])
        pen = QPen(QColor(C["TEXT"])); pen.setWidth(2)
        p.setPen(pen)
        x = int(self.rho * (w - 2)) + 1
        p.drawLine(x, mid - 5, x, mid + 11)
        p.end()


class StatCard(QFrame):
    def __init__(self, title: str, accent: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        k = QLabel(title); k.setProperty("class", "k")
        self.value_label = QLabel("0")
        self.value_label.setProperty("class", "statv")  # 크기·굵기는 테마 QSS가 배율까지 관리
        self.value_label.setStyleSheet(f"color: {accent};")
        lay.addWidget(k); lay.addWidget(self.value_label)

    def set_value(self, n: int) -> None:
        self.value_label.setText(str(n))
