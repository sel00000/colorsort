import types
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


def test_window_resize_scales_fonts(qapp, fake_project):
    w = MainWindow(lang="en", settings={})
    w.resize(1600, 900)
    w._rescale()                                   # 타이머 대신 직접 호출
    assert qapp._qss_scale > 1.0
    w.resize(980, 640)
    w._rescale()
    assert qapp._qss_scale == 1.0


def test_sidebar_grows_to_fit_texts(qapp, fake_project):
    """고정 폭 회귀 방지 — 사이드바 요구 폭이 로고·메뉴 글자 요구 폭보다 작으면 안 된다."""
    from PySide6.QtWidgets import QFrame, QLabel
    w = MainWindow(lang="ko", settings={})
    bar = w.findChild(QFrame, "sidebar")
    logo = w.findChild(QLabel, "logo")
    assert bar.sizeHint().width() >= logo.sizeHint().width()
    for b in w.nav.values():
        assert bar.sizeHint().width() >= b.sizeHint().width()


def test_grid_cells_and_sidebar_hold_shape(qapp, fake_project):
    """아이콘 지각 도착에도 칸이 안 찌그러지고, 사이드바는 압축되지 않는다."""
    from PySide6.QtWidgets import QFrame, QSizePolicy
    w = MainWindow(lang="en", settings={})
    assert w.grid.gridSize().width() >= 144 and w.grid.gridSize().height() >= 144 + 40
    bar = w.findChild(QFrame, "sidebar")
    assert bar.sizePolicy().horizontalPolicy() == QSizePolicy.Fixed


# ── 빈 결과 안내 (사진 0장) ──
def _empty_state(n_excluded=0):
    """사진 0장 상태. n_excluded>0이면 전부 이전 결과 폴더 사본이라 제외된 경우."""
    return types.SimpleNamespace(
        input_root=Path("/fake"), output_root=Path("/fake/results"),
        items=[], store=None, n_excluded=n_excluded, undo_stack=[],
        counts=lambda: {"all": 0, "blue": 0, "green": 0, "review": 0,
                        "no-signal": 0, "mixed": 0, "other": 0})


def _one_photo_state():
    it = types.SimpleNamespace(path=Path("/fake/x.png"), rel="x.png", fp="x_png",
                               result=None, machine_sub="blue", human=None,
                               effective_sub="blue", dest="blue/x.png")
    return types.SimpleNamespace(
        input_root=Path("/fake"), output_root=Path("/fake/results"),
        items=[it], store=None, n_excluded=0, undo_stack=[],
        counts=lambda: {"all": 1, "blue": 1, "green": 0, "review": 0,
                        "no-signal": 0, "mixed": 0, "other": 0})


def test_empty_folder_shows_notice(qapp, monkeypatch):
    """분류 결과 0장이면 그리드 대신 안내 라벨이 뜬다."""
    import colorsortgui.project as project
    from colorsortgui.i18n import tr
    st = _empty_state()
    monkeypatch.setattr(project, "open_project", lambda inp, out: st)
    monkeypatch.setattr(project, "apply_copies", lambda s: (0, []))
    w = MainWindow(lang="ko", settings={})
    w.open_folder(Path("/fake")); qapp.processEvents()
    assert not w.empty_notice.isHidden()
    assert w.grid.isHidden()
    assert w.visible_count() == 0
    assert w.empty_notice.text() == tr("err.no_photos", "ko")


def test_photos_hide_empty_notice(qapp, fake_project):
    """사진이 있으면 안내는 숨고 그리드가 보인다."""
    w = MainWindow(lang="en", settings={})
    w.open_folder(Path("/fake")); qapp.processEvents()
    assert w.empty_notice.isHidden()
    assert not w.grid.isHidden()


def test_all_excluded_shows_distinct_notice(qapp, monkeypatch):
    """0장이지만 전부 이전 결과 폴더라 제외된 경우, '사진 없음'이 아니라 제외 안내를 보인다."""
    import colorsortgui.project as project
    from colorsortgui.i18n import tr
    st = _empty_state(n_excluded=5)
    monkeypatch.setattr(project, "open_project", lambda inp, out: st)
    monkeypatch.setattr(project, "apply_copies", lambda s: (0, []))
    w = MainWindow(lang="ko", settings={})
    w.open_folder(Path("/fake")); qapp.processEvents()
    assert not w.empty_notice.isHidden() and w.grid.isHidden()
    assert w.empty_notice.text() == tr("err.all_excluded", "ko", n=5)
    assert "5" in w.empty_notice.text()
    assert w.empty_notice.text() != tr("err.no_photos", "ko")


def test_notice_clears_on_reopen_with_photos(qapp, monkeypatch):
    """빈 폴더 뒤 사진 있는 폴더를 다시 열면 안내가 사라지고 그리드가 돌아온다."""
    import colorsortgui.project as project
    cur = {"state": _empty_state()}
    monkeypatch.setattr(project, "open_project", lambda inp, out: cur["state"])
    monkeypatch.setattr(project, "apply_copies", lambda s: (len(s.items), []))
    w = MainWindow(lang="en", settings={})
    w.open_folder(Path("/fake")); qapp.processEvents()
    assert not w.empty_notice.isHidden()          # 처음엔 빈 상태
    cur["state"] = _one_photo_state()
    w.open_folder(Path("/fake")); qapp.processEvents()
    assert w.empty_notice.isHidden()              # 갱신되어 사라짐
    assert not w.grid.isHidden()
