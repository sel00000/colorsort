"""03-dependency-graph.png — 모듈 import 의존성 그래프.

각 .py 의 실제 import/from 문을 화살표로 그린다 (A→B = A가 B를 import).
3계층: 위 colorsortgui/qt · 중간 colorsortgui · 아래 colorsort.
핵심: 코어(colorsort)는 GUI를 절대 import하지 않는다 — 의존은 경계를 넘어 아래로만.

한/영 두 장을 만든다:  python3 03-dependency-graph.py ko | python3 03-dependency-graph.py en
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams
import matplotlib.patheffects as _pe
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── 폰트 ────────────────────────────────────────────────────────────────────
for _f in ("/home/pc/.local/share/fonts/win-kr/malgun.ttf",
           "/home/pc/.local/share/fonts/win-kr/malgunbd.ttf",
           "/home/pc/.local/share/fonts/win-kr/consola.ttf",
           "/home/pc/.local/share/fonts/win-kr/consolab.ttf"):
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

# ── 영어 번역표 (모듈명·폴더명은 식별자라 번역하지 않는다) ───────────────────
EN = {
    "모듈 import 의존성 그래프": "Module Import Dependency Graph",
    "화살표 = 그 모듈을 import 한다 · 굵은 보라 = 코어로 향하는 의존":
        "Arrow = imports that module · bold violet = dependency toward the core",
    "▲ colorsortgui 세계 (화면 + 로직)": "▲ colorsortgui world (screens + logic)",
    "▼ colorsort 코어 — 위에서 아래로만 의존한다":
        "▼ colorsort core — dependencies only point downward",
    "코어(colorsort)로 향하는 import": "import toward the core (colorsort)",
    "qt → colorsortgui import": "qt → colorsortgui import",
    "app → qt (위로 · 유일한 예외)": "app → qt (upward · the only exception)",
    "같은 계층 내부 import": "import inside the same layer",
    "단방향": "one-way",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


def heavy(color):
    """bold 글자를 한 단계 더 굵게 보이게 하는 같은 색 외곽선."""
    return [_pe.withStroke(linewidth=STROKE, foreground=color)]


INK, INK2, MUT = "#0b0b0b", "#52514e", "#898781"
VIOLET, ORANGE, ROSE = "#4a3aa7", "#d1591f", "#b83d70"
GREYLINE = "#a9a8a1"


def tint(hexc, tt):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(((c * tt + 255 * (1 - tt)) / 255.0) for c in (r, g, b))


# ── 노드 배치 순서 (교차 최소화: 각 계층 허브를 중앙에 정렬) ──────────────────
CORE = ["__main__", "__init__", "language", "messages", "report", "cli",
        "config", "models", "measure", "rules", "sorting", "loading"]
GUI = ["__init__", "__main__", "app", "settings", "i18n", "project",
       "decisions", "fingerprint", "foldering", "enhance", "thumbcache"]
QT = ["__init__", "theme", "widgets", "mainwindow", "detail", "langdialog",
      "imageview"]

# ── 실제 import 엣지 (키 = 'band:module') ────────────────────────────────────
E_INTRA, E_CORE, E_QTGUI, E_UP = [], [], [], []


def add(lst, src, dsts):
    for d in dsts:
        lst.append((src, d))


# colorsort 내부
add(E_INTRA, "core:__main__", ["core:cli"])
add(E_INTRA, "core:cli", ["core:config", "core:language", "core:loading",
                          "core:measure", "core:messages", "core:models",
                          "core:report", "core:rules", "core:sorting"])
add(E_INTRA, "core:language", ["core:messages"])
add(E_INTRA, "core:loading", ["core:models"])
add(E_INTRA, "core:measure", ["core:config", "core:models"])
add(E_INTRA, "core:messages", ["core:models"])
add(E_INTRA, "core:report", ["core:__init__", "core:config", "core:messages", "core:models"])
add(E_INTRA, "core:rules", ["core:config", "core:models"])
add(E_INTRA, "core:sorting", ["core:config", "core:models"])
# colorsortgui 내부
add(E_INTRA, "gui:__main__", ["gui:app"])
add(E_INTRA, "gui:app", ["gui:project", "gui:i18n", "gui:settings"])
add(E_INTRA, "gui:project", ["gui:decisions", "gui:fingerprint", "gui:foldering"])
add(E_INTRA, "gui:thumbcache", ["gui:enhance"])
# qt 내부
add(E_INTRA, "qt:mainwindow", ["qt:detail", "qt:langdialog", "qt:theme", "qt:widgets"])
add(E_INTRA, "qt:detail", ["qt:imageview", "qt:widgets"])
add(E_INTRA, "qt:widgets", ["qt:theme"])
# ── 경계를 넘는 의존 (아래로) ──
add(E_CORE, "gui:project", ["core:cli", "core:config", "core:models",
                            "core:report", "core:sorting"])
add(E_CORE, "gui:thumbcache", ["core:loading"])
add(E_CORE, "qt:mainwindow", ["core:messages", "core:loading"])
add(E_CORE, "qt:detail", ["core:config"])
# qt → gui (아래로, 경계 안쪽) — __init__ 은 __version__ 을 가져오는 실제 import
add(E_QTGUI, "qt:mainwindow", ["gui:i18n", "gui:settings", "gui:thumbcache",
                               "gui:project", "gui:__init__"])
add(E_QTGUI, "qt:detail", ["gui:enhance", "gui:i18n"])
# gui → qt (위로: app 은 실행 시작점이라 화면을 불러온다 — 유일한 예외)
add(E_UP, "gui:app", ["qt:mainwindow", "qt:langdialog", "qt:theme"])

# ── 좌표 ────────────────────────────────────────────────────────────────────
W, H = 28.0, 15.5
NW, NH = 2.05, 0.75
Y_QT, Y_GUI, Y_CORE = H - 4.3, H - 8.0, H - 12.3
Y_BOUND = (Y_GUI + Y_CORE) / 2 + 0.20
MARGIN = 1.28

pos = {}


def place(order, band, y):
    n = len(order)
    usable = W - 2 * MARGIN
    for i, name in enumerate(order):
        x = MARGIN + (usable * i / (n - 1) if n > 1 else usable / 2)
        pos[f"{band}:{name}"] = (x, y)


place(CORE, "core", Y_CORE)
place(GUI, "gui", Y_GUI)
place(QT, "qt", Y_QT)

fig = plt.figure(figsize=(W * S, H * S))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")


def T(x, y, s, size, color=INK, fam=KR, weight="normal", ha="left",
      va="baseline", z=None, **extra):
    """글자: 무조건 +FB pt·bold. 원래 bold였던 글자는 같은 색 외곽선으로 더 굵게."""
    kw = dict(extra)
    if weight == "bold":
        kw["path_effects"] = heavy(color)
    if z is not None:
        kw["zorder"] = z
    return ax.text(x, y, s, fontsize=size + FB, color=color, family=fam,
                   fontweight="bold", ha=ha, va=va, **kw)


def border_pt(c, tx, ty):
    cx, cy = c
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (NW / 2) / abs(dx) if dx else 1e9
    sy = (NH / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def draw_edge(src, dst, color, lw, rad, alpha=1.0, ms=13, z=2, dashed=False):
    a, b = pos[src], pos[dst]
    p0 = border_pt(a, *b)
    p1 = border_pt(b, *a)
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=ms * S, lw=lw * S, color=color,
        alpha=alpha, connectionstyle=f"arc3,rad={rad}", zorder=z,
        linestyle="--" if dashed else "-", shrinkA=1, shrinkB=1,
        joinstyle="round", capstyle="round"))


# 같은 계층 내부 엣지: 바깥쪽으로 부풀려 겹침을 줄인다
def intra_rad(src, dst):
    ax0 = pos[src][0]
    bx0 = pos[dst][0]
    band = src.split(":")[0]
    mag = 0.10 + 0.02 * abs(CORE_index(src) - CORE_index(dst)) if band == "core" else 0.16
    d = -1 if bx0 > ax0 else 1        # 왼→오는 음수 rad = 아래로 부풀림
    if band == "qt":
        d = -d                        # qt 내부는 위로 부풀림(빈 여백 쪽)
    return d * mag


def CORE_index(key):
    m = key.split(":")[1]
    order = {"core": CORE, "gui": GUI, "qt": QT}[key.split(":")[0]]
    return order.index(m)


# ── 그리기 순서: 배경 엣지 먼저, 노드 나중 ──────────────────────────────────
# 경계선 + 라벨
ax.plot([0.4, W - 0.4], [Y_BOUND, Y_BOUND], color=INK2, lw=1.6 * S,
        ls=(0, (7, 5)), zorder=1)
T(2.15, Y_BOUND + 0.30, t("▲ colorsortgui 세계 (화면 + 로직)"), 12.5, INK2,
  ha="left", va="bottom")
T(2.15, Y_BOUND - 0.30, t("▼ colorsort 코어 — 위에서 아래로만 의존한다"), 12.5,
  VIOLET, ha="left", va="top", weight="bold")

# intra (thin gray)
for s, d in E_INTRA:
    draw_edge(s, d, GREYLINE, 1.1, intra_rad(s, d), alpha=0.85, ms=9, z=2)
# qt→gui (orange, medium)
for s, d in E_QTGUI:
    draw_edge(s, d, tint(ORANGE, 0.85), 1.7, 0.05, alpha=0.9, ms=12, z=3)
# gui→qt 위로 (dashed rose — 예외)
for s, d in E_UP:
    draw_edge(s, d, ROSE, 1.7, 0.16, alpha=0.95, ms=12, z=3, dashed=True)
# 경계 넘어 코어로 (violet, bold) — 핵심
for s, d in E_CORE:
    draw_edge(s, d, VIOLET, 2.5, 0.05, alpha=0.97, ms=16, z=4)


# ── 노드 ────────────────────────────────────────────────────────────────────
def node(key, accent):
    x, y = pos[key]
    name = key.split(":")[1]
    ax.add_patch(FancyBboxPatch(
        (x - NW / 2, y - NH / 2), NW, NH,
        boxstyle="round,pad=0,rounding_size=0.10",
        facecolor=tint(accent, 0.12), edgecolor=accent, linewidth=1.8 * S, zorder=6))
    T(x, y, name, 11.5, INK, MONO, ha="center", va="center", z=7)


for n in CORE:
    node(f"core:{n}", VIOLET)
for n in GUI:
    node(f"gui:{n}", ORANGE)
for n in QT:
    node(f"qt:{n}", ROSE)

# ── 계층 라벨 (왼쪽) ────────────────────────────────────────────────────────
for y, lab, col in [(Y_QT, "colorsortgui/qt/", ROSE),
                    (Y_GUI, "colorsortgui/", ORANGE),
                    (Y_CORE, "colorsort/", VIOLET)]:
    T(0.45, y + NH / 2 + 0.34, lab, 14.5, col, MONO, weight="bold",
      ha="left", va="bottom")

# ── 제목 ────────────────────────────────────────────────────────────────────
T(0.5, H - 0.95, t("모듈 import 의존성 그래프"), 25, INK, KR, weight="bold")
T(0.5, H - 1.70, t("화살표 = 그 모듈을 import 한다 · 굵은 보라 = 코어로 향하는 의존"),
  14, INK2, KR)

# ── 범례 (우상단) ───────────────────────────────────────────────────────────
lx, ly = 20.0, H - 0.80
leg = [(VIOLET, "-", 2.5, "코어(colorsort)로 향하는 import"),
       (tint(ORANGE, 0.85), "-", 1.7, "qt → colorsortgui import"),
       (ROSE, "--", 1.7, "app → qt (위로 · 유일한 예외)"),
       (GREYLINE, "-", 1.2, "같은 계층 내부 import")]
for i, (c, ls, lw, lab) in enumerate(leg):
    yy = ly - i * 0.58
    ax.plot([lx, lx + 1.0], [yy, yy], color=c, lw=lw * S, ls=ls,
            solid_capstyle="round")
    T(lx + 1.25, yy, t(lab), 12, INK2, KR, va="center")

# ── 단방향 강조 배지 (경계 왼쪽) ────────────────────────────────────────────
T(0.45, Y_BOUND, t("단방향"), 13, VIOLET, KR, weight="bold", ha="left",
  va="center",
  bbox=dict(boxstyle="round,pad=0.35", facecolor=tint(VIOLET, 0.14),
            edgecolor=VIOLET, linewidth=1.6 * S))

OUT = Path(__file__).resolve().parent.parent / f"03-dependency-graph{SUF}.png"
fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)
