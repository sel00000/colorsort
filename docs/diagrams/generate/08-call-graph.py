"""08-call-graph.png — 함수 콜 그래프.

두 진입점(CLI=보라, GUI=주황)에서 시작하는 주요 함수 호출.
공유 코어 함수는 한 번만 그려 양쪽 화살표가 모이게 한다.

한/영 두 장을 만든다:  python3 08-call-graph.py ko  |  python3 08-call-graph.py en

좌표는 예전 그림의 좌표계(20.0 x 15.8)를 그대로 쓰고, px()/py() 가 새 캔버스
(25.5 x 20.0)로 늘려 준다 — 상대 배치를 손대지 않고 글자만 키우기 위해서다.
노드 폭은 글자 수에서 자동 계산한다(+20pt 에서 예전 고정 폭은 전부 모자란다).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams
import matplotlib.patheffects as _pe
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

# ── 큰 글자 상수 (2026-07 확정 · _common.py와 같은 값 — 이 파일은 자체 완결) ──
S, FB, STROKE = 1.45, 20, 1.1
LANG = "en" if "en" in sys.argv[1:] else "ko"
SUF = "" if LANG == "ko" else "-en"

# ── 영어 번역표 (노드 이름은 전부 코드 식별자라 번역하지 않는다) ─────────────
EN = {
    "함수 콜 그래프": "Function Call Graph",
    "두 진입점에서 시작하는 주요 함수 호출 — 공유 코어는 한 번만 그렸다":
        "Main function calls from the two entry points — "
        "the shared core is drawn once",
    "명령줄 (CLI)": "Command line (CLI)",
    "① 부팅": "① Boot",
    "② 분류 (Sort)": "② Sort",
    "③ 썸네일": "③ Thumbnails",
    "④ 크게 보기 · 수정 · 되돌리기": "④ Detail view · edit · undo",
    "공유 코어 — 두 진입점이 여기서 만난다 (함수 한 벌)":
        "Shared core — where the two entry points meet (one set of functions)",
    "run  (v1_run) — 판정 파이프라인": "run  (v1_run) — verdict pipeline",
    "복사 · 기록 실행기": "Copy · record executor",
    "장마다 반복": "per photo",
    "--apply 시 양쪽이 같은 함수 호출": "with --apply both call the same functions",
    "→ load_image (코어) 재사용": "→ reuses load_image (core)",
    "CLI 호출": "CLI calls",
    "GUI 호출": "GUI calls",
    "공유 코어 함수": "shared core function",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


def heavy(color):
    """bold 글자를 한 단계 더 굵게 보이게 하는 같은 색 외곽선."""
    return [_pe.withStroke(linewidth=STROKE, foreground=color)]


INK, INK2, MUT = "#0b0b0b", "#52514e", "#898781"
VIOLET, ORANGE, GREY = "#4a3aa7", "#d1591f", "#7d7c77"
COREC = "#3f6b52"          # 공유 코어 = 짙은 초록빛 회색 (중립·의미색과 구분)


def tint(hexc, tt):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(((c * tt + 255 * (1 - tt)) / 255.0) for c in (r, g, b))


W, H = 25.5, 20.0
OW, OH = 20.0, 15.8               # 예전 좌표계 — 아래 좌표는 전부 이 기준이다
SX, SY = W / OW, H / OH


def px(x):
    return x * SX


def py(y):
    return y * SY


def char_w(fs):
    """Consolas 한 글자의 데이터 단위 폭 (fs 는 +FB 전 크기)."""
    return (max(fs, 11.5) + FB) / 72.0 / S * 0.55


fig = plt.figure(figsize=(W * S, H * S))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

# ── 노드 등록부 ─────────────────────────────────────────────────────────────
N = {}   # name -> (cx, cy, w, h)  (새 좌표계)
COL = {"cli": VIOLET, "gui": ORANGE, "core": COREC}


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


def node(name, x, y, kind, w=None, h=0.62, fs=11.5, bold=False, label=None,
         pad=0.34):
    """노드 상자. w 를 안 주면 글자 수에서 자동 계산한다."""
    fs = max(fs, 11.5)          # 최소 글자 크기 보장 (사용자가 큰 글자 선호)
    text = label or name
    if w is None:
        w = pad + len(text) * char_w(fs)
    cx, cy = px(x), py(y)
    N[name] = (cx, cy, w, h)
    c = COL[kind]
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.10",
        facecolor=tint(c, 0.13), edgecolor=c,
        linewidth=(2.0 if bold else 1.6) * S, zorder=6))
    T(cx, cy, text, fs, INK, MONO, "bold" if bold else "normal",
      ha="center", va="center", z=7)


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
        p0, p1, arrowstyle="-|>", mutation_scale=ms * S, lw=lw * S, color=color,
        alpha=alpha, connectionstyle=f"arc3,rad={rad}", zorder=z,
        linestyle="--" if dashed else "-",
        shrinkA=1, shrinkB=1, joinstyle="round", capstyle="round"))


def cluster(x0, y0, x1, y1, color, label, lx=None, ly=None):
    X0, Y0, X1, Y1 = px(x0), py(y0), px(x1), py(y1)
    ax.add_patch(FancyBboxPatch(
        (X0, Y0), X1 - X0, Y1 - Y0, boxstyle="round,pad=0,rounding_size=0.16",
        facecolor=tint(color, 0.05), edgecolor=tint(color, 0.5), linewidth=1.4 * S,
        linestyle=(0, (6, 4)), zorder=0))
    T(px(lx) if lx is not None else X0 + 0.32,
      py(ly) if ly is not None else Y1 - 0.44,
      t(label), 13, color, KR, "bold", ha="left", va="center", z=1)


# ── 클러스터 배경 ───────────────────────────────────────────────────────────
cluster(0.4, 6.0, 6.2, 14.2, VIOLET, "명령줄 (CLI)")
cluster(6.5, 11.1, 19.6, 14.2, ORANGE, "① 부팅")
cluster(6.5, 5.7, 12.6, 10.8, ORANGE, "② 분류 (Sort)")
cluster(12.85, 7.3, 15.6, 10.8, ORANGE, "③ 썸네일")
cluster(15.85, 3.85, 19.75, 11.0, ORANGE, "④ 크게 보기 · 수정 · 되돌리기")
cluster(0.4, 0.75, 15.35, 5.35, COREC,
        "공유 코어 — 두 진입점이 여기서 만난다 (함수 한 벌)")

# ── 코어 내부 상자: run + 실행기 ─────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((px(0.8), py(1.1)), px(7.55) - px(0.8),
             py(4.65) - py(1.1),
             boxstyle="round,pad=0,rounding_size=0.12", facecolor="white",
             edgecolor=COREC, linewidth=1.8 * S, zorder=2))
T(px(4.175), py(4.28), t("run  (v1_run) — 판정 파이프라인"), 12.5, COREC, KR,
  "bold", ha="center", va="center", z=3)
ax.add_patch(FancyBboxPatch((px(7.95), py(1.1)), px(14.95) - px(7.95),
             py(4.65) - py(1.1),
             boxstyle="round,pad=0,rounding_size=0.12", facecolor="white",
             edgecolor=COREC, linewidth=1.8 * S, zorder=2))
T(px(11.45), py(4.28), t("복사 · 기록 실행기"), 12.5, COREC, KR, "bold",
  ha="center", va="center", z=3)
# 수렴 화살표가 상자(함수 묶음)를 겨냥하도록 얇은 앵커를 둔다
N["run@top"] = (px(4.175), py(4.62), 5.0, 0.08)
N["exec@top"] = (px(11.45), py(4.62), 4.5, 0.08)

# run 내부 칩
node("_input_photos", 1.97, 3.45, "core", h=0.68, fs=10, pad=0.26)
node("load_image", 3.88, 3.45, "core", h=0.68, fs=10, pad=0.26)
node("measure", 5.39, 3.45, "core", h=0.68, fs=10, pad=0.26)
node("decide", 6.64, 3.45, "core", h=0.68, fs=10, pad=0.26)
node("crosscheck_file_sizes", 2.55, 2.25, "core", h=0.68, fs=9.5)
node("plan_copies", 5.55, 2.25, "core", h=0.68, fs=10)
T(px(4.3), py(3.93), t("장마다 반복"), 11, MUT, KR, ha="center", va="center", z=3)
for a, b in [("_input_photos", "load_image"), ("load_image", "measure"),
             ("measure", "decide")]:
    edge(a, b, GREY, 1.3, 0.0, ms=9, z=3)
edge("decide", "crosscheck_file_sizes", GREY, 1.3, -0.35, ms=9, z=3)
edge("crosscheck_file_sizes", "plan_copies", GREY, 1.3, 0.0, ms=9, z=3)

# 실행기 칩
node("find_collisions", 9.35, 3.45, "core", h=0.68, fs=10)
node("execute_copies", 12.6, 3.45, "core", h=0.68, fs=10)
node("write_results_csv", 9.35, 2.45, "core", h=0.68, fs=9.5)
node("write_run_json", 12.6, 2.45, "core", h=0.68, fs=9.5)
node("write_copy_log", 11.0, 1.55, "core", h=0.68, fs=9.5)

# ── 진입점 ──────────────────────────────────────────────────────────────────
node("cli.main", 2.9, 13.15, "cli", w=2.9, h=1.02, fs=13.5, bold=True)
node("app.main", 12.0, 13.15, "gui", w=2.9, h=1.02, fs=13.5, bold=True)

# ── CLI ─────────────────────────────────────────────────────────────────────
node("_preparse_lang", 1.53, 11.9, "cli", h=0.68, fs=10)
node("resolve_language", 3.98, 11.9, "cli", h=0.68, fs=10)
node("_build_parser", 4.95, 10.85, "cli", h=0.68, fs=10)
node("summarize", 1.7, 6.7, "cli", h=0.72, fs=10.5)

# ── GUI 부팅 ────────────────────────────────────────────────────────────────
node("load_settings", 8.1, 12.3, "gui", h=0.68, fs=10)
node("LanguageDialog", 15.45, 12.3, "gui", h=0.68, fs=10)
node("MainWindow", 12.0, 11.65, "gui", w=2.9, h=0.86, fs=12, bold=True)

# ── GUI 분류 ────────────────────────────────────────────────────────────────
node("SortWorker.run", 8.3, 9.9, "gui", h=0.78, fs=11)
node("project.open_project", 7.9, 8.3, "gui", h=0.78, fs=10.5)
node("project.apply_copies", 11.0, 8.3, "gui", h=0.78, fs=10.5)
node("file_fingerprint", 6.55, 6.55, "gui", h=0.68, fs=9.5)
node("DecisionStore.get", 9.2, 6.55, "gui", h=0.68, fs=9.5)
node("dest_subfolder", 11.65, 6.55, "gui", h=0.68, fs=9.5)

# ── GUI 썸네일 ──────────────────────────────────────────────────────────────
node("_ThumbRunner.run", 14.2, 9.9, "gui", h=0.78, fs=10.5)
node("get_thumb", 14.2, 8.2, "gui", h=0.72, fs=11)

# ── GUI 크게보기·수정·되돌리기 ──────────────────────────────────────────────
node("DetailPage", 17.8, 9.9, "gui", h=0.78, fs=11)
node("_set_human", 16.75, 8.3, "gui", h=0.68, fs=10)
node("_undo", 18.95, 8.3, "gui", h=0.68, fs=10)
node("project.set_human", 16.6, 6.7, "gui", h=0.72, fs=9.5, pad=0.28)
node("project.undo", 18.95, 6.7, "gui", h=0.72, fs=9.5, pad=0.28)
node("store.set", 16.3, 5.2, "gui", h=0.68, fs=9.5)
node("_move_copy", 18.4, 5.2, "gui", h=0.68, fs=9.5)
node("_append_move_log", 17.35, 4.3, "gui", h=0.68, fs=9.5)

# ── 엣지: CLI (보라) ────────────────────────────────────────────────────────
for tgt in ["_preparse_lang", "resolve_language", "_build_parser"]:
    edge("cli.main", tgt, VIOLET, 1.6, 0.0, ms=12)
edge("cli.main", "run@top", VIOLET, 2.6, 0.10, ms=17)          # → run 파이프라인
edge("cli.main", "summarize", VIOLET, 1.8, 0.0, ms=13)
edge("cli.main", "exec@top", VIOLET, 2.4, 0.26, ms=16)         # → 실행기

# ── 엣지: GUI (주황) ────────────────────────────────────────────────────────
edge("app.main", "load_settings", ORANGE, 1.6, 0.0, ms=12)
edge("app.main", "LanguageDialog", ORANGE, 1.6, 0.0, ms=12)
edge("app.main", "MainWindow", ORANGE, 2.2, 0.0, ms=15, z=5)
edge("MainWindow", "SortWorker.run", ORANGE, 2.0, 0.0, ms=14)
edge("MainWindow", "_ThumbRunner.run", ORANGE, 2.0, 0.0, ms=14)
edge("MainWindow", "DetailPage", ORANGE, 1.8, -0.05, ms=13)     # 더블클릭 _open_detail
edge("SortWorker.run", "project.open_project", ORANGE, 1.8, 0.05, ms=13)
edge("SortWorker.run", "project.apply_copies", ORANGE, 1.8, -0.12, ms=13)
edge("project.open_project", "run@top", ORANGE, 2.4, -0.20, ms=16)  # → run (v1_run)
for tgt in ["file_fingerprint", "DecisionStore.get", "dest_subfolder"]:
    edge("project.open_project", tgt, ORANGE, 1.5, 0.0, ms=11)
edge("project.apply_copies", "exec@top", ORANGE, 2.4, -0.05, ms=16)  # → 실행기
edge("_ThumbRunner.run", "get_thumb", ORANGE, 1.8, 0.0, ms=13)
edge("DetailPage", "_set_human", ORANGE, 1.6, 0.0, ms=12)
edge("DetailPage", "_undo", ORANGE, 1.6, 0.0, ms=12)
edge("_set_human", "project.set_human", ORANGE, 1.6, 0.0, ms=12)
edge("_undo", "project.undo", ORANGE, 1.6, 0.0, ms=12)
for tgt in ["store.set", "_move_copy", "_append_move_log"]:
    edge("project.set_human", tgt, ORANGE, 1.4, 0.0, ms=11)

# ── 수렴 강조 라벨 ──────────────────────────────────────────────────────────
T(px(5.35), py(5.75), "v1_run =\ncolorsort.cli.run", 11, ORANGE, KR,
  ha="center", va="center", z=8, linespacing=1.3,
  bbox=dict(boxstyle="round,pad=0.24", fc="white", ec=tint(ORANGE, 0.5),
            lw=1.0 * S))
T(px(11.9), py(5.05), t("--apply 시 양쪽이 같은 함수 호출"), 11, INK2, KR,
  ha="center", va="center", z=8,
  bbox=dict(boxstyle="round,pad=0.24", fc="white", ec="none"))
T(px(14.25), py(7.55), t("→ load_image (코어) 재사용"), 11, MUT, KR,
  ha="center", va="center", z=8)

# ── 제목 · 범례 ─────────────────────────────────────────────────────────────
T(0.5, H - 0.95, t("함수 콜 그래프"), 25, INK, KR, "bold")
T(0.5, H - 1.72, t("두 진입점에서 시작하는 주요 함수 호출 — 공유 코어는 한 번만 그렸다"),
  14, INK2, KR)
lx, ly = 8.7, H - 0.95
for i, (c, lab) in enumerate([(VIOLET, "CLI 호출"), (ORANGE, "GUI 호출"),
                              (COREC, "공유 코어 함수")]):
    bx = lx + i * 5.3
    ax.add_patch(FancyBboxPatch((bx, ly - 0.24), 0.55, 0.48,
                 boxstyle="round,pad=0,rounding_size=0.10",
                 facecolor=tint(c, 0.13), edgecolor=c, linewidth=1.8 * S))
    T(bx + 0.80, ly, t(lab), 12, INK2, KR, va="center")

# ── 겹침 감시: 노드 상자끼리 겹치거나 캔버스를 벗어나면 보고한다 ─────────────
_boxes = [(n, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
          for n, (cx, cy, w, h) in N.items() if not n.endswith("@top")]
_bad = []
for i in range(len(_boxes)):
    n1, a0, b0, a1, b1 = _boxes[i]
    if a0 < 0.05 or a1 > W - 0.05 or b0 < 0.05 or b1 > H - 0.05:
        _bad.append(f"캔버스 밖: {n1} x[{a0:.2f},{a1:.2f}] y[{b0:.2f},{b1:.2f}]")
    for j in range(i + 1, len(_boxes)):
        n2, c0, d0, c1, d1 = _boxes[j]
        ox = min(a1, c1) - max(a0, c0)
        oy = min(b1, d1) - max(b0, d0)
        if ox > -0.12 and oy > -0.12:
            _bad.append(f"겹침/근접: {n1} ↔ {n2}  여백 x={ox:+.2f} y={oy:+.2f}")
if _bad:
    print(f"[배치 경고 {len(_bad)}건]")
    for b in _bad:
        print("  " + b)

OUT = Path(__file__).resolve().parent.parent / f"08-call-graph{SUF}.png"
fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)
