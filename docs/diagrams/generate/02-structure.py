"""02-structure.png — 패키지·모듈 구조도.

각 .py 파일이 무슨 일을 하는지(모듈 docstring 첫 줄 요약)를 패키지별 상자로 보여준다.
비전문가용 자료: 설명은 한국어, 파일·클래스·함수명은 영문 그대로.

한/영 두 장을 만든다:  python3 02-structure.py ko  |  python3 02-structure.py en
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams
import matplotlib.patheffects as _pe
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── 폰트: 맑은 고딕(한글) + Consolas(코드 식별자) ──────────────────────────
_FONTS = ("/home/pc/.local/share/fonts/win-kr/malgun.ttf",
          "/home/pc/.local/share/fonts/win-kr/malgunbd.ttf",
          "/home/pc/.local/share/fonts/win-kr/consola.ttf",
          "/home/pc/.local/share/fonts/win-kr/consolab.ttf")
for _f in _FONTS:
    font_manager.fontManager.addfont(_f)
rcParams["font.family"] = "Malgun Gothic"
rcParams["axes.unicode_minus"] = False
KR = "Malgun Gothic"
MONO = font_manager.FontProperties(
    fname="/home/pc/.local/share/fonts/win-kr/consola.ttf").get_name()

# ── 큰 글자 상수 (2026-07 확정 · _common.py와 같은 값 — 이 파일은 자체 완결) ──
S, FB, STROKE = 1.45, 20, 1.1
LANG = "en" if "en" in sys.argv[1:] else "ko"
SUF = "" if LANG == "ko" else "-en"

# ── 영어 번역표 (파일명·폴더명·식별자는 번역하지 않는다) ─────────────────────
EN = {
    "패키지 · 모듈 구조도": "Package & Module Structure",
    "각 파일이 맡은 일 — 모듈 docstring 첫 줄 요약":
        "What each file does — first-line summary of each module docstring",
    # colorsort/
    "패키지 소개 · 버전 상수": "intro · version constant",
    "실행 진입점 (cli.main)": "entry point (cli.main)",
    "명령줄 파싱·호출·출력": "CLI: parse · run · print",
    "판정 임계값 데이터": "verdict thresholds",
    "언어 선택·저장·재사용": "language pick & reuse",
    "이미지 읽기 (유일 통로)": "image load (only path)",
    "픽셀 측정 · 순수 함수": "pixel stats · pure funcs",
    "한/영 문구 카탈로그": "KO/EN message catalog",
    "불변 자료구조": "immutable data types",
    "CSV·기록·이력·요약": "CSV, history, summary",
    "판정 규칙 · 순수 함수": "verdict rules · pure fn",
    "복사 계획 수립·실행": "plan & run the copies",
    # colorsortgui/
    "v2 GUI (v1 그대로 사용)": "v2 GUI (v1 untouched)",
    "실행 진입점 (app.main)": "entry point (app.main)",
    "부팅: 설정→언어→창": "boot: set→lang→win",
    "사람 확정 (지문 열쇠)": "human confirm (hash)",
    "표시 전용 변환 (판정 X)": "display only, no verdict",
    "파일 내용 지문": "file content fingerprint",
    "하위 폴더 결정 (영문)": "subfolder (English)",
    "GUI 문자열표 (기본 EN)": "GUI strings (EN default)",
    "유일한 창구: v1+사람": "gateway: v1 + human",
    "포터블 설정": "portable settings",
    "썸네일 디스크 캐시": "thumbnail disk cache",
    # colorsortgui/qt/
    "화면 패키지": "screen package",
    "크게 보기 + 검사관 카드": "detail view + inspector",
    "확대·이동 이미지 뷰": "zoom / pan image view",
    "첫 실행 언어 대화상자": "first-run lang dialog",
    "메인 창 · 그리드·분류": "main win · grid/sort",
    "VENOM 색 토큰·QSS": "VENOM colors · QSS",
    "ρ 눈금자 · 통계 카드": "ρ ruler · stat cards",
    # 헤더 역할줄
    "CLI 코어 · v1 판정 엔진": "CLI core · v1 verdict engine",
    "GUI 로직 · v2 (사람 확정)": "GUI logic · v2 (human confirm)",
    "PySide6 화면": "PySide6 screens",
    # 노트 상자
    "프로젝트 루트": "project root",
    "자동 검사 11개 + 하위 폴더": "11 auto tests + subfolders",
    "PyInstaller exe 배포 도구": "PyInstaller exe build tools",
    "최상위 파일과 폴더": "top-level files & folders",
    # 콜아웃
    "핵심 원칙": "Core principle",
    "colorsortgui(주황)는 colorsort(보라)를 수정 없이 그대로 재사용한다 — "
    "파랑/초록 판정 로직은 프로젝트 전체에 단 한 벌.":
        "colorsortgui (orange) reuses colorsort (violet) as-is — "
        "the blue/green verdict logic exists once in the whole project.",
    "GUI는 그 위에 '사람이 버튼으로 고친 결정'만 얹는다 (project.py 가 유일한 창구).":
        "The GUI only layers 'decisions a human fixed with a button' on top "
        "(project.py is the only gateway).",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


def heavy(color):
    """bold 글자를 한 단계 더 굵게 보이게 하는 같은 색 외곽선."""
    return [_pe.withStroke(linewidth=STROKE, foreground=color)]


# ── 색: 코어=보라, GUI로직=주황, 화면=자홍. 파랑/초록/호박은 사진 의미색 전용 ──
INK, INK2, MUT = "#0b0b0b", "#52514e", "#898781"
VIOLET, ORANGE, ROSE = "#4a3aa7", "#d1591f", "#b83d70"
TESTS, PACK, ROOTC = "#1baf7a", "#2f6f9f", "#6b6a66"


def tint(hexc, tt):
    """hexc 를 흰색과 섞는다. tt=색의 비율(0→흰색, 1→원색)."""
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(((c * tt + 255 * (1 - tt)) / 255.0) for c in (r, g, b))


def rbox(ax, x, y, w, h, fill, edge, lw=1.4, rad=0.10):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rad}",
        facecolor=fill, edgecolor=edge, linewidth=lw * S, mutation_aspect=1.0))


# ── 데이터: (파일명, 한 줄 설명) — docstring 첫 줄을 요약 ───────────────────
CORE = [
    ("__init__.py",   "패키지 소개 · 버전 상수"),
    ("__main__.py",   "실행 진입점 (cli.main)"),
    ("cli.py",        "명령줄 파싱·호출·출력"),
    ("config.py",     "판정 임계값 데이터"),
    ("language.py",   "언어 선택·저장·재사용"),
    ("loading.py",    "이미지 읽기 (유일 통로)"),
    ("measure.py",    "픽셀 측정 · 순수 함수"),
    ("messages.py",   "한/영 문구 카탈로그"),
    ("models.py",     "불변 자료구조"),
    ("report.py",     "CSV·기록·이력·요약"),
    ("rules.py",      "판정 규칙 · 순수 함수"),
    ("sorting.py",    "복사 계획 수립·실행"),
]
GUI = [
    ("__init__.py",    "v2 GUI (v1 그대로 사용)"),
    ("__main__.py",    "실행 진입점 (app.main)"),
    ("app.py",         "부팅: 설정→언어→창"),
    ("decisions.py",   "사람 확정 (지문 열쇠)"),
    ("enhance.py",     "표시 전용 변환 (판정 X)"),
    ("fingerprint.py", "파일 내용 지문"),
    ("foldering.py",   "하위 폴더 결정 (영문)"),
    ("i18n.py",        "GUI 문자열표 (기본 EN)"),
    ("project.py",     "유일한 창구: v1+사람"),
    ("settings.py",    "포터블 설정"),
    ("thumbcache.py",  "썸네일 디스크 캐시"),
]
QT = [
    ("__init__.py",    "화면 패키지"),
    ("detail.py",      "크게 보기 + 검사관 카드"),
    ("imageview.py",   "확대·이동 이미지 뷰"),
    ("langdialog.py",  "첫 실행 언어 대화상자"),
    ("mainwindow.py",  "메인 창 · 그리드·분류"),
    ("theme.py",       "VENOM 색 토큰·QSS"),
    ("widgets.py",     "ρ 눈금자 · 통계 카드"),
]

# ── 치수 ───────────────────────────────────────────────────────────────────
W = 21.6
LM, GAP = 0.5, 0.55
COLW = (W - 2 * LM - 2 * GAP) / 3.0          # 세 열 폭
ROW_H, HEAD_H = 0.58, 1.20
PAD_TOP, PAD_BOT = 0.14, 0.22
NAME_OFF = 2.80                               # 상자 왼쪽 안쪽에서 설명 시작까지
NOTE_LH = 0.58                                # 노트 상자 줄간

_over = []                                    # 넘침 감시 목록


def box_height(n):
    return HEAD_H + PAD_TOP + n * ROW_H + PAD_BOT


def T(ax, x, y, s, size, color=INK, fam=KR, weight="normal", ha="left",
      va="center", limit=None):
    """글자: 무조건 +FB pt·bold. 원래 bold였던 글자는 같은 색 외곽선으로 더 굵게.

    limit 을 주면 렌더 후 실제 폭을 재서 넘치면 _over 에 기록한다(눈 검사 보조).
    """
    kw = {}
    if weight == "bold":
        kw["path_effects"] = heavy(color)
    tx = ax.text(x, y, s, fontsize=size + FB, color=color, family=fam,
                 fontweight="bold", ha=ha, va=va, **kw)
    if limit is not None:
        _watch.append((tx, limit, s))
    return tx


_watch = []


def draw_group(ax, x, top, folder, role, rows, accent):
    n = len(rows)
    h = box_height(n)
    bottom = top - h
    rbox(ax, x, bottom, COLW, h, fill="white", edge=accent, lw=2.4, rad=0.16)
    # 헤더
    hy = top - HEAD_H
    rbox(ax, x, hy, COLW, HEAD_H, fill=tint(accent, 0.14), edge="none", rad=0.16)
    ax.add_patch(plt_rect(x, hy, COLW, 0.03, accent))     # 헤더 밑줄
    T(ax, x + 0.22, top - 0.42, folder, 17, accent, MONO, "bold")
    T(ax, x + COLW - 0.20, top - 0.42,
      f"{n}개" if LANG == "ko" else f"{n} files", 12.5, MUT, KR, ha="right")
    T(ax, x + 0.23, top - 0.90, t(role), 12.5, INK2, KR, limit=COLW - 0.40)
    # 행
    ry = hy - PAD_TOP - ROW_H / 2
    for i, (name, desc) in enumerate(rows):
        if i % 2 == 1:
            rbox(ax, x + 0.08, ry - ROW_H / 2, COLW - 0.16, ROW_H,
                 fill=tint(accent, 0.05), edge="none", lw=0, rad=0.06)
        T(ax, x + 0.24, ry, name, 12.5, INK, MONO, limit=NAME_OFF - 0.30)
        T(ax, x + NAME_OFF, ry, t(desc), 12.5, INK2, KR,
          limit=COLW - NAME_OFF - 0.12)
        ry -= ROW_H
    return bottom


def plt_rect(x, y, w, h, color):
    from matplotlib.patches import Rectangle
    return Rectangle((x, y), w, h, facecolor=color, edgecolor="none")


def draw_note(ax, x, top, folder, lines, accent, width=None, title_fam=MONO):
    ww = width or COLW
    n = len(lines)
    h = HEAD_H + PAD_TOP + n * NOTE_LH + PAD_BOT
    bottom = top - h
    rbox(ax, x, bottom, ww, h, fill="white", edge=accent, lw=2.4, rad=0.16)
    hy = top - HEAD_H
    rbox(ax, x, hy, ww, HEAD_H, fill=tint(accent, 0.14), edge="none", rad=0.16)
    ax.add_patch(plt_rect(x, hy, ww, 0.03, accent))
    T(ax, x + 0.22, top - 0.42, t(folder) if title_fam is KR else folder,
      17, accent, title_fam, "bold", limit=ww - 0.40)
    T(ax, x + 0.23, top - 0.90, t(lines[0][0]), 12.5, INK2, KR, limit=ww - 0.40)
    ly = hy - PAD_TOP - 0.40
    for s, fam in lines[1:]:
        T(ax, x + 0.24, ly, s, 12.5, INK, fam, limit=ww - 0.42)
        ly -= NOTE_LH
    return bottom


# ── 레이아웃 계산 ───────────────────────────────────────────────────────────
TITLE_H = 2.0
h_core = box_height(len(CORE))
h_gui = box_height(len(GUI))
h_qt = box_height(len(QT))
band1_h = max(h_core, h_gui)                  # 세 패키지 상자 중 가장 큰 높이
# 2번째 줄: tests / packaging / root (노트형)
notes_h = HEAD_H + PAD_TOP + 3 * NOTE_LH + PAD_BOT
band2_h = notes_h
callout_h = HEAD_H + PAD_TOP + 2 * NOTE_LH + PAD_BOT
GAP_V = 0.55
H = TITLE_H + band1_h + GAP_V + band2_h + GAP_V + callout_h + 0.50

fig = plt.figure(figsize=(W * S, H * S))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

# 제목
T(ax, LM, H - 0.80, t("패키지 · 모듈 구조도"), 25, INK, KR, "bold")
T(ax, LM, H - 1.50, t("각 파일이 맡은 일 — 모듈 docstring 첫 줄 요약"), 14, INK2, KR,
  limit=W - 2 * LM)

# 1번째 줄: 세 패키지
b1_top = H - TITLE_H
x0 = LM
x1 = LM + COLW + GAP
x2 = LM + 2 * (COLW + GAP)
draw_group(ax, x0, b1_top, "colorsort/", "CLI 코어 · v1 판정 엔진", CORE, VIOLET)
draw_group(ax, x1, b1_top, "colorsortgui/", "GUI 로직 · v2 (사람 확정)", GUI, ORANGE)
draw_group(ax, x2, b1_top, "colorsortgui/qt/", "PySide6 화면", QT, ROSE)

# 2번째 줄: tests / packaging / 루트
b2_top = b1_top - band1_h - GAP_V
draw_note(ax, x0, b2_top, "tests/",
          [("자동 검사 11개 + 하위 폴더", KR),
           ("test_rules · test_measure", MONO),
           ("test_cli · test_scan_markers", MONO),
           ("test_e2e · gui_core/ · gui_qt/", MONO)], TESTS)
draw_note(ax, x1, b2_top, "packaging/",
          [("PyInstaller exe 배포 도구", KR),
           ("colorsort.spec · colorsort.ico", MONO),
           ("demo_capture.py · make_icon.py", MONO),
           ("README_FIRST · USER_GUIDE", MONO)], PACK)
draw_note(ax, x2, b2_top, "프로젝트 루트",
          [("최상위 파일과 폴더", KR),
           ("README.md · .gitignore", MONO),
           ("build/ · dist/ · docs/", MONO),
           ("colorsort/ · colorsortgui/", MONO)], ROOTC, title_fam=KR)

# 3번째 줄: 핵심 원칙 콜아웃 (전체 폭)
b3_top = b2_top - band2_h - GAP_V
cw = W - 2 * LM
rbox(ax, LM, b3_top - callout_h, cw, callout_h,
     fill=tint(ORANGE, 0.08), edge=ORANGE, lw=2.4, rad=0.16)
T(ax, LM + 0.35, b3_top - 0.62, t("핵심 원칙"), 16, ORANGE, KR, "bold")
T(ax, LM + 0.35, b3_top - 1.38,
  t("colorsortgui(주황)는 colorsort(보라)를 수정 없이 그대로 재사용한다 — "
    "파랑/초록 판정 로직은 프로젝트 전체에 단 한 벌."),
  13.5, INK, KR, limit=cw - 0.70)
T(ax, LM + 0.35, b3_top - 1.98,
  t("GUI는 그 위에 '사람이 버튼으로 고친 결정'만 얹는다 (project.py 가 유일한 창구)."),
  13.5, INK2, KR, limit=cw - 0.70)

# ── 넘침 감시: 실제 렌더 폭을 재서 배정 폭을 넘는 글자를 보고한다 ────────────
fig.canvas.draw()
_r = fig.canvas.get_renderer()
_inv = ax.transData.inverted()
for tx, lim, s in _watch:
    bb = tx.get_window_extent(renderer=_r)
    wdata = _inv.transform((bb.x1, bb.y1))[0] - _inv.transform((bb.x0, bb.y0))[0]
    if wdata > lim:
        _over.append((round(wdata, 3), lim, s))
if _over:
    print(f"[넘침 {len(_over)}건]")
    for wdata, lim, s in sorted(_over, reverse=True):
        print(f"  {wdata} > {lim:.2f}   {s!r}")

OUT = Path(__file__).resolve().parent.parent / f"02-structure{SUF}.png"
fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT, f"W={W} H={round(H, 2)}")
