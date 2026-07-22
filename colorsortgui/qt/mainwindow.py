"""메인 윈도우: 사이드바·헤더·통계·탭·썸네일 그리드·분류 워커.

분류는 QThread 워커로 돌린다(open_project 호출). 썸네일은 QThreadPool 러너가
get_thumb를 불러 신호로 아이콘을 채운다. 파일 이동·되돌리기는 전부 project 창구가 한다.
"""
import csv
from pathlib import Path

from PIL import Image
from PySide6.QtCore import (QByteArray, QObject, QRunnable, QSize, Qt, QThread,
                            QThreadPool, QTimer, Signal)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QFileDialog,
                               QFrame, QHBoxLayout, QLabel, QListView,
                               QListWidget, QListWidgetItem, QMainWindow,
                               QProgressBar, QPushButton, QStackedWidget,
                               QVBoxLayout, QWidget)

from colorsort import messages
from colorsort.loading import load_image
from colorsortgui import __version__
from colorsortgui.i18n import tr
from colorsortgui.settings import save_settings
from colorsortgui.thumbcache import get_thumb
from .detail import DetailPage
from .langdialog import LanguageDialog
from .theme import C, qss
from .widgets import StatCard

_TABS = ("all", "blue", "green", "review")
_GROUPS = ("no-signal", "mixed", "other")
_THUMB = 144


class SortWorker(QThread):
    """폴더 하나를 분류한다. UI를 얼리지 않도록 별도 스레드에서 돈다."""
    finished_state = Signal(object)              # ProjectState
    failed = Signal(str)

    def __init__(self, input_root, output_root):
        super().__init__()
        self.input_root, self.output_root = input_root, output_root

    def run(self):
        try:
            from colorsortgui import project      # 테스트 주입 가능하도록 run() 안에서
            state = project.open_project(self.input_root, self.output_root)
            project.apply_copies(state)
            self.finished_state.emit(state)
        except Exception as exc:                  # 워커에서 죽으면 UI가 얼어붙은 것처럼 보인다
            self.failed.emit(str(exc))


class _ThumbSignals(QObject):
    done = Signal(int, str)                       # (row, thumb_path)


class _ThumbRunner(QRunnable):
    """USB는 느리므로 썸네일은 백그라운드 풀에서 만든다."""

    def __init__(self, row, cache_dir, source, fp, signals):
        super().__init__()
        self.row, self.cache_dir = row, cache_dir
        self.source, self.fp, self.signals = source, fp, signals

    def run(self):
        try:
            path = get_thumb(self.cache_dir, self.source, self.fp, _THUMB)
            self.signals.done.emit(self.row, str(path))
        except Exception:
            pass                                  # 썸네일 실패는 치명적이지 않다


