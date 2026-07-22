"""08-call-graph.png — 함수 콜 그래프.

두 진입점(CLI=보라, GUI=주황)에서 시작하는 주요 함수 호출.
공유 코어 함수는 한 번만 그려 양쪽 화살표가 모이게 한다.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

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

INK, INK2, MUT = "#0b0b0b", "#52514e", "#898781"
VIOLET, ORANGE, GREY = "#4a3aa7", "#d1591f", "#7d7c77"
COREC = "#3f6b52"          # 공유 코어 = 짙은 초록빛 회색 (중립·의미색과 구분)


def tint(hexc, t):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(((c * t + 255 * (1 - t)) / 255.0) for c in (r, g, b))


W, H = 20.0, 15.8
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

# ── 노드 등록부 ─────────────────────────────────────────────────────────────
N = {}   # name -> (cx, cy, w, h)
COL = {"cli": VIOLET, "gui": ORANGE, "core": COREC}


def node(name, x, y, kind, w=2.2, h=0.62, fs=11.5, bold=False, label=None):
    fs = max(fs, 11.5)          # 최소 글자 크기 보장 (사용자가 큰 글자 선호)
    N[name] = (x, y, w, h)
    c = COL[kind]
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.10",
        facecolor=tint(c, 0.13), edgecolor=c, linewidth=2.0 if bold else 1.6, zorder=6))
    ax.text(x, y, label or name, fontsize=fs, color=INK, family=MONO,
            fontweight="bold" if bold else "normal", ha="center", va="center", zorder=7)


def border_pt(name, tx, ty):
    cx, cy, w, h = N[name]
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2) / abs(dx) if dx else 1e9
    sy = (h / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def edge(a, b, color, lw=2.0, rad=0.0, ms=15, z=4, dashed=False, alpha=1.0):
    ax_, ay_, _, _ = N[a]
    bx_, by_, _, _ = N[b]
    p0 = border_pt(a, bx_, by_)
    p1 = border_pt(b, ax_, ay_)
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, alpha=alpha,
        connectionstyle=f"arc3,rad={rad}", zorder=z, linestyle="--" if dashed else "-",
        shrinkA=1, shrinkB=1, joinstyle="round", capstyle="round"))


def cluster(x0, y0, x1, y1, color, label, lx=None, ly=None):
    ax.add_patch(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.16",
        facecolor=tint(color, 0.05), edgecolor=tint(color, 0.5), linewidth=1.4,
        linestyle=(0, (6, 4)), zorder=0))
    ax.text(lx if lx is not None else x0 + 0.25, ly if ly is not None else y1 - 0.3,
            label, fontsize=13, color=color, family=KR, fontweight="bold",
            ha="left", va="center", zorder=1)


# ── 클러스터 배경 ───────────────────────────────────────────────────────────
cluster(0.4, 6.0, 6.2, 14.2, VIOLET, "명령줄 (CLI)")
cluster(6.5, 11.1, 19.6, 14.2, ORANGE, "① 부팅")
cluster(6.5, 5.7, 12.9, 10.8, ORANGE, "② 분류 (Sort)")
cluster(13.1, 7.3, 15.6, 10.8, ORANGE, "③ 썸네일")
cluster(15.8, 4.0, 19.6, 10.8, ORANGE, "④ 크게 보기 · 수정 · 되돌리기")
cluster(0.4, 0.75, 15.5, 5.4, COREC, "공유 코어 — 두 진입점이 여기서 만난다 (함수 한 벌)")

# ── 코어 내부 상자: run + 실행기 ─────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((0.8, 1.1), 7.4, 3.5,
             boxstyle="round,pad=0,rounding_size=0.12", facecolor="white",
             edgecolor=COREC, linewidth=1.8, zorder=2))
ax.text(4.5, 4.32, "run  (v1_run) — 판정 파이프라인", fontsize=12.5, color=COREC,
        family=KR, fontweight="bold", ha="center", zorder=3)
ax.add_patch(FancyBboxPatch((8.5, 1.1), 6.6, 3.5,
             boxstyle="round,pad=0,rounding_size=0.12", facecolor="white",
             edgecolor=COREC, linewidth=1.8, zorder=2))
ax.text(11.8, 4.32, "복사 · 기록 실행기", fontsize=12.5, color=COREC,
        family=KR, fontweight="bold", ha="center", zorder=3)
# 수렴 화살표가 상자(함수 묶음)를 겨냥하도록 얇은 앵커를 둔다
N["run@top"] = (4.5, 4.56, 5.0, 0.08)
N["exec@top"] = (11.8, 4.56, 4.5, 0.08)

# run 내부 칩
node("_input_photos", 2.0, 3.5, "core", w=1.85, h=0.5, fs=10)
node("load_image", 4.0, 3.5, "core", w=1.75, h=0.5, fs=10)
node("measure", 5.55, 3.5, "core", w=1.4, h=0.5, fs=10)
node("decide", 6.9, 3.5, "core", w=1.3, h=0.5, fs=10)
node("crosscheck_file_sizes", 3.0, 2.35, "core", w=2.9, h=0.5, fs=9.5)
node("plan_copies", 6.0, 2.35, "core", w=1.9, h=0.5, fs=10)
ax.text(5.45, 3.96, "장마다 반복", fontsize=11, color=MUT, family=KR, ha="center", zorder=3)
for a, b in [("_input_photos", "load_image"), ("load_image", "measure"),
             ("measure", "decide")]:
    edge(a, b, GREY, 1.3, 0.0, ms=9, z=3)
edge("decide", "crosscheck_file_sizes", GREY, 1.3, -0.35, ms=9, z=3)
edge("crosscheck_file_sizes", "plan_copies", GREY, 1.3, 0.0, ms=9, z=3)

# 실행기 칩
node("find_collisions", 9.9, 3.4, "core", w=2.3, h=0.5, fs=10)
node("execute_copies", 12.7, 3.4, "core", w=2.3, h=0.5, fs=10)
node("write_results_csv", 9.85, 2.3, "core", w=2.5, h=0.5, fs=9.5)
node("write_run_json", 12.2, 2.3, "core", w=2.2, h=0.5, fs=9.5)
node("write_copy_log", 11.0, 1.6, "core", w=2.3, h=0.5, fs=9.5)

# ── 진입점 ──────────────────────────────────────────────────────────────────
node("cli.main", 2.9, 13.4, "cli", w=2.5, h=0.78, fs=13.5, bold=True)
node("app.main", 12.0, 13.4, "gui", w=2.5, h=0.78, fs=13.5, bold=True)

# ── CLI ─────────────────────────────────────────────────────────────────────
node("_preparse_lang", 1.5, 11.9, "cli", w=2.1, h=0.5, fs=10)
node("resolve_language", 3.7, 11.9, "cli", w=2.3, h=0.5, fs=10)
node("_build_parser", 5.2, 10.9, "cli", w=2.0, h=0.5, fs=10)
node("summarize", 1.7, 6.7, "cli", w=1.9, h=0.55, fs=10.5)

# ── GUI 부팅 ────────────────────────────────────────────────────────────────
node("load_settings", 8.1, 12.4, "gui", w=2.1, h=0.5, fs=10)
node("LanguageDialog", 15.4, 12.4, "gui", w=2.3, h=0.5, fs=10)
node("MainWindow", 12.0, 11.7, "gui", w=2.5, h=0.66, fs=12, bold=True)

# ── GUI 분류 ────────────────────────────────────────────────────────────────
node("SortWorker.run", 8.3, 9.9, "gui", w=2.6, h=0.6, fs=11)
node("project.open_project", 7.9, 8.3, "gui", w=2.9, h=0.6, fs=10.5)
node("project.apply_copies", 10.9, 8.3, "gui", w=2.9, h=0.6, fs=10.5)
node("file_fingerprint", 6.6, 6.6, "gui", w=2.4, h=0.5, fs=9.5)
node("DecisionStore.get", 9.1, 6.6, "gui", w=2.5, h=0.5, fs=9.5)
node("dest_subfolder", 11.5, 6.6, "gui", w=2.2, h=0.5, fs=9.5)

# ── GUI 썸네일 ──────────────────────────────────────────────────────────────
node("_ThumbRunner.run", 14.3, 9.9, "gui", w=2.6, h=0.6, fs=10.5)
node("get_thumb", 14.3, 8.2, "gui", w=2.0, h=0.55, fs=11)

# ── GUI 크게보기·수정·되돌리기 ──────────────────────────────────────────────
node("DetailPage", 17.7, 9.9, "gui", w=2.2, h=0.6, fs=11)
node("_set_human", 16.7, 8.3, "gui", w=1.9, h=0.5, fs=10)
node("_undo", 18.9, 8.3, "gui", w=1.5, h=0.5, fs=10)
node("project.set_human", 16.7, 6.7, "gui", w=2.5, h=0.55, fs=9.5)
node("project.undo", 18.9, 6.7, "gui", w=1.9, h=0.55, fs=9.5)
node("store.set", 16.2, 5.2, "gui", w=1.7, h=0.48, fs=9.5)
node("_move_copy", 18.3, 5.2, "gui", w=1.8, h=0.48, fs=9.5)
node("_append_move_log", 17.3, 4.35, "gui", w=2.5, h=0.48, fs=9.5)

# ── 엣지: CLI (보라) ────────────────────────────────────────────────────────
for t in ["_preparse_lang", "resolve_language", "_build_parser"]:
    edge("cli.main", t, VIOLET, 1.6, 0.0, ms=12)
edge("cli.main", "run@top", VIOLET, 2.6, 0.10, ms=17)          # → run 파이프라인
edge("cli.main", "summarize", VIOLET, 1.8, 0.0, ms=13)
edge("cli.main", "exec@top", VIOLET, 2.4, 0.26, ms=16)         # → 실행기

# ── 엣지: GUI (주황) ────────────────────────────────────────────────────────
edge("app.main", "load_settings", ORANGE, 1.6, 0.0, ms=12)
edge("app.main", "LanguageDialog", ORANGE, 1.6, 0.0, ms=12)
edge("app.main", "MainWindow", ORANGE, 2.2, 0.0, ms=15, z=5)
edge("MainWindow", "SortWorker.run", ORANGE, 2.0, 0.0, ms=14)
edge("MainWindow", "_ThumbRunner.run", ORANGE, 2.0, 0.0, ms=14)
edge("MainWindow", "DetailPage", ORANGE, 1.8, 0.14, ms=13)     # 더블클릭 _open_detail
edge("SortWorker.run", "project.open_project", ORANGE, 1.8, 0.05, ms=13)
edge("SortWorker.run", "project.apply_copies", ORANGE, 1.8, -0.12, ms=13)
edge("project.open_project", "run@top", ORANGE, 2.4, -0.20, ms=16)  # → run (v1_run)
for t in ["file_fingerprint", "DecisionStore.get", "dest_subfolder"]:
    edge("project.open_project", t, ORANGE, 1.5, 0.0, ms=11)
edge("project.apply_copies", "exec@top", ORANGE, 2.4, -0.05, ms=16)  # → 실행기
edge("_ThumbRunner.run", "get_thumb", ORANGE, 1.8, 0.0, ms=13)
edge("DetailPage", "_set_human", ORANGE, 1.6, 0.0, ms=12)
edge("DetailPage", "_undo", ORANGE, 1.6, 0.0, ms=12)
edge("_set_human", "project.set_human", ORANGE, 1.6, 0.0, ms=12)
edge("_undo", "project.undo", ORANGE, 1.6, 0.0, ms=12)
for t in ["store.set", "_move_copy", "_append_move_log"]:
    edge("project.set_human", t, ORANGE, 1.4, 0.0, ms=11)

# ── 수렴 강조 라벨 ──────────────────────────────────────────────────────────
ax.text(5.15, 5.82, "v1_run =\ncolorsort.cli.run", fontsize=11, color=ORANGE,
        family=KR, ha="center", va="center", zorder=8,
        bbox=dict(boxstyle="round,pad=0.24", fc="white", ec=tint(ORANGE, 0.5), lw=1.0))
ax.text(11.6, 5.0, "--apply 시 양쪽이 같은 함수 호출", fontsize=11, color=INK2,
        family=KR, ha="center", va="center", zorder=8,
        bbox=dict(boxstyle="round,pad=0.24", fc="white", ec="none"))
ax.text(14.3, 7.62, "→ load_image (코어) 재사용", fontsize=11, color=MUT,
        family=KR, ha="center", va="center", zorder=8)

# ── 제목 · 범례 ─────────────────────────────────────────────────────────────
ax.text(0.5, H - 0.5, "함수 콜 그래프", fontsize=25, color=INK, family=KR, fontweight="bold")
ax.text(0.5, H - 1.0, "두 진입점에서 시작하는 주요 함수 호출 — 공유 코어는 한 번만 그렸다",
        fontsize=14, color=INK2, family=KR)
lx, ly = 6.7, H - 0.55
for i, (c, lab) in enumerate([(VIOLET, "CLI 호출"), (ORANGE, "GUI 호출"),
                              (COREC, "공유 코어 함수")]):
    yy = ly - i * 0.0
    ax.add_patch(FancyBboxPatch((lx + i * 3.3, ly - 0.16), 0.34, 0.30,
                 boxstyle="round,pad=0,rounding_size=0.06",
                 facecolor=tint(c, 0.13), edgecolor=c, linewidth=1.8))
    ax.text(lx + i * 3.3 + 0.5, ly, lab, fontsize=12, color=INK2, family=KR, va="center")

OUT = Path(__file__).resolve().parent.parent / "08-call-graph.png"
fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)
