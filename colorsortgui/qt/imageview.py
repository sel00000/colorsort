"""확대·이동 가능한 이미지 뷰. 마우스가 가리키는 이미지 좌표를 신호로 알린다."""
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


def array_to_qimage(arr: np.ndarray) -> QImage:
    arr = np.ascontiguousarray(arr)              # QImage는 연속 메모리를 요구한다
    h, w, _ = arr.shape
    img = QImage(arr.data, w, h, 3 * w, QImage.Format_RGB888)
    return img.copy()                            # 원본 버퍼 수명과 분리


class ZoomView(QGraphicsView):
    probed = Signal(int, int)                    # 이미지 좌표 (x, y)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self._item: QGraphicsPixmapItem | None = None
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)  # 픽셀이 보여야 한다
        self.setMouseTracking(True)
        self.setBackgroundBrush(Qt.black)

    def set_array(self, arr: np.ndarray) -> None:
        pix = QPixmap.fromImage(array_to_qimage(arr))
        self.scene().clear()
        self._item = self.scene().addPixmap(pix)
        self.setSceneRect(self._item.boundingRect())
        self.fitInView(self._item, Qt.KeepAspectRatio)

    def wheelEvent(self, ev):
        factor = 1.25 if ev.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def mouseMoveEvent(self, ev):
        if self._item is not None:
            p = self._item.mapFromScene(self.mapToScene(ev.position().toPoint()))
            x, y = int(p.x()), int(p.y())
            r = self._item.pixmap().rect()
            if 0 <= x < r.width() and 0 <= y < r.height():
                self.probed.emit(x, y)
        super().mouseMoveEvent(ev)

    def emit_probe_for_test(self, x: int, y: int) -> None:
        self.probed.emit(x, y)
