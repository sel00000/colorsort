"""01-architecture.png — 전체 아키텍처.

입력(사진 폴더) → 두 진입점(CLI / GUI) → 공통 코어 파이프라인 → 산출물(results/).
핵심 메시지: GUI(colorsortgui)는 코어(colorsort)를 수정 없이 그대로 재사용한다.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams
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

# ── 색 ──────────────────────────────────────────────────────────────────────
INK, INK2, MUT = "#0b0b0b", "#52514e", "#898781"
VIOLET, ORANGE = "#4a3aa7", "#d1591f"
BLUE, GREEN, AMBER = "#2a78d6", "#1f8a3b", "#e0932a"
GREY = "#6b6a66"


def tint(hexc, t):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(((c * t + 255 * (1 - t)) / 255.0) for c in (r, g, b))


def rbox(ax, x, y, w, h, fill, edge, lw=2.4, rad=0.12):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rad}",
        facecolor=fill, edgecolor=edge, linewidth=lw, mutation_aspect=1.0))


def arrow(ax, p0, p1, color, lw=2.6, ms=24, rad=0.0):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color,
        shrinkA=2, shrinkB=2, connectionstyle=f"arc3,rad={rad}",
        joinstyle="round", capstyle="round"))


def T(ax, x, y, s, size, color=INK, fam=KR, weight="normal", ha="left", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, family=fam,
            fontweight=weight, ha=ha, va=va)


W, H = 15.0, 13.8
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

# 제목
T(ax, 0.5, H - 0.55, "전체 아키텍처", 25, INK, KR, "bold")
T(ax, 0.5, H - 1.08, "사진이 어떻게 파랑/초록/검토 폴더로 나뉘는가 — 두 갈래로 실행, 코어는 하나",
  14, INK2)

# 범례 (우상단)
lx, ly = 10.4, H - 0.55
for i, (c, lab) in enumerate([(VIOLET, "colorsort 코어 (v1)"),
                              (ORANGE, "colorsortgui (v2)"),
                              (BLUE, "파랑/초록/검토 폴더")]):
    yy = ly - i * 0.42
    rbox(ax, lx, yy - 0.13, 0.30, 0.26, fill=tint(c, 0.9), edge=c, lw=1.6, rad=0.06)
    T(ax, lx + 0.44, yy, lab, 13.5, INK2)

cx = W / 2.0
x_cli, x_gui = 3.55, 11.45

# ── 입력 ────────────────────────────────────────────────────────────────────
in_top, in_h, in_w = H - 1.75, 0.95, 6.4
rbox(ax, cx - in_w / 2, in_top - in_h, in_w, in_h, fill=tint(GREY, 0.10),
     edge=GREY, lw=2.4)
T(ax, cx, in_top - 0.34, "입력 · 사진 폴더", 16, INK, KR, "bold", ha="center")
T(ax, cx, in_top - 0.70, "안에 흩어진 PNG 파일들 (하위 폴더까지 훑음)", 13, INK2, ha="center")

# ── 진입점 ──────────────────────────────────────────────────────────────────
ent_top, ent_h, ent_w = H - 3.75, 1.55, 5.4
# CLI
rbox(ax, x_cli - ent_w / 2, ent_top - ent_h, ent_w, ent_h,
     fill=tint(VIOLET, 0.08), edge=VIOLET)
T(ax, x_cli, ent_top - 0.36, "CLI 진입점", 15.5, VIOLET, KR, "bold", ha="center")
T(ax, x_cli, ent_top - 0.80, "py -3 -m colorsort", 15, INK, MONO, "bold", ha="center")
T(ax, x_cli, ent_top - 1.22, "콘솔에서 실행 · 미리보기와 --apply", 13.5, INK2, ha="center")
# GUI
rbox(ax, x_gui - ent_w / 2, ent_top - ent_h, ent_w, ent_h,
     fill=tint(ORANGE, 0.08), edge=ORANGE)
T(ax, x_gui, ent_top - 0.36, "GUI 진입점", 15.5, ORANGE, KR, "bold", ha="center")
T(ax, x_gui, ent_top - 0.80, "Colorsort.exe", 15, INK, MONO, "bold", ha="center")
T(ax, x_gui, ent_top - 1.22, "창에서 실행 · PyInstaller 배포", 13.5, INK2, ha="center")

# 입력 → 두 진입점
arrow(ax, (cx - 1.5, in_top - in_h), (x_cli + 0.6, ent_top + 0.02), GREY, lw=2.2)
arrow(ax, (cx + 1.5, in_top - in_h), (x_gui - 0.6, ent_top + 0.02), GREY, lw=2.2)

# ── colorsortgui 계층 (GUI 전용) ────────────────────────────────────────────
g_top, g_h, g_w = H - 5.95, 2.05, 5.9
rbox(ax, x_gui - g_w / 2, g_top - g_h, g_w, g_h, fill=tint(ORANGE, 0.06), edge=ORANGE)
T(ax, x_gui, g_top - 0.36, "colorsortgui 계층 (GUI 전용)", 14.5, ORANGE, KR, "bold", ha="center")
gl = x_gui - g_w / 2 + 0.35
T(ax, gl, g_top - 0.82, "project.py", 13, INK, MONO, "bold")
T(ax, gl + 1.85, g_top - 0.82, "유일한 창구 — v1 그대로 + 사람 결정", 13.5, INK2)
T(ax, gl, g_top - 1.24, "DecisionStore", 13, INK, MONO, "bold")
T(ax, gl + 1.85, g_top - 1.24, "사람이 버튼으로 확정 (decisions.json)", 13.5, INK2)
T(ax, gl, g_top - 1.66, "qt/", 13, INK, MONO, "bold")
T(ax, gl + 1.85, g_top - 1.66, "화면 — 창 · 썸네일 · 크게 보기", 13.5, INK2)

# GUI 진입점 → colorsortgui
arrow(ax, (x_gui, ent_top - ent_h), (x_gui, g_top + 0.02), ORANGE)

# ── 공통 코어 ───────────────────────────────────────────────────────────────
c_top, c_h, c_w = H - 8.9, 2.15, 13.8
c_x = cx - c_w / 2
rbox(ax, c_x, c_top - c_h, c_w, c_h, fill=tint(VIOLET, 0.07), edge=VIOLET, lw=3.0)
T(ax, cx, c_top - 0.40, "공통 코어 · colorsort 파이프라인", 16.5, VIOLET, KR, "bold", ha="center")

stages = [("loading", "이미지 읽기"), ("measure", "픽셀 측정"), ("rules", "판정"),
          ("sorting", "복사 계획·실행"), ("report", "결과 기록")]
sw, sh = 2.28, 0.95
gap = (c_w - 0.7 - len(stages) * sw) / (len(stages) - 1)
sx = c_x + 0.35
sy = c_top - c_h + 0.35
stage_centers = []
for i, (nm, gl2) in enumerate(stages):
    x = sx + i * (sw + gap)
    rbox(ax, x, sy, sw, sh, fill="white", edge=VIOLET, lw=1.8, rad=0.10)
    T(ax, x + sw / 2, sy + sh - 0.34, nm, 13.5, VIOLET, MONO, "bold", ha="center")
    T(ax, x + sw / 2, sy + 0.28, gl2, 12, INK2, ha="center")
    stage_centers.append(x + sw / 2)
    if i:
        arrow(ax, (prev_x + sw, sy + sh / 2), (x, sy + sh / 2), MUT, lw=2.0, ms=18)
    prev_x = x

# 수렴 강조: CLI(왼쪽)와 colorsortgui(오른쪽) 둘 다 코어로
arrow(ax, (x_cli, ent_top - ent_h), (x_cli, c_top + 0.02), VIOLET, lw=2.8)
arrow(ax, (x_gui, g_top - g_h), (x_gui, c_top + 0.02), ORANGE, lw=2.8)
# GUI→코어 화살표 옆 주석
T(ax, x_gui + 0.25, (g_top - g_h + c_top) / 2, "v1_run =\ncolorsort.cli.run\n그대로 호출",
  11.5, ORANGE, KR, ha="left")
# 수렴 배지
badge_y = c_top + 0.42
rbox(ax, cx - 3.4, badge_y - 0.28, 6.8, 0.56, fill=tint(VIOLET, 0.16), edge=VIOLET,
     lw=1.8, rad=0.20)
T(ax, cx, badge_y, "CLI도 GUI도 여기로 — 판정 로직은 프로젝트에 단 한 벌",
  13, VIOLET, KR, "bold", ha="center")

# ── 산출물 ──────────────────────────────────────────────────────────────────
o_top, o_h, o_w = H - 11.35, 2.0, 13.8
o_x = cx - o_w / 2
rbox(ax, o_x, o_top - o_h, o_w, o_h, fill=tint(GREY, 0.08), edge=GREY)
T(ax, cx, o_top - 0.38, "산출물 · results/ 폴더", 16, INK, KR, "bold", ha="center")
arrow(ax, (cx, c_top - c_h), (cx, o_top + 0.02), VIOLET, lw=2.8)

# 폴더 칩 (실제 파랑/초록/호박)
fy = o_top - 1.0
folders = [("blue/", BLUE), ("green/", GREEN), ("review/", AMBER)]
fx = o_x + 0.55
for nm, col in folders:
    rbox(ax, fx, fy - 0.34, 1.75, 0.68, fill=col, edge=col, lw=1.5, rad=0.12)
    T(ax, fx + 0.875, fy, nm, 14, "white", MONO, "bold", ha="center")
    fx += 2.05
T(ax, fx + 0.05, fy, "← 사진 사본이 색깔별로", 13.5, INK2)

# 파일 칩
fy2 = o_top - 1.62
files_common = ["results.csv", "run.json", "copy-log.csv"]
fx = o_x + 0.55
for nm in files_common:
    w = 0.20 + len(nm) * 0.135
    rbox(ax, fx, fy2 - 0.26, w, 0.52, fill="white", edge=GREY, lw=1.4, rad=0.10)
    T(ax, fx + w / 2, fy2, nm, 12, INK, MONO, ha="center")
    fx += w + 0.28
T(ax, fx + 0.02, fy2, "(공통)", 12, MUT)
fx += 1.15
for nm in ["decisions.json", "moves-log.csv"]:
    w = 0.20 + len(nm) * 0.135
    rbox(ax, fx, fy2 - 0.26, w, 0.52, fill=tint(ORANGE, 0.10), edge=ORANGE, lw=1.4, rad=0.10)
    T(ax, fx + w / 2, fy2, nm, 12, INK, MONO, ha="center")
    fx += w + 0.28
T(ax, fx + 0.02, fy2, "(GUI 전용)", 12, ORANGE)

OUT = Path(__file__).resolve().parent.parent / "01-architecture.png"
fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)
