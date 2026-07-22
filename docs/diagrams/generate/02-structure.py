"""02-structure.png — 패키지·모듈 구조도.

각 .py 파일이 무슨 일을 하는지(모듈 docstring 첫 줄 요약)를 패키지별 상자로 보여준다.
비전문가용 자료: 설명은 한국어, 파일·클래스·함수명은 영문 그대로.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams
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

# ── 색: 코어=보라, GUI로직=주황, 화면=자홍. 파랑/초록/호박은 사진 의미색 전용 ──
INK, INK2, MUT = "#0b0b0b", "#52514e", "#898781"
VIOLET, ORANGE, ROSE = "#4a3aa7", "#d1591f", "#b83d70"
TESTS, PACK, ROOTC = "#1baf7a", "#2f6f9f", "#6b6a66"


def tint(hexc, t):
    """hexc 를 흰색과 섞는다. t=색의 비율(0→흰색, 1→원색)."""
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(((c * t + 255 * (1 - t)) / 255.0) for c in (r, g, b))


def rbox(ax, x, y, w, h, fill, edge, lw=1.4, rad=0.10):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rad}",
        facecolor=fill, edgecolor=edge, linewidth=lw, mutation_aspect=1.0))


# ── 데이터: (파일명, 한 줄 설명) — docstring 첫 줄을 요약 ───────────────────
CORE = [
    ("__init__.py",   "패키지 소개 · 버전 상수"),
    ("__main__.py",   "실행 진입점 (cli.main)"),
    ("cli.py",        "명령줄 IF · 파싱·호출·출력"),
    ("config.py",     "판정 임계값 (데이터로 둠)"),
    ("language.py",   "언어 선택·저장·재사용"),
    ("loading.py",    "이미지 읽기 (유일 통로)"),
    ("measure.py",    "픽셀 측정 · 순수 함수"),
    ("messages.py",   "한/영 문구 카탈로그"),
    ("models.py",     "불변 자료구조"),
    ("report.py",     "CSV·기록·이력·요약 출력"),
    ("rules.py",      "판정 규칙 · 순수 함수"),
    ("sorting.py",    "복사 계획 수립·실행"),
]
GUI = [
    ("__init__.py",    "v2 GUI (v1 그대로 사용)"),
    ("__main__.py",    "실행 진입점 (app.main)"),
    ("app.py",         "부팅: 설정→언어→창"),
    ("decisions.py",   "사람 확정 결정 (지문 열쇠)"),
    ("enhance.py",     "표시 전용 변환 (판정 X)"),
    ("fingerprint.py", "파일 내용 지문"),
    ("foldering.py",   "하위 폴더 결정 (영문 고정)"),
    ("i18n.py",        "GUI 문자열표 (기본 EN)"),
    ("project.py",     "유일한 창구: v1+사람결정"),
    ("settings.py",    "포터블 설정"),
    ("thumbcache.py",  "썸네일 디스크 캐시"),
]
QT = [
    ("__init__.py",    "화면 패키지"),
    ("detail.py",      "크게 보기 + 검사관 카드"),
    ("imageview.py",   "확대·이동 이미지 뷰"),
    ("langdialog.py",  "첫 실행 언어 대화상자"),
    ("mainwindow.py",  "메인 창: 그리드·분류 워커"),
    ("theme.py",       "VENOM 색 토큰·QSS"),
    ("widgets.py",     "ρ 눈금자 · 통계 카드"),
]

# ── 치수 ───────────────────────────────────────────────────────────────────
W = 16.6
LM, GAP = 0.5, 0.55
COLW = (W - 2 * LM - 2 * GAP) / 3.0          # 세 열 폭
ROW_H, HEAD_H = 0.47, 0.86
PAD_TOP, PAD_BOT = 0.10, 0.16
NAME_OFF = 1.72                               # 상자 왼쪽 안쪽에서 설명 시작까지


def box_height(n):
    return HEAD_H + PAD_TOP + n * ROW_H + PAD_BOT


def draw_group(ax, x, top, folder, role, rows, accent):
    n = len(rows)
    h = box_height(n)
    bottom = top - h
    rbox(ax, x, bottom, COLW, h, fill="white", edge=accent, lw=2.4, rad=0.14)
    # 헤더
    hy = top - HEAD_H
    rbox(ax, x, hy, COLW, HEAD_H, fill=tint(accent, 0.14), edge="none", rad=0.14)
    ax.add_patch(plt_rect(x, hy, COLW, 0.03, accent))     # 헤더 밑줄
    ax.text(x + 0.22, top - 0.30, folder, fontsize=17, color=accent,
            family=MONO, fontweight="bold", va="center", ha="left")
    ax.text(x + COLW - 0.20, top - 0.30, f"{n}개", fontsize=12.5, color=MUT,
            family=KR, va="center", ha="right")
    ax.text(x + 0.23, top - 0.66, role, fontsize=12.5, color=INK2,
            family=KR, va="center", ha="left")
    # 행
    ry = hy - PAD_TOP - ROW_H / 2
    for i, (name, desc) in enumerate(rows):
        if i % 2 == 1:
            rbox(ax, x + 0.08, ry - ROW_H / 2, COLW - 0.16, ROW_H,
                 fill=tint(accent, 0.05), edge="none", lw=0, rad=0.05)
        ax.text(x + 0.24, ry, name, fontsize=12.5, color=INK,
                family=MONO, va="center", ha="left")
        ax.text(x + NAME_OFF, ry, desc, fontsize=12.5, color=INK2,
                family=KR, va="center", ha="left")
        ry -= ROW_H
    return bottom


def plt_rect(x, y, w, h, color):
    from matplotlib.patches import Rectangle
    return Rectangle((x, y), w, h, facecolor=color, edgecolor="none")


def draw_note(ax, x, top, folder, lines, accent, width=None, title_fam=MONO):
    ww = width or COLW
    n = len(lines)
    h = HEAD_H + PAD_TOP + n * 0.44 + PAD_BOT
    bottom = top - h
    rbox(ax, x, bottom, ww, h, fill="white", edge=accent, lw=2.4, rad=0.14)
    hy = top - HEAD_H
    rbox(ax, x, hy, ww, HEAD_H, fill=tint(accent, 0.14), edge="none", rad=0.14)
    ax.add_patch(plt_rect(x, hy, ww, 0.03, accent))
    ax.text(x + 0.22, top - 0.30, folder, fontsize=17, color=accent,
            family=title_fam, fontweight="bold", va="center", ha="left")
    ax.text(x + 0.23, top - 0.66, lines[0][0], fontsize=12.5, color=INK2,
            family=KR, va="center", ha="left")
    ly = hy - PAD_TOP - 0.30
    for s, fam in lines[1:]:
        ax.text(x + 0.24, ly, s, fontsize=12.5, color=INK,
                family=fam, va="center", ha="left")
        ly -= 0.44
    return bottom


# ── 레이아웃 계산 ───────────────────────────────────────────────────────────
TITLE_H = 1.35
band1_top = None  # set after H known
h_core = box_height(len(CORE))
h_gui = box_height(len(GUI))
h_qt = box_height(len(QT))
band1_h = max(h_core, h_gui)                  # 세 패키지 상자 중 가장 큰 높이
# 2번째 줄: tests / packaging / root (노트형)
notes_h = HEAD_H + PAD_TOP + 3 * 0.44 + PAD_BOT
band2_h = notes_h
callout_h = HEAD_H + PAD_TOP + 2 * 0.44 + PAD_BOT
GAP_V = 0.5
H = TITLE_H + band1_h + GAP_V + band2_h + GAP_V + callout_h + 0.45

fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

# 제목
ax.text(LM, H - 0.55, "패키지 · 모듈 구조도", fontsize=25, color=INK,
        family=KR, fontweight="bold", va="center", ha="left")
ax.text(LM, H - 1.05, "각 파일이 맡은 일 — 모듈 docstring 첫 줄 요약",
        fontsize=14, color=INK2, family=KR, va="center", ha="left")

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
           ("test_rules · test_measure · test_cli", MONO),
           ("test_e2e · test_scan_markers …", MONO),
           ("gui_core/ · gui_qt/", MONO)], TESTS)
draw_note(ax, x1, b2_top, "packaging/",
          [("PyInstaller exe 배포 도구", KR),
           ("colorsort.spec · colorsort.ico", MONO),
           ("demo_capture.py · make_icon.py", MONO),
           ("README_FIRST · USER_GUIDE", MONO)], PACK)
draw_note(ax, x2, b2_top, "프로젝트 루트",
          [("최상위 파일과 폴더", KR),
           ("README.md · CLAUDE.md", MONO),
           ("build/ · dist/ · docs/", MONO),
           ("colorsort/ · colorsortgui/", MONO)], ROOTC, title_fam=KR)

# 3번째 줄: 핵심 원칙 콜아웃 (전체 폭)
b3_top = b2_top - band2_h - GAP_V
cw = W - 2 * LM
rbox(ax, LM, b3_top - callout_h, cw, callout_h,
     fill=tint(ORANGE, 0.08), edge=ORANGE, lw=2.4, rad=0.14)
ax.text(LM + 0.3, b3_top - 0.5, "핵심 원칙", fontsize=16, color=ORANGE,
        family=KR, fontweight="bold", va="center", ha="left")
ax.text(LM + 0.3, b3_top - 1.02,
        "colorsortgui(주황)는 colorsort(보라)를 수정 없이 그대로 재사용한다 — "
        "파랑/초록 판정 로직은 프로젝트 전체에 단 한 벌.",
        fontsize=13.5, color=INK, family=KR, va="center", ha="left")
ax.text(LM + 0.3, b3_top - 1.5,
        "GUI는 그 위에 '사람이 버튼으로 고친 결정'만 얹는다 (project.py 가 유일한 창구).",
        fontsize=13.5, color=INK2, family=KR, va="center", ha="left")

OUT = Path(__file__).resolve().parent.parent / "02-structure.png"
fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)
