"""04-class-diagram.png — UML 클래스 다이어그램.

읽은 코드: colorsort/models.py, colorsort/config.py, colorsortgui/project.py,
colorsortgui/decisions.py, colorsortgui/qt/*.py. 필드·메서드·상속은 코드 그대로.
3그룹(코어 데이터 / GUI 상태 / Qt 화면)을 배경 밴드로 구분한다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, band, rbox, label, arrow, line, diamond,
                     hollow_tri, save, INK, INK2, MUTED, FAINT, GRID, AXIS,
                     WHITE, BLUE, GREEN, VIOLET, AMBER, TEAL, BAND_CORE,
                     BAND_GUI, BAND_QT, NEUTRAL_FILL)

W, H = 18.3, 22.4
fig, ax = new_fig(W, H)

RECTS = {}
NAME_H, LH, PADY = 0.62, 0.32, 0.11


def class_box(key, x, y, w, name, fields, methods, note,
              accent=INK, fill=WHITE, stereo=None, base=None, signals=None):
    signals = signals or []
    body = signals + fields
    fh = (len(body) * LH + 2 * PADY) if body else 0.0
    mh = (len(methods) * LH + 2 * PADY) if methods else 0.0
    h = NAME_H + fh + mh
    rbox(ax, x, y, w, h, fc=fill, ec=accent, lw=1.9, rounding=0.10)
    cx = x + w / 2
    label(ax, cx, y + 0.26, name, size=16.5, weight="bold", color=accent)
    if base is not None:
        hollow_tri(ax, x + 0.32, y + 0.5, size=0.1, point="right",
                   ec=accent, fc=WHITE)
        label(ax, x + 0.5, y + 0.5, base + " 상속", size=11, color=MUTED,
              ha="left", style="italic")
    elif stereo:
        label(ax, cx, y + 0.5, stereo, size=11, color=MUTED, style="italic")
    yy = y + NAME_H
    line(ax, (x + 0.05, yy), (x + w - 0.05, yy), color=accent, lw=1.1)
    if body:
        for i, f in enumerate(body):
            col = TEAL if i < len(signals) else INK2
            txt = ("«Signal» " + f) if i < len(signals) else f
            label(ax, x + 0.2, yy + PADY + 0.16 + i * LH, txt, size=13,
                  color=col, ha="left")
        yy += fh
        if methods:
            line(ax, (x + 0.05, yy), (x + w - 0.05, yy), color=GRID, lw=1.0)
    for i, m in enumerate(methods):
        label(ax, x + 0.2, yy + PADY + 0.16 + i * LH, m, size=13,
              color=INK2, ha="left")
    label(ax, x + 0.04, y + h + 0.24, note, size=12.5, color=MUTED,
          ha="left", va="top", style="italic")
    RECTS[key] = (x, y, w, h)
    return h


def edge(key, side):
    x, y, w, h = RECTS[key]
    return {"top": (x + w / 2, y), "bottom": (x + w / 2, y + h),
            "left": (x, y + h / 2), "right": (x + w, y + h / 2),
            "tl": (x + w * 0.28, y), "tr": (x + w * 0.72, y),
            "bl": (x + w * 0.28, y + h), "br": (x + w * 0.72, y + h)}[side]


def aggregation(whole, wside, part, pside, accent=INK, label_text=None,
                filled=True):
    p1, p2 = edge(whole, wside), edge(part, pside)
    line(ax, p1, p2, color=accent, lw=1.7, z=3)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    d = (dx * dx + dy * dy) ** 0.5 or 1
    diamond(ax, p1[0] + dx / d * 0.19, p1[1] + dy / d * 0.19, r=0.12,
            fc=(accent if filled else WHITE), ec=accent)
    if label_text:
        label(ax, (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 0.15, label_text,
              size=11, color=MUTED, style="italic")


def assoc(fr, fside, to, tside, accent=INK, label_text=None, dashed=False,
          cs=None, lpos=0.5):
    p1, p2 = edge(fr, fside), edge(to, tside)
    arrow(ax, p1, p2, color=accent, lw=1.8, ls=("--" if dashed else "-"),
          style="-|>", ms=13, z=4, cs=cs)
    if label_text:
        label(ax, p1[0] + (p2[0] - p1[0]) * lpos + 0.3,
              p1[1] + (p2[1] - p1[1]) * lpos, label_text, size=11,
              color=MUTED, style="italic", ha="left")


def band_header(y, left, caption, accent):
    label(ax, 0.62, y + 0.29, left, size=15, weight="bold", color=accent,
          ha="left")
    label(ax, W - 0.55, y + 0.29, caption, size=12.5, color=MUTED,
          ha="right", style="italic")


# ── 제목 ──
label(ax, W / 2, 0.4, "클래스 지도 — 이 프로그램을 이루는 부품들",
      size=25, weight="bold", color=INK)
label(ax, W / 2, 0.78,
      "네모 하나가 부품(클래스) 하나입니다. 코드의 실제 필드·메서드·상속 관계를 그대로 옮겼습니다.",
      size=13.5, color=MUTED)

# ── 밴드 ──
band(ax, 0.35, 1.0, W - 0.7, 7.45, BAND_CORE)
band(ax, 0.35, 8.7, W - 0.7, 4.05, BAND_GUI)
band(ax, 0.35, 13.0, W - 0.7, 9.1, BAND_QT)
band_header(1.0, "코어 데이터  ·  colorsort", "판정 파이프라인이 주고받는 값(모두 frozen)", BLUE)
band_header(8.7, "GUI 상태  ·  colorsortgui", "v1 판정 위에 사람 확정을 겹친다", TEAL)
band_header(13.0, "Qt 화면  ·  colorsortgui/qt", "PySide6 위젯 — 각자 Qt 기본 클래스를 상속", VIOLET)

# ── 코어 데이터 (윗줄: 파이프라인 순서, FileResult는 두 부품을 품으므로 아래 가운데) ──
class_box("LoadResult", 0.55, 1.65, 2.95, "LoadResult",
          ["path: Path", "rgb: ndarray (H,W,3)", "width, height, file_bytes",
           "has_transparent_pixels", "palette_size, load_error"], [],
          "PNG 한 장을 읽은 결과", accent=BLUE, stereo="«frozen»")
class_box("Measurements", 4.05, 1.65, 3.2, "Measurements",
          ["gate_used: int|None", "n_blue, n_green", "n_intermediate, n_gated",
           "peak, energy_blue/green", "…  (통계 11개)"],
          ["is_low_confidence", "f_blue", "f_blue_energy"],
          "픽셀 색 통계 · 계산 속성 3개", accent=BLUE, stereo="«frozen»")
class_box("Decision", 7.5, 1.65, 3.05, "Decision",
          ["label: str", "   BLUE|GREEN|HYBRID|ABSTAIN", "reason: Msg",
           "low_confidence: bool", "warnings: tuple[Msg,…]"],
          ["reason_code", "folder(config)"],
          "판정 결과 + 이유", accent=BLUE, stereo="«frozen»")
class_box("Msg", 10.75, 1.65, 2.6, "Msg",
          ["key: str", "params: Mapping"], [],
          "언어 독립 메시지\n(열쇠+숫자만, 문장은 나중에)", accent=BLUE, stereo="«frozen»")
class_box("CopyItem", 13.65, 1.65, 2.5, "CopyItem",
          ["source: Path", "dest: Path", "label: str"], [],
          "원본→사본 복사 계획", accent=BLUE, stereo="«frozen»")
class_box("Config", 0.55, 4.75, 3.2, "Config",
          ["rho_blue=0.90, rho_green=0.35", "gates=(5,2,1), n_min=30",
           "minority_floor=50", "max_intermediate_frac=0.10",
           "purity_eps=0.02", "consistency_max=0.10"], [],
          "판정 임계값 — 코드가 아닌 데이터\nfolder_blue / green / review",
          accent=INK, fill=NEUTRAL_FILL, stereo="«설정값 frozen»")
class_box("FileResult", 6.6, 6.05, 2.95, "FileResult",
          ["path: Path", "measurements", "decision"], [],
          "한 장의 전체 결과\n(CSV 한 줄에 대응)", accent=BLUE, stereo="«frozen»")

# ── GUI 상태 (ProjectState가 가운데서 양쪽을 품는다) ──
class_box("DecisionStore", 0.8, 9.3, 3.2, "DecisionStore",
          ["path: Path", "_d: dict"], ["get / set / remove", "count"],
          "사람 확정 저장 (decisions.json)\n지문(fingerprint)이 열쇠", accent=TEAL,
          stereo="«상태»")
class_box("ProjectState", 5.15, 9.3, 3.75, "ProjectState",
          ["input_root, output_root", "items: list[PhotoItem]",
           "store: DecisionStore", "n_excluded, undo_stack"], ["counts()"],
          "프로젝트 전체 상태", accent=TEAL, stereo="«상태»")
class_box("PhotoItem", 10.05, 9.3, 3.7, "PhotoItem",
          ["path, rel, fp", "result: FileResult", "machine_sub: str",
           "human: str|None"], ["effective_sub", "dest_name / dest"],
          "사진 1장 + 사람 확정(human)을 겹침", accent=TEAL, stereo="«상태»")

# ── Qt 화면 ──
class_box("MainWindow", 0.7, 13.75, 4.3, "MainWindow",
          ["_state, _items, _current", "stack, detail, grid",
           "stat_cards, _pool", "_thumb_signals"],
          ["open_folder()", "_on_sorted()", "_open_detail()",
           "_set_human() / _undo()"],
          "메인 창 — 사이드바·통계·그리드·워커 총괄", accent=VIOLET,
          base="QMainWindow")
class_box("SortWorker", 5.4, 13.75, 3.5, "SortWorker",
          ["input_root, output_root"], ["run()"],
          "폴더 하나를 백그라운드에서 분류", accent=VIOLET, base="QThread",
          signals=["finished_state", "failed"])
class_box("ThumbSignals", 9.3, 13.75, 3.0, "_ThumbSignals", [], [],
          "썸네일 완료 신호를 운반\n(QRunnable은 신호를 못 냄)", accent=VIOLET,
          base="QObject", signals=["done(row, path)"])
class_box("ThumbRunner", 12.7, 13.75, 3.4, "_ThumbRunner",
          ["row, cache_dir", "source, fp, signals"], ["run()"],
          "썸네일 1장을 백그라운드 생성", accent=VIOLET, base="QRunnable")
class_box("DetailPage", 0.7, 18.2, 3.9, "DetailPage",
          ["view: ZoomView", "ruler: RhoRuler"],
          ["show_item()", "current_view_array()", "set_view_mode()"],
          "크게 보기 + 검사관 카드", accent=VIOLET, base="QWidget",
          signals=["to_blue / to_green", "undone / back"])
class_box("ZoomView", 4.9, 18.2, 3.2, "ZoomView",
          ["_item"], ["set_array()", "wheelEvent()", "mouseMoveEvent()"],
          "확대·이동 이미지 뷰", accent=VIOLET, base="QGraphicsView",
          signals=["probed(x, y)"])
class_box("RhoRuler", 8.4, 18.2, 2.85, "RhoRuler",
          ["rho: float"], ["set_rho()", "paintEvent()"],
          "ρ 눈금자 (경계 0.35 / 0.90)", accent=VIOLET, base="QWidget")
class_box("StatCard", 11.5, 18.2, 2.4, "StatCard",
          ["value_label"], ["set_value()"],
          "첫 화면 통계 카드", accent=VIOLET, base="QFrame")
class_box("LangDialog", 14.15, 18.2, 2.5, "LanguageDialog",
          ["en, ko: QRadioButton"], ["selected()"],
          "첫 실행 언어 선택", accent=VIOLET, base="QDialog")

# ── 관계선 ──
aggregation("FileResult", "tl", "Measurements", "bottom", accent=BLUE)
aggregation("FileResult", "tr", "Decision", "bottom", accent=BLUE)
aggregation("Decision", "right", "Msg", "left", accent=BLUE)
aggregation("ProjectState", "left", "DecisionStore", "right", accent=TEAL)
aggregation("ProjectState", "right", "PhotoItem", "left", accent=TEAL)
assoc("PhotoItem", "top", "FileResult", "bottom", accent=TEAL,
      label_text="result", lpos=0.55)
assoc("MainWindow", "tr", "ProjectState", "bl", accent=VIOLET,
      cs="arc3,rad=0.12")
assoc("MainWindow", "right", "SortWorker", "left", accent=VIOLET)
assoc("MainWindow", "bottom", "DetailPage", "top", accent=VIOLET)
assoc("ThumbRunner", "left", "ThumbSignals", "right", accent=FAINT,
      dashed=True)
aggregation("DetailPage", "right", "ZoomView", "left", accent=VIOLET,
            filled=False)

# ── 범례 (오른쪽 아래 빈 자리) ──
lx, ly = 11.45, 20.35
rbox(ax, lx, ly, 5.15, 1.5, fc=WHITE, ec=AXIS, lw=1.3, rounding=0.07)
label(ax, lx + 0.2, ly + 0.3, "관계 기호 읽는 법", size=13, weight="bold",
      color=INK, ha="left")
diamond(ax, lx + 0.34, ly + 0.66, r=0.1, fc=INK, ec=INK)
line(ax, (lx + 0.44, ly + 0.66), (lx + 0.85, ly + 0.66), color=INK, lw=1.5)
label(ax, lx + 0.98, ly + 0.66, "포함 — 한 부품이 다른 부품을 품음", size=11.5,
      color=INK2, ha="left")
hollow_tri(ax, lx + 0.34, ly + 0.98, size=0.11, point="right", ec=INK, fc=WHITE)
line(ax, (lx + 0.45, ly + 0.98), (lx + 0.85, ly + 0.98), color=INK, lw=1.5)
label(ax, lx + 0.98, ly + 0.98, "상속 — Qt 기본 클래스를 물려받음", size=11.5,
      color=INK2, ha="left")
arrow(ax, (lx + 0.18, ly + 1.28), (lx + 0.85, ly + 1.28), color=INK, lw=1.6,
      style="-|>", ms=11)
label(ax, lx + 0.98, ly + 1.28, "참조·사용   ·   점선 = 신호/백그라운드",
      size=11.5, color=INK2, ha="left")
arrow(ax, (lx + 0.18, ly + 1.28), (lx + 0.62, ly + 1.28), color=FAINT, lw=1.6,
      style="-|>", ms=11, ls="--")

out = Path(__file__).resolve().parent.parent / "04-class-diagram.png"
save(fig, out)
print("saved", out)
