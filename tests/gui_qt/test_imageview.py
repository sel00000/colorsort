import numpy as np
from colorsortgui.qt.imageview import ZoomView, array_to_qimage


def test_array_to_qimage_size_and_pixel(qapp):
    arr = np.zeros((10, 20, 3), dtype=np.uint8); arr[2, 3] = (0, 50, 200)
    img = array_to_qimage(arr)
    assert (img.width(), img.height()) == (20, 10)
    c = img.pixelColor(3, 2)
    assert (c.red(), c.green(), c.blue()) == (0, 50, 200)


def test_set_array_populates_scene(qapp):
    v = ZoomView()
    v.set_array(np.zeros((8, 8, 3), dtype=np.uint8))
    assert v.scene().itemsBoundingRect().width() == 8


def test_probe_signal(qapp):
    v = ZoomView()
    v.set_array(np.zeros((8, 8, 3), dtype=np.uint8))
    got = []
    v.probed.connect(lambda x, y: got.append((x, y)))
    v.emit_probe_for_test(3, 4)
    assert got == [(3, 4)]
