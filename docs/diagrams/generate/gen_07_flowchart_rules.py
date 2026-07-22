"""07-flowchart-rules.png — 판정 규칙 decide() 플로우차트.

읽은 코드: colorsort/rules.py(decide), colorsort/config.py, colorsort/models.py.
docstring "검사 순서가 중요하다. 위쪽이 아래쪽을 가린다" 대로 위→아래.
마름모=조건, 사각형=결과. 결과 색: BLUE 파랑, GREEN 초록, HYBRID 보라, ABSTAIN 회색.
저신뢰(is_low_confidence)는 '표시'일 뿐 폴더를 바꾸지 않는다(코드 그대로).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, rbox, label, line, arrow, save,
                     INK, INK2, MUTED, FAINT, AXIS, GRID, WHITE, BLUE, GREEN,
                     VIOLET, AMBER, TEAL, RED)
from matplotlib.patches import Polygon, Circle

W, H = 15.6, 18.4
fig, ax = new_fig(W, H)

DIA_FILL = "#eef1f5"
ABST_FILL = "#eceae4"
ABST_EC = "#8b897f"


def dia(cx, cy, w, h, text, size=13, fill=DIA_FILL, ec=INK2):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, fc=fill, ec=ec, lw=1.9, zorder=3))
    label(ax, cx, cy, text, size=size, color=INK, z=6)
    return {"t": (cx, cy - h / 2), "r": (cx + w / 2, cy),
            "b": (cx, cy + h / 2), "l": (cx - w / 2, cy), "c": (cx, cy)}


def result(x, y, w, h, title, sub, fill, ec, tcol):
    rbox(ax, x, y, w, h, fc=fill, ec=ec, lw=2.0, rounding=0.08, z=3)
    label(ax, x + w / 2, y + h * 0.36, title, size=15, weight="bold", color=tcol)
    label(ax, x + w / 2, y + h * 0.72, sub, size=11.5, color=INK2)
    return {"t": (x + w / 2, y), "l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "b": (x + w / 2, y + h)}


def badge(cx, cy, n, color=INK2):
    ax.add_patch(Circle((cx, cy), 0.22, fc=color, ec="none", zorder=7))
    label(ax, cx, cy, str(n), size=12.5, weight="bold", color=WHITE, z=8)


def flow(p1, p2, label_text=None, color=INK, lx=0.0, ly=0.0, dashed=False):
    arrow(ax, p1, p2, color=color, lw=1.9, style="-|>", ms=14, z=4,
          ls=("--" if dashed else "-"), shrinkA=2, shrinkB=2)
    if label_text:
        ax.text((p1[0] + p2[0]) / 2 + lx, (p1[1] + p2[1]) / 2 + ly, label_text,
                fontsize=11.5, color=color, ha="center", va="center", zorder=7,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.18", fc=WHITE, ec="none"))


# 제목
label(ax, W / 2, 0.42, "판정 규칙 — decide() 는 어떻게 색을 정하나",
      size=24, weight="bold", color=INK)
label(ax, W / 2, 0.8,
      "위에서 아래로 차례로 검사한다. 위 검사가 걸리면 거기서 끝(위가 아래를 가림). "
      "마름모=질문, 사각형=결과.", size=12.5, color=MUTED)

# 범례
rbox(ax, 8.55, 1.2, 6.7, 1.15, fc=WHITE, ec=AXIS, lw=1.3, rounding=0.06, z=2)
label(ax, 8.75, 1.46, "결과 색", size=12, weight="bold", color=INK, ha="left")
for i, (t, c, cf) in enumerate([("BLUE=파랑", BLUE, BLUE), ("GREEN=초록", GREEN, GREEN),
                                ("HYBRID=혼합", VIOLET, VIOLET),
                                ("ABSTAIN=기권→사람 검토", ABST_EC, INK2)]):
    yy = 1.75 + (i // 2) * 0.4
    xx = 8.75 + (i % 2) * 3.15
    rbox(ax, xx, yy - 0.13, 0.26, 0.26, fc=c, ec=c, lw=1, rounding=0.03, z=3)
    label(ax, xx + 0.36, yy, t, size=11, color=INK2, ha="left")

# 시작
start = rbox(ax, 2.35, 1.35, 3.3, 0.62, fc="#dfeaf7", ec=BLUE, lw=1.8,
             rounding=0.3, z=3)
label(ax, 4.0, 1.66, "measure() 결과 → decide()", size=12.5, weight="bold",
      color=BLUE)

XC = 4.0            # 마름모 세로 중심선
DW, DH = 3.55, 1.5
XE = 8.3           # 오른쪽 기권 상자 x
EW = 4.4

# ── 상단 폭포: 문제가 있으면 즉시 ABSTAIN ──
checks = [
    (3.05, "투명 픽셀이 있는가?", "투명 — 배경과 구분 불가", "review/other"),
    (4.9, "빨강이 있는가?  (max_red>0)", "색공간 이상", "review/other"),
    (6.75, "밝은 픽셀이 부족한가?\n(gate_used 없음)", "무신호 — 근거 없음", "review/no-signal"),
    (8.6, "중간색이 10%를 넘는가?\n(> max_intermediate_frac)", "중간색 과다 — 제3의 색", "review/other"),
    (10.45, "파랑·초록이 하나도 없나?\n(n_blue+n_green = 0)", "전부 중간색", "review/other"),
]
prev = (4.0, 1.97)   # start 아래
for i, (cy, q, why, folder) in enumerate(checks, start=1):
    d = dia(XC, cy, DW, DH, q)
    badge(XC - DW / 2 + 0.05, cy - DH / 2 + 0.05, i)
    flow(prev, d["t"], color=INK)
    box = result(XE, cy - 0.5, EW, 1.0, "ABSTAIN", f"{why}   ·   {folder}",
                 ABST_FILL, ABST_EC, INK2)
    flow(d["r"], box["l"], "예", color=RED)
    prev = d["b"]

# ── 6. 순수 파랑/초록? ──
d6 = dia(XC, 12.35, DW, 1.65, "순수 파랑 또는 초록인가?\n(f_blue≥0.98 & n_green<50\n또는 ≤0.02 & n_blue<50)",
         size=12)
badge(XC - DW / 2 + 0.05, 12.35 - 0.82 + 0.05, 6)
flow(prev, d6["t"], color=INK)

# ── 7. 순수면 → 밝기 일관성 검사 → BLUE/GREEN ──
d7 = dia(9.6, 12.35, 3.3, 1.45, "밝기가 불일치하는가?\n(gap > 0.10)", size=13)
badge(9.6 - 1.65 + 0.05, 12.35 - 0.72 + 0.05, 7)
flow(d6["r"], d7["l"], "예 (순수)", color=GREEN)

incon = result(13.0, 11.9, 2.5, 0.9, "ABSTAIN", "불일치·review/other",
               ABST_FILL, ABST_EC, INK2)
flow(d7["r"], incon["l"], "예", color=RED)

blue_b = result(8.15, 13.75, 2.55, 0.98, "BLUE", "→ blue/", "#dbe8f8", BLUE, BLUE)
green_b = result(11.05, 13.75, 2.55, 0.98, "GREEN", "→ green/", "#d7ecdc", GREEN, GREEN)
flow(d7["b"], (9.42, 13.75), "아니오", color=INK, ly=0.0)
flow((9.6, 12.95), (12.32, 13.75), color=INK)
label(ax, 12.05, 13.38, "순수 파랑이면 BLUE · 순수 초록이면 GREEN", size=11,
      color=MUTED, ha="center")

# 저신뢰 주석 (폴더를 바꾸지 않는다 — 코드 그대로)
rbox(ax, 8.15, 15.05, 5.5, 0.82, fc="#fbf1d8", ec=AMBER, lw=1.4, rounding=0.06, z=3)
ax.text(8.35, 15.46,
        "게이트가 완화되면 '저신뢰' 표시가 붙지만 폴더는 그대로 blue/green.\n"
        "(review 로 보내지 않음 — results.csv 신뢰도 칸·요약에만 표시)",
        fontsize=11, color=INK2, ha="left", va="center", zorder=6,
        linespacing=1.3)

# ── 8. 순수가 아니면 → 하이브리드 또는 애매 ──
d8 = dia(XC, 15.0, DW, 1.5, "파랑·초록 둘 다 50장 이상?\nmin(n_blue, n_green) ≥ 50",
         size=13)
badge(XC - DW / 2 + 0.05, 15.0 - 0.75 + 0.05, 8)
flow(d6["b"], d8["t"], "아니오", color=INK)

hybrid = result(6.55, 16.0, 3.35, 0.92, "HYBRID", "혼합 · review/mixed",
                "#e5e1f4", VIOLET, VIOLET)
flow(d8["r"], hybrid["l"], "예", color=VIOLET)

amb = result(1.05, 16.55, 4.0, 0.92, "ABSTAIN", "애매함(소수파 부족) · review/other",
             ABST_FILL, ABST_EC, INK2)
flow(d8["b"], amb["t"], "아니오", color=RED)

out = Path(__file__).resolve().parent.parent / "07-flowchart-rules.png"
save(fig, out)
print("saved", out)
