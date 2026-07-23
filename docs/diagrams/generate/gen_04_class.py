"""04-class-diagram.png / 04-class-diagram-en.png — UML 클래스 다이어그램.

읽은 코드: colorsort/models.py, colorsort/config.py, colorsortgui/project.py,
colorsortgui/decisions.py, colorsortgui/qt/*.py. 필드·메서드·상속은 코드 그대로.
3그룹(코어 데이터 / GUI 상태 / Qt 화면)을 배경 밴드로 구분한다.

실행: python3 gen_04_class.py ko | en
글자 +20pt·bold 는 _common.py 가 자동 적용한다. 필드/메서드는 전부 식별자라
번역하지 않고, 상자 아래 이탤릭 설명·«스테레오타입»·밴드 머리글만 번역한다.
'상속' 꼬리표는 클래스 이름을 건드리지 않도록 문장 틀만 언어별로 바꾼다.
주의: 7250×8932px(약 65메가픽셀)이라 렌더 한 번에 수십 초 걸린다 — 정상이다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, band, rbox, label, arrow, line, diamond,
                     hollow_tri, save, get_lang, suffix,
                     INK, INK2, MUTED, FAINT, GRID, AXIS,
                     WHITE, BLUE, VIOLET, TEAL, BAND_CORE,
                     BAND_GUI, BAND_QT, NEUTRAL_FILL)

LANG = get_lang()
SUF = suffix(LANG)

# ── 영어 번역표 (키 = 한글 원문 그대로, 줄바꿈 포함) ──
# 필드·메서드·클래스명은 전부 코드의 식별자라 번역하지 않는다.
EN = {
    "클래스 지도 — 이 프로그램을 이루는 부품들":
        "Class Map — the Parts of This Program",
    "네모 하나가 부품(클래스) 하나입니다. 코드의 실제 필드·메서드·상속 관계를 그대로 옮겼습니다.":
        "Each box is one part (class). Fields, methods and inheritance are "
        "taken directly from the code.",
    # 밴드 머리글
    "코어 데이터  ·  colorsort": "Core data  ·  colorsort",
    "판정 파이프라인이 주고받는 값(모두 frozen)":
        "values the verdict pipeline passes around (all frozen)",
    "GUI 상태  ·  colorsortgui": "GUI state  ·  colorsortgui",
    "v1 판정 위에 사람 확정을 겹친다":
        "human confirmation layered on the v1 verdict",
    "Qt 화면  ·  colorsortgui/qt": "Qt screens  ·  colorsortgui/qt",
    "PySide6 위젯 — 각자 Qt 기본 클래스를 상속":
        "PySide6 widgets — each extends a Qt base class",
    # «스테레오타입» («frozen» 은 UML 낱말이라 그대로 두되 t()를 거치므로 등록)
    "«frozen»": "«frozen»",
    "«설정값 frozen»": "«settings frozen»",
    "«상태»": "«state»",
    # 필드 중 유일하게 식별자가 아닌 줄
    "…  (통계 11개)": "…  (11 stats)",
    # 상자 아래 이탤릭 설명
    "PNG 한 장을 읽은 결과": "one PNG file, read",
    "픽셀 색 통계 · 계산 속성 3개": "color stats · 3 computed properties",
    "판정 결과 + 이유": "verdict + reason",
    "언어 독립 메시지\n(열쇠+숫자만,\n문장은 나중에)":
        "language-independent\nmessage (key + numbers,\nwording comes later)",
    "원본→사본\n복사 계획": "original →\ncopy plan",
    "판정 임계값 — 코드가 아닌 데이터\nfolder_blue / green / review":
        "verdict thresholds — data, not code\nfolder_blue / green / review",
    "한 장의 전체 결과\n(CSV 한 줄에 대응)":
        "the full result for one photo\n(one CSV row)",
    "사람 확정 저장 (decisions.json)\n지문(fingerprint)이 열쇠":
        "human confirmations\n(decisions.json)\nthe fingerprint is the key",
    "프로젝트 전체 상태": "whole project state",
    "사진 1장 + 사람 확정(human)을 겹침":
        "one photo + the human confirmation (human)",
    "메인 창 — 사이드바·통계·그리드·워커 총괄":
        "main window — sidebar, stats, grid, worker",
    "폴더 하나를 백그라운드에서 분류": "sorts one folder in the background",
    "썸네일 완료 신호를 운반\n(QRunnable은 신호를 못 냄)":
        "carries the thumbnail-done signal\n(a QRunnable cannot emit signals)",
    "썸네일 1장을 백그라운드 생성": "builds one thumbnail\nin the background",
    "크게 보기 + 검사관 카드": "detail view + inspector card",
    "확대·이동 이미지 뷰": "zoom & pan image view",
    "ρ 눈금자 (경계 0.35 / 0.90)": "ρ ruler (borders 0.35 / 0.90)",
    "첫 화면 통계 카드": "first-screen stat card",
    "첫 실행 언어 선택": "language pick on first run",
    # 범례
    "관계 기호 읽는 법": "How to read the relation symbols",
    "포함 — 한 부품이 다른 부품을 품음": "contains — one part holds another",
    "상속 — Qt 기본 클래스를 물려받음": "inherits — from a Qt base class",
    "참조·사용   ·   점선 = 신호/백그라운드":
        "uses  ·  dashed = signal / background",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


def extends(base):
    """'상속' 꼬리표. 클래스 이름(base)은 식별자라 번역하지 않는다."""
    return f"{base} 상속" if LANG == "ko" else f"extends {base}"


W, H = 25.0, 30.8
fig, ax = new_fig(W, H)

RECTS = {}
NAME_H, LH, PADY = 1.00, 0.45, 0.15
NOTE_GAP = 0.24


def class_box(key, x, y, w, name, fields, methods, note,
              accent=INK, fill=WHITE, stereo=None, base=None, signals=None):
    signals = signals or []
    body = signals + fields
    fh = (len(body) * LH + 2 * PADY) if body else 0.0
    mh = (len(methods) * LH + 2 * PADY) if methods else 0.0
    h = NAME_H + fh + mh
    rbox(ax, x, y, w, h, fc=fill, ec=accent, lw=1.9, rounding=0.10)
    cx = x + w / 2
    label(ax, cx, y + 0.38, name, size=16.5, weight="bold", color=accent)
    if base is not None:
        hollow_tri(ax, x + 0.34, y + 0.80, size=0.13, point="right",
                   ec=accent, fc=WHITE)
        label(ax, x + 0.56, y + 0.80, extends(base), size=11, color=MUTED,
              ha="left", style="italic")
    elif stereo:
        label(ax, cx, y + 0.80, t(stereo), size=11, color=MUTED, style="italic")
    yy = y + NAME_H
    line(ax, (x + 0.05, yy), (x + w - 0.05, yy), color=accent, lw=1.1)
    if body:
        for i, f in enumerate(body):
            col = TEAL if i < len(signals) else INK2
            txt = ("«Signal» " + f) if i < len(signals) else f
            label(ax, x + 0.22, yy + PADY + 0.22 + i * LH, txt, size=13,
                  color=col, ha="left")
        yy += fh
        if methods:
            line(ax, (x + 0.05, yy), (x + w - 0.05, yy), color=GRID, lw=1.0)
    for i, m in enumerate(methods):
        label(ax, x + 0.22, yy + PADY + 0.22 + i * LH, m, size=13,
              color=INK2, ha="left")
    label(ax, x + 0.04, y + h + NOTE_GAP, t(note), size=12.5, color=MUTED,
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
    diamond(ax, p1[0] + dx / d * 0.24, p1[1] + dy / d * 0.24, r=0.15,
            fc=(accent if filled else WHITE), ec=accent)
    if label_text:
        label(ax, (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 0.20, label_text,
              size=11, color=MUTED, style="italic")


def assoc(fr, fside, to, tside, accent=INK, label_text=None, dashed=False,
          cs=None, lpos=0.5):
    p1, p2 = edge(fr, fside), edge(to, tside)
    arrow(ax, p1, p2, color=accent, lw=1.8, ls=("--" if dashed else "-"),
          style="-|>", ms=13, z=4, cs=cs)
    if label_text:
        label(ax, p1[0] + (p2[0] - p1[0]) * lpos + 0.4,
              p1[1] + (p2[1] - p1[1]) * lpos, label_text, size=11,
              color=MUTED, style="italic", ha="left")


def band_header(y, left, caption, accent):
    label(ax, 0.62, y + 0.45, t(left), size=15, weight="bold", color=accent,
          ha="left")
    label(ax, W - 0.55, y + 0.45, t(caption), size=12.5, color=MUTED,
          ha="right", style="italic")


# ── 제목 ──
label(ax, W / 2, 0.60, t("클래스 지도 — 이 프로그램을 이루는 부품들"),
      size=25, weight="bold", color=INK)
label(ax, W / 2, 1.25,
      t("네모 하나가 부품(클래스) 하나입니다. 코드의 실제 필드·메서드·상속 관계를 그대로 옮겼습니다."),
      size=13.5, color=MUTED)

# ── 밴드 (내용 높이에 맞춰 다시 계산한 값) ──
band(ax, 0.35, 1.75, W - 0.7, 10.45, BAND_CORE)
band(ax, 0.35, 12.50, W - 0.7, 6.02, BAND_GUI)
band(ax, 0.35, 18.82, W - 0.7, 11.69, BAND_QT)
band_header(1.75, "코어 데이터  ·  colorsort",
            "판정 파이프라인이 주고받는 값(모두 frozen)", BLUE)
band_header(12.50, "GUI 상태  ·  colorsortgui", "v1 판정 위에 사람 확정을 겹친다",
            TEAL)
band_header(18.82, "Qt 화면  ·  colorsortgui/qt",
            "PySide6 위젯 — 각자 Qt 기본 클래스를 상속", VIOLET)

# ── 코어 데이터 (윗줄: 파이프라인 순서, FileResult는 두 부품을 품으므로 아래 가운데) ──
class_box("LoadResult", 0.55, 2.55, 4.25, "LoadResult",
          ["path: Path", "rgb: ndarray (H,W,3)", "width, height, file_bytes",
           "has_transparent_pixels", "palette_size, load_error"], [],
          "PNG 한 장을 읽은 결과", accent=BLUE, stereo="«frozen»")
class_box("Measurements", 6.20, 2.55, 4.10, "Measurements",
          ["gate_used: int|None", "n_blue, n_green", "n_intermediate, n_gated",
           "peak, energy_blue/green", t("…  (통계 11개)")],
          ["is_low_confidence", "f_blue / f_blue_energy"],
          "픽셀 색 통계 · 계산 속성 3개", accent=BLUE, stereo="«frozen»")
class_box("Decision", 11.60, 2.55, 5.30, "Decision",
          ["label: str", "   BLUE|GREEN|HYBRID|ABSTAIN", "reason: Msg",
           "low_confidence: bool", "warnings: tuple[Msg,…]"],
          ["reason_code", "folder(config)"],
          "판정 결과 + 이유", accent=BLUE, stereo="«frozen»")
class_box("Msg", 17.90, 2.55, 2.95, "Msg",
          ["key: str", "params: Mapping"], [],
          "언어 독립 메시지\n(열쇠+숫자만,\n문장은 나중에)", accent=BLUE,
          stereo="«frozen»")
class_box("CopyItem", 22.10, 2.55, 2.40, "CopyItem",
          ["source: Path", "dest: Path", "label: str"], [],
          "원본→사본\n복사 계획", accent=BLUE, stereo="«frozen»")
class_box("Config", 0.55, 7.02, 5.35, "Config",
          ["rho_blue=0.90, rho_green=0.35", "gates=(5,2,1), n_min=30",
           "minority_floor=50", "max_intermediate_frac=0.10",
           "purity_eps=0.02", "consistency_max=0.10"], [],
          "판정 임계값 — 코드가 아닌 데이터\nfolder_blue / green / review",
          accent=INK, fill=NEUTRAL_FILL, stereo="«설정값 frozen»")
class_box("FileResult", 9.60, 8.22, 2.50, "FileResult",
          ["path: Path", "measurements", "decision"], [],
          "한 장의 전체 결과\n(CSV 한 줄에 대응)", accent=BLUE, stereo="«frozen»")

# ── GUI 상태 (ProjectState가 가운데서 양쪽을 품는다) ──
class_box("DecisionStore", 0.80, 13.30, 3.20, "DecisionStore",
          ["path: Path", "_d: dict"], ["get / set / remove", "count"],
          "사람 확정 저장 (decisions.json)\n지문(fingerprint)이 열쇠", accent=TEAL,
          stereo="«상태»")
class_box("ProjectState", 5.60, 13.30, 4.00, "ProjectState",
          ["input_root, output_root", "items: list[PhotoItem]",
           "store: DecisionStore", "n_excluded, undo_stack"], ["counts()"],
          "프로젝트 전체 상태", accent=TEAL, stereo="«상태»")
class_box("PhotoItem", 11.20, 13.30, 3.20, "PhotoItem",
          ["path, rel, fp", "result: FileResult", "machine_sub: str",
           "human: str|None"], ["effective_sub", "dest_name / dest"],
          "사진 1장 + 사람 확정(human)을 겹침", accent=TEAL, stereo="«상태»")

# ── Qt 화면 ──
class_box("MainWindow", 1.10, 19.62, 4.60, "MainWindow",
          ["_state, _items, _current", "stack, detail, grid",
           "stat_cards, _pool", "_thumb_signals"],
          ["open_folder() / _on_sorted()", "_open_detail()",
           "_set_human() / _undo()"],
          "메인 창 — 사이드바·통계·그리드·워커 총괄", accent=VIOLET,
          base="QMainWindow")
class_box("SortWorker", 7.10, 19.62, 4.30, "SortWorker",
          ["input_root, output_root"], ["run()"],
          "폴더 하나를 백그라운드에서 분류", accent=VIOLET, base="QThread",
          signals=["finished_state", "failed"])
class_box("ThumbSignals", 13.00, 19.62, 4.30, "_ThumbSignals", [], [],
          "썸네일 완료 신호를 운반\n(QRunnable은 신호를 못 냄)", accent=VIOLET,
          base="QObject", signals=["done(row, path)"])
class_box("ThumbRunner", 19.00, 19.62, 3.50, "_ThumbRunner",
          ["row, cache_dir", "source, fp, signals"], ["run()"],
          "썸네일 1장을 백그라운드 생성", accent=VIOLET, base="QRunnable")
class_box("DetailPage", 1.10, 25.29, 4.95, "DetailPage",
          ["view: ZoomView", "ruler: RhoRuler"],
          ["show_item() / set_view_mode()", "current_view_array()"],
          "크게 보기 + 검사관 카드", accent=VIOLET, base="QWidget",
          signals=["to_blue / to_green", "undone / back"])
class_box("ZoomView", 6.50, 25.29, 4.15, "ZoomView",
          ["_item"], ["set_array()", "wheelEvent()", "mouseMoveEvent()"],
          "확대·이동 이미지 뷰", accent=VIOLET, base="QGraphicsView",
          signals=["probed(x, y)"])
class_box("RhoRuler", 11.20, 25.29, 3.10, "RhoRuler",
          ["rho: float"], ["set_rho()", "paintEvent()"],
          "ρ 눈금자 (경계 0.35 / 0.90)", accent=VIOLET, base="QWidget")
class_box("StatCard", 14.90, 25.29, 2.95, "StatCard",
          ["value_label"], ["set_value()"],
          "첫 화면 통계 카드", accent=VIOLET, base="QFrame")
class_box("LangDialog", 18.40, 25.29, 3.55, "LanguageDialog",
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
# 설명글이 두 상자 사이를 가로로 꽉 채워, 세로로 이으면 글자를 관통한다.
# 연결 관계(MainWindow → DetailPage)는 그대로 두고 경로만 왼쪽으로 비킨다.
assoc("MainWindow", "left", "DetailPage", "left", accent=VIOLET,
      cs="arc3,rad=0.10")
assoc("ThumbRunner", "left", "ThumbSignals", "right", accent=FAINT,
      dashed=True)
aggregation("DetailPage", "right", "ZoomView", "left", accent=VIOLET,
            filled=False)

# ── 범례 (코어 밴드 오른쪽 빈 자리 — 예전 자리인 오른쪽 아래는 상자로 찼다) ──
lx, ly = 17.30, 8.60
rbox(ax, lx, ly, 7.10, 2.55, fc=WHITE, ec=AXIS, lw=1.3, rounding=0.07)
label(ax, lx + 0.25, ly + 0.45, t("관계 기호 읽는 법"), size=13, weight="bold",
      color=INK, ha="left")
diamond(ax, lx + 0.42, ly + 1.10, r=0.13, fc=INK, ec=INK)
line(ax, (lx + 0.55, ly + 1.10), (lx + 1.10, ly + 1.10), color=INK, lw=1.5)
label(ax, lx + 1.25, ly + 1.10, t("포함 — 한 부품이 다른 부품을 품음"), size=11.5,
      color=INK2, ha="left")
hollow_tri(ax, lx + 0.42, ly + 1.70, size=0.14, point="right", ec=INK, fc=WHITE)
line(ax, (lx + 0.56, ly + 1.70), (lx + 1.10, ly + 1.70), color=INK, lw=1.5)
label(ax, lx + 1.25, ly + 1.70, t("상속 — Qt 기본 클래스를 물려받음"), size=11.5,
      color=INK2, ha="left")
arrow(ax, (lx + 0.25, ly + 2.30), (lx + 1.10, ly + 2.30), color=INK, lw=1.6,
      style="-|>", ms=11)
label(ax, lx + 1.25, ly + 2.30, t("참조·사용   ·   점선 = 신호/백그라운드"),
      size=11.5, color=INK2, ha="left")
arrow(ax, (lx + 0.25, ly + 2.30), (lx + 0.80, ly + 2.30), color=FAINT, lw=1.6,
      style="-|>", ms=11, ls="--")

out = Path(__file__).resolve().parent.parent / f"04-class-diagram{SUF}.png"
save(fig, out)
print("saved", out)
