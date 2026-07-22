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


def test_nav_switches_pages(qapp, fake_project):
    w = MainWindow(lang="en", settings={})
    w.nav["log"].click()
    assert w.stack.currentWidget() is w.log_page
    w.nav["settings"].click()
    assert w.stack.currentWidget() is w.settings_page
    w.nav["review"].click()
    assert w.stack.currentIndex() == 0 and w.current_tab() == "review"
    w.nav["library"].click()
    assert w.stack.currentIndex() == 0 and w.current_tab() == "all"


def test_log_page_reads_moves_csv(qapp, tmp_path, fake_project):
    (tmp_path / "moves-log.csv").write_text(
        "time,file,fingerprint,from,to\n"
        "2026-07-22T10:00:00,x.png,ab,review/other,blue\n",
        encoding="utf-8-sig")
    w = MainWindow(lang="en", settings={})
    w.open_folder(Path("/fake")); qapp.processEvents()
    w._state.output_root = tmp_path                 # 가짜 상태의 출력 폴더를 실제 tmp로
    w.nav["log"].click()
    assert w.log_list.count() == 1
    assert "x.png" in w.log_list.item(0).text()
    assert w.log_empty.isHidden()


def test_log_page_empty_state(qapp, fake_project):
    w = MainWindow(lang="en", settings={})
    w.nav["log"].click()
    assert w.log_list.count() == 0 and not w.log_empty.isHidden()


def test_apply_language_recreates_window(qapp, fake_project, monkeypatch, tmp_path):
    import colorsortgui.settings as st
    monkeypatch.setattr(st, "settings_dir", lambda: tmp_path)   # 설정 저장을 tmp로
    w = MainWindow(lang="en", settings={})
    w._apply_language("ko")
    new = qapp._colorsort_win
    assert new is not w and new._lang == "ko"
    assert new.nav["library"].text() == "라이브러리"
    new.close()
