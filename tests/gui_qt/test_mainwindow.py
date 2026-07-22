from pathlib import Path
from colorsortgui.qt.mainwindow import MainWindow


def test_boot_counts_zero(qapp):
    w = MainWindow(lang="en", settings={})
    assert w.visible_count() == 0


def test_open_folder_populates(qapp, fake_project):
    w = MainWindow(lang="en", settings={})
    w.open_folder(Path("/fake"))                 # 스텁은 동기 완료
    qapp.processEvents()
    assert w.visible_count() == 3
    assert w.stat_cards["all"].value_label.text() == "3"


def test_tab_filtering(qapp, fake_project):
    w = MainWindow(lang="en", settings={})
    w.open_folder(Path("/fake")); qapp.processEvents()
    w.set_tab("blue")
    assert w.current_tab() == "blue" and w.visible_count() == 1
    w.set_tab("review")
    assert w.visible_count() == 1


def test_min_size(qapp):
    w = MainWindow(lang="en", settings={})
    assert w.minimumWidth() >= 980 and w.minimumHeight() >= 640