class MainWindow(QMainWindow):
    def __init__(self, lang: str, settings: dict):
        super().__init__()
        self._lang = lang
        self._settings = settings if settings is not None else {}
        self._state = None
        self._items: list = []
        self._current = None
        self._input_root = None
        self._tab = "all"
        self._review_group = None
        self._pool = QThreadPool.globalInstance()
        self._thumb_signals = _ThumbSignals()
        self._thumb_signals.done.connect(self._set_thumb)

        self.setWindowTitle(tr("app.title", lang))
        self.setMinimumSize(980, 640)
        self.setAcceptDrops(True)

        central = QWidget(); self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        outer.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_library())     # index 0
        self.detail = DetailPage()
        self.detail.to_blue.connect(lambda: self._set_human("BLUE"))
        self.detail.to_green.connect(lambda: self._set_human("GREEN"))
        self.detail.undone.connect(self._undo)
        self.detail.back.connect(self._show_library)
        self.detail.save_btn.clicked.connect(self._save_png)
        self.stack.addWidget(self.detail)               # index 1
        self.log_page = self._build_log()
        self.stack.addWidget(self.log_page)             # index 2
        self.settings_page = self._build_settings()
        self.stack.addWidget(self.settings_page)        # index 3
        outer.addWidget(self.stack, 1)

        # 창이 커지면 글자도 커진다(2026-07-22 실기 피드백). QSS 재적용은 비싸므로
        # 크기 조절이 멎은 뒤 한 번만, 배율이 실제로 바뀌었을 때만 수행한다.
        self._scale_timer = QTimer(self)
        self._scale_timer.setSingleShot(True)
        self._scale_timer.timeout.connect(self._rescale)

        self._restore_geometry()
        self.set_tab("all")

    # ── 화면 구성 ──
    def _build_sidebar(self) -> QFrame:
        bar = QFrame(); bar.setObjectName("sidebar"); bar.setFixedWidth(184)
        lay = QVBoxLayout(bar)
        logo = QLabel(f"COLOR<span style='color:{C['RED']}'>SORT</span>")
        logo.setTextFormat(Qt.RichText)
        logo.setObjectName("logo")
        lay.addWidget(logo)
        lay.addSpacing(8)
        self.nav = {}
        group = QButtonGroup(self); group.setExclusive(True)
        for key, i18n_key in (("library", "nav.library"), ("review", "nav.review"),
                              ("log", "nav.log"), ("settings", "nav.settings"),
                              ("language", "nav.language")):
            b = QPushButton(tr(i18n_key, self._lang))
            b.setProperty("class", "nav")
            if key == "language":
                # 언어는 화면이 아니라 즉시 실행되는 동작(대화상자)이라 체크 상태를 갖지 않는다.
                b.setCheckable(False)
            else:
                b.setCheckable(True); group.addButton(b)
            lay.addWidget(b); self.nav[key] = b
            b.clicked.connect(lambda _=False, k=key: self._nav(k))
        self.nav["library"].setChecked(True)
        lay.addStretch(1)
        return bar

    def _build_library(self) -> QWidget:
        page = QWidget(); v = QVBoxLayout(page)

        header = QHBoxLayout()
        self.path_chip = QLabel(tr("msg.pick_or_drop", self._lang))
        self.path_chip.setProperty("class", "mono")
        self.path_chip.setStyleSheet(f"color: {C['MUT']};")
        self.choose_btn = QPushButton(tr("btn.choose_folder", self._lang))
        self.choose_btn.clicked.connect(self._choose)
        self.sort_btn = QPushButton(tr("btn.sort", self._lang))
        self.sort_btn.setObjectName("primary")
        self.sort_btn.clicked.connect(self._resort)
        header.addWidget(self.path_chip, 1)
        header.addWidget(self.choose_btn); header.addWidget(self.sort_btn)
        v.addLayout(header)

        self.progress = QProgressBar(); self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        v.addWidget(self.progress)

        stats = QHBoxLayout()
        self.stat_cards = {}
        for key, title_key, accent in (("all", "stat.scanned", C["TEXT"]),
                                       ("blue", "stat.blue", C["BLUE"]),
                                       ("green", "stat.green", C["GREEN"]),
                                       ("review", "stat.review", C["AMBER"])):
            card = StatCard(tr(title_key, self._lang).upper(), accent=accent)
            self.stat_cards[key] = card; stats.addWidget(card)
        v.addLayout(stats)

        tabrow = QHBoxLayout()
        self._tab_group = QButtonGroup(self); self._tab_group.setExclusive(True)
        self._tab_btns = {}
        for name in _TABS:
            b = QPushButton(tr("tab." + name, self._lang))
            b.setCheckable(True); b.setProperty("class", "tab")
            self._tab_group.addButton(b); tabrow.addWidget(b); self._tab_btns[name] = b
            b.clicked.connect(lambda _=False, t=name: self.set_tab(t))
        tabrow.addStretch(1)
        v.addLayout(tabrow)

        chiprow = QHBoxLayout(); chiprow.setContentsMargins(0, 0, 0, 0)
        self._chip_frame = QWidget(); self._chip_frame.setLayout(chiprow)
        self._chip_btns = {}
        for g in _GROUPS:
            b = QPushButton(tr("group." + g, self._lang))
            b.setCheckable(True); b.setProperty("class", "tab")
            chiprow.addWidget(b); self._chip_btns[g] = b
            b.clicked.connect(lambda _=False, gg=g: self._set_group(gg))
        chiprow.addStretch(1)
        self._chip_frame.setVisible(False)
        v.addWidget(self._chip_frame)

        self.grid = QListWidget()
        self.grid.setViewMode(QListView.IconMode)
        self.grid.setIconSize(QSize(_THUMB, _THUMB))
        self.grid.setUniformItemSizes(True)
        self.grid.setResizeMode(QListView.Adjust)
        self.grid.setMovement(QListView.Static)
        self.grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.grid.setSpacing(8)
        self.grid.itemDoubleClicked.connect(self._open_detail)
        v.addWidget(self.grid, 1)
        return page

    # ── 공개 API ──
    def open_folder(self, path: Path) -> None:
        path = Path(path)
        self._input_root = path
        self._settings["last_folder"] = str(path)
        self.path_chip.setText(str(path))
        self.progress.setRange(0, 0)              # 불확정 진행 바
        self.progress.setVisible(True)
        self._worker = SortWorker(path, path / "results")
        self._worker.finished_state.connect(self._on_sorted)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()
        # [B] 결정론적 완료: run()이 끝날 때까지 기다린다. 신호는 큐에 남고 호출자의
        #     이벤트 처리에서 전달된다. UI 블로킹 트레이드오프는 implementation-notes 참조.
        self._worker.wait()

    def current_tab(self) -> str:
        return self._tab

    def visible_count(self) -> int:
        return sum(not self.grid.item(i).isHidden() for i in range(self.grid.count()))

    def set_tab(self, name: str) -> None:
        self._tab = name
        if name in self._tab_btns:
            self._tab_btns[name].setChecked(True)
        is_review = name == "review"
        self._chip_frame.setVisible(is_review)
        if not is_review:
            self._review_group = None
            for b in self._chip_btns.values():
                b.setChecked(False)
        self._apply_filter()

    # ── 내부 동작 ──
    def _set_group(self, g: str) -> None:
        if self._chip_btns[g].isChecked():
            self._review_group = g
            for k, b in self._chip_btns.items():
                if k != g:
                    b.setChecked(False)
        else:
            self._review_group = None
        self._apply_filter()

    def _match(self, item) -> bool:
        sub = item.effective_sub
        if self._tab == "all":
            return True
        if self._tab == "blue":
            return sub == "blue"
        if self._tab == "green":
            return sub == "green"
        if self._tab == "review":
            if not sub.startswith("review"):
                return False
            if self._review_group is None:
                return True
            return sub == "review/" + self._review_group
        return True

    def _apply_filter(self) -> None:
        for i in range(self.grid.count()):
            self.grid.item(i).setHidden(not self._match(self._items[i]))

    def _on_sorted(self, state) -> None:
        self._state = state
        self._items = list(state.items)
        self._populate()
        self._update_counts()
        self.progress.setVisible(False)
        self.set_tab(self._tab)

    def _on_failed(self, msg: str) -> None:
        self.progress.setVisible(False)
        self.path_chip.setText(msg)

    def _populate(self) -> None:
        self.grid.clear()
        cache_dir = self._state.output_root / ".thumbs"
        for i, item in enumerate(self._items):
            text = ("✓ " if item.human else "") + item.path.name
            self.grid.addItem(QListWidgetItem(text))
            self._pool.start(_ThumbRunner(i, cache_dir, item.path, item.fp,
                                          self._thumb_signals))

    def _set_thumb(self, row: int, path: str) -> None:
        if 0 <= row < self.grid.count():
            pix = QPixmap(path)
            if not pix.isNull():
                self.grid.item(row).setIcon(QIcon(pix))

    def _update_counts(self) -> None:
        c = self._state.counts()
        for key, card in self.stat_cards.items():
            card.set_value(c.get(key, 0))

    def _choose(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, tr("btn.choose_folder", self._lang))
        if chosen:
            self.open_folder(Path(chosen))

    def _resort(self) -> None:
        if self._input_root is not None:
            self.open_folder(self._input_root)

    # ── 크게 보기 연결 ──
    def _open_detail(self, li: QListWidgetItem) -> None:
        row = self.grid.row(li)
        self._current = self._items[row]
        rgb = load_image(self._current.path).rgb
        self.detail.show_item(rgb, self._meta(self._current), self._lang)
        self.stack.setCurrentWidget(self.detail)

    def _meta(self, item) -> dict:
        m = item.result.measurements
        return {"name": item.path.name, "peak": int(m.peak), "lit": int(m.n_lit_1),
                "f_blue": float(m.f_blue), "rho_hint": float(m.f_blue),
                "reason_text": messages.render(item.result.decision.reason, self._lang),
                "human": item.human}

    def _show_library(self) -> None:
        self.stack.setCurrentIndex(0)

    def _set_human(self, label: str) -> None:
        if self._current is None:
            return
        import colorsortgui.project as project
        project.set_human(self._state, self._current, label)
        self._refresh_after_change()

    def _undo(self) -> None:
        import colorsortgui.project as project
        project.undo(self._state)
        self._refresh_after_change()

    def _refresh_after_change(self) -> None:
        self._items = list(self._state.items)
        self._populate()
        self._update_counts()
        self._apply_filter()
        self._show_library()

    def _save_png(self) -> None:
        arr = self.detail.current_view_array()
        chosen, _ = QFileDialog.getSaveFileName(
            self, tr("btn.save_png", self._lang), filter="PNG (*.png)")
        if chosen:
            Image.fromarray(arr).save(chosen)

    def _nav(self, key: str) -> None:
        if key == "library":
            self._show_library(); self.set_tab("all")
        elif key == "review":
            self._show_library(); self.set_tab("review")
        elif key == "log":
            self._refresh_log()
            self.stack.setCurrentWidget(self.log_page)
        elif key == "settings":
            self.stack.setCurrentWidget(self.settings_page)
        elif key == "language":
            self._language_dialog()

    # ── 기록 화면 ──
    def _build_log(self) -> QWidget:
        page = QWidget(); v = QVBoxLayout(page)
        title = QLabel(tr("log.title", self._lang).upper())
        title.setProperty("class", "k")
        v.addWidget(title)
        self.log_empty = QLabel(tr("log.empty", self._lang))
        self.log_empty.setProperty("class", "mut")
        self.log_list = QListWidget()
        v.addWidget(self.log_empty)
        v.addWidget(self.log_list, 1)
        return page

    def _refresh_log(self) -> None:
        self.log_list.clear()
        rows = []
        if self._state is not None:
            path = Path(self._state.output_root) / "moves-log.csv"
            if path.exists():
                with open(path, newline="", encoding="utf-8-sig") as f:
                    rows = list(csv.DictReader(f))
        for r in reversed(rows):                       # 최근 것이 위로
            self.log_list.addItem(f"{r.get('time', '')}   {r.get('file', '')}   "
                                  f"{r.get('from', '')} → {r.get('to', '')}")
        self.log_empty.setVisible(not rows)
        self.log_list.setVisible(bool(rows))

    # ── 설정 화면 ──
    def _build_settings(self) -> QWidget:
        page = QWidget(); v = QVBoxLayout(page)
        title = QLabel(tr("nav.settings", self._lang).upper())
        title.setProperty("class", "k")
        v.addWidget(title)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("nav.language", self._lang)))
        self.lang_btn = QPushButton("한국어" if self._lang == "ko" else "English")
        self.lang_btn.clicked.connect(self._language_dialog)
        row.addWidget(self.lang_btn); row.addStretch(1)
        v.addLayout(row)
        note = QLabel(tr("settings.results_note", self._lang))
        note.setProperty("class", "mut"); note.setWordWrap(True)
        v.addWidget(note)
        ver = QLabel(tr("settings.version", self._lang, v=__version__))
        ver.setProperty("class", "mut")
        v.addWidget(ver)
        v.addStretch(1)
        return page

    # ── 언어 전환 ──
    def _language_dialog(self) -> None:
        dlg = LanguageDialog(self)
        if self._lang == "ko":
            dlg.ko.setChecked(True)
        if dlg.exec():
            self._apply_language(dlg.selected())

    def _apply_language(self, lang: str) -> None:
        """언어를 바꾸면 창을 새 언어로 다시 만든다. 모든 문구가 즉시 바뀌고,
        보던 폴더는 자동으로 다시 연다(썸네일 캐시 덕에 몇 초면 끝난다)."""
        if lang == self._lang:
            return
        self._settings["lang"] = lang
        save_settings(self._settings)
        from PySide6.QtWidgets import QApplication
        new = MainWindow(lang=lang, settings=self._settings)
        new.setGeometry(self.geometry())
        QApplication.instance()._colorsort_win = new   # 참조를 붙잡아 GC를 막는다
        new.show()
        if self._input_root is not None:
            new.open_folder(self._input_root)
        self.close()

    # ── 창 크기 연동 글자 배율 ──
    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._scale_timer.start(150)

    def _rescale(self) -> None:
        from PySide6.QtWidgets import QApplication
        scale = max(1.0, min(self.width() / 980.0, 1.5))
        scale = round(scale * 20) / 20               # 0.05 단위 — 미세 변동에 재적용 안 함
        app = QApplication.instance()
        if getattr(app, "_qss_scale", None) != scale:
            app._qss_scale = scale
            app.setStyleSheet(qss(scale))

    # ── 창 상태 ──
    def _restore_geometry(self) -> None:
        g = self._settings.get("geometry")
        if g:
            try:
                self.restoreGeometry(QByteArray.fromBase64(g.encode()))
            except Exception:
                pass

    def closeEvent(self, ev) -> None:
        try:
            self._settings["geometry"] = bytes(self.saveGeometry().toBase64().data()).decode()
        except Exception:
            pass
        super().closeEvent(ev)

    def dragEnterEvent(self, ev) -> None:
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()

    def dropEvent(self, ev) -> None:
        for url in ev.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.is_dir():
                self.open_folder(p)
                break
