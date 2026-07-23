"""07-flowchart-rules.png / 07-flowchart-rules-en.png — 판정 규칙 decide() 플로우차트.

읽은 코드: colorsort/rules.py(decide), colorsort/config.py, colorsort/models.py.
docstring "검사 순서가 중요하다. 위쪽이 아래쪽을 가린다" 대로 위→아래.
마름모=조건, 사각형=결과. 결과 색: BLUE 파랑, GREEN 초록, HYBRID 보라, ABSTAIN 회색.
저신뢰(is_low_confidence)는 '표시'일 뿐 폴더를 바꾸지 않는다(코드 그대로).

실행: python3 gen_07_flowchart_rules.py ko | en
글자 +20pt·bold 는 _common.py 가 자동 적용한다. 직접 ax.text 를 쓰는 flow()
라벨과 저신뢰 쪽지만 +FB·bold 를 손으로 적용한다.
마름모는 가운데가 제일 넓다 — 여러 줄 질문은 가운데에서 멀어질수록 좁아지므로
줄이 길수록 DW·DH 를 함께 키워야 한다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, rbox, label, line, arrow, save, get_lang, suffix,
                     heavy_effect, FB,
                     INK, INK2, MUTED, AXIS, WHITE, BLUE, GREEN,
                     VIOLET, AMBER, RED)
from matplotlib.patches import Polygon, Circle

LANG = get_lang()
SUF = suffix(LANG)

# ── 영어 번역표 (키 = 한글 원문 그대로, 줄바꿈 포함) ──
# 식별자(max_intermediate_frac, f_blue …)와 폴더명(review/other …)은 번역하지 않는다.
EN = {
    "판정 규칙 — decide() 는 어떻게 색을 정하나":
        "Verdict Rules — How decide() Picks the Color",
    "위에서 아래로 차례로 검사한다. 위 검사가 걸리면 거기서 끝(위가 아래를 가림). "
    "마름모=질문, 사각형=결과.":
        "Checks run top to bottom; the first match wins (upper checks shadow "
        "lower ones).\nDiamond = question, rectangle = result.",
    # 범례
    "결과 색": "Verdict colors",
    "BLUE=파랑": "BLUE=blue",
    "GREEN=초록": "GREEN=green",
    "HYBRID=혼합": "HYBRID=mixed",
    "ABSTAIN=기권→사람 검토": "ABSTAIN=abstain → human review",
    # 시작
    "measure() 결과 → decide()": "measure() result → decide()",
    # 상단 폭포 5문항
    "투명 픽셀이 있는가?": "Any transparent pixels?",
    "투명 — 배경과 구분 불가": "transparent pixels",
    "빨강이 있는가?  (max_red>0)": "Any red?  (max_red>0)",
    "색공간 이상": "color-space anomaly",
    "밝은 픽셀이 부족한가?\n(gate_used 없음)": "Too few lit pixels?\n(no gate_used)",
    "무신호 — 근거 없음": "no signal — no evidence",
    "중간색이 10%를 넘는가?\n(> max_intermediate_frac)":
        "Intermediates over 10%?\n(> max_intermediate_frac)",
    "중간색 과다 — 제3의 색": "too many intermediates",
    "파랑·초록이 하나도 없나?\n(n_blue+n_green = 0)":
        "No blue and no green?\n(n_blue+n_green = 0)",
    "전부 중간색": "all intermediate",
    # 6~8 문항
    "순수 파랑 또는 초록인가?\n(f_blue≥0.98 & n_green<50\n또는 ≤0.02 & n_blue<50)":
        "Pure blue or pure green?\n(f_blue≥0.98 & n_green<50\n"
        "or ≤0.02 & n_blue<50)",
    "밝기가 불일치하는가?\n(gap > 0.10)": "Brightness inconsistent?\n(gap > 0.10)",
    "파랑·초록 둘 다 50장 이상?\nmin(n_blue, n_green) ≥ 50":
        "Both blue and green ≥ 50?\nmin(n_blue, n_green) ≥ 50",
    # 결과 상자
    "불일치·review/other": "inconsistent · review/other",
    "→ blue/": "→ blue/", "→ green/": "→ green/",
    "혼합 · review/mixed": "mixed · review/mixed",
    "애매함(소수파 부족) · review/other":
        "ambiguous (minority too small) · review/other",
    "순수 파랑이면 BLUE\n순수 초록이면 GREEN":
        "pure blue → BLUE\npure green → GREEN",
    # 화살표 라벨
    "예": "yes", "아니오": "no", "예 (순수)": "yes (pure)",
    # 저신뢰 쪽지
    "게이트가 완화되면 '저신뢰' 표시가 붙지만\n"
    "폴더는 그대로 blue/green. (review 로 보내지 않음\n"
    "— results.csv 신뢰도 칸·요약에만 표시)":
        "A relaxed gate adds a 'low confidence' flag —\n"
        "the folder stays blue/green (not sent to review).\n"
        "Shown only in results.csv & the summary.",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


W, H = 19.9, 23.5
fig, ax = new_fig(W, H)

DIA_FILL = "#eef1f5"
ABST_FILL = "#eceae4"
ABST_EC = "#8b897f"


def dia(cx, cy, w, h, text, size=13, fill=DIA_FILL, ec=INK2):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, fc=fill, ec=ec, lw=1.9 * 1.45,
                         zorder=3))
    label(ax, cx, cy, t(text), size=size, color=INK, z=6)
    return {"t": (cx, cy - h / 2), "r": (cx + w / 2, cy),
            "b": (cx, cy + h / 2), "l": (cx - w / 2, cy), "c": (cx, cy)}


def result(x, y, w, h, title, sub, fill, ec, tcol):
    rbox(ax, x, y, w, h, fc=fill, ec=ec, lw=2.0, rounding=0.08, z=3)
    label(ax, x + w / 2, y + h * 0.36, title, size=15, weight="bold", color=tcol)
    label(ax, x + w / 2, y + h * 0.72, sub, size=11.5, color=INK2)
    return {"t": (x + w / 2, y), "l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "b": (x + w / 2, y + h)}


def badge(cx, cy, n, color=INK2):
    ax.add_patch(Circle((cx, cy), 0.30, fc=color, ec="none", zorder=7))
    label(ax, cx, cy, str(n), size=12.5, weight="bold", color=WHITE, z=8)


def flow(p1, p2, label_text=None, color=INK, lx=0.0, ly=0.0, dashed=False):
    """화살표 + 라벨. 라벨은 직접 ax.text 라 +FB·bold 를 손으로 적용한다."""
    arrow(ax, p1, p2, color=color, lw=1.9, style="-|>", ms=14, z=4,
          ls=("--" if dashed else "-"), shrinkA=2, shrinkB=2)
    if label_text:
        ax.text((p1[0] + p2[0]) / 2 + lx, (p1[1] + p2[1]) / 2 + ly,
                t(label_text), fontsize=11.5 + FB, color=color, ha="center",
                va="center", zorder=7, fontweight="bold",
                path_effects=heavy_effect(color),
                bbox=dict(boxstyle="round,pad=0.18", fc=WHITE, ec="none"))


# 제목
label(ax, W / 2, 0.60, t("판정 규칙 — decide() 는 어떻게 색을 정하나"),
      size=24, weight="bold", color=INK)
label(ax, W / 2, 1.35 if LANG == "ko" else 1.30,
      t("위에서 아래로 차례로 검사한다. 위 검사가 걸리면 거기서 끝(위가 아래를 가림). "
        "마름모=질문, 사각형=결과."), size=12.5, color=MUTED)

# 범례
rbox(ax, 10.60, 1.82, 8.85, 1.72, fc=WHITE, ec=AXIS, lw=1.3, rounding=0.06, z=2)
label(ax, 10.85, 2.24, t("결과 색"), size=12, weight="bold", color=INK,
      ha="left")
for i, (tx, c) in enumerate([("BLUE=파랑", BLUE), ("GREEN=초록", GREEN),
                             ("HYBRID=혼합", VIOLET),
                             ("ABSTAIN=기권→사람 검토", ABST_EC)]):
    yy = 2.80 + (i // 2) * 0.47
    xx = 10.85 + (i % 2) * 2.80
    rbox(ax, xx, yy - 0.15, 0.30, 0.30, fc=c, ec=c, lw=1, rounding=0.03, z=3)
    label(ax, xx + 0.44, yy, t(tx), size=11, color=INK2, ha="left")

XC = 4.8            # 마름모 세로 중심선
DW, DH = 5.6, 2.1
XE = 10.6           # 오른쪽 기권 상자 x
EW, EH = 7.0, 1.4

# 시작
rbox(ax, XC - 2.2, 1.85, 4.4, 0.85, fc="#dfeaf7", ec=BLUE, lw=1.8,
     rounding=0.3, z=3)
label(ax, XC, 2.28, t("measure() 결과 → decide()"), size=12.5, weight="bold",
      color=BLUE)

# ── 상단 폭포: 문제가 있으면 즉시 ABSTAIN ──
checks = [
    (4.35, "투명 픽셀이 있는가?", "투명 — 배경과 구분 불가", "review/other"),
    (6.75, "빨강이 있는가?  (max_red>0)", "색공간 이상", "review/other"),
    (9.15, "밝은 픽셀이 부족한가?\n(gate_used 없음)", "무신호 — 근거 없음",
     "review/no-signal"),
    (11.55, "중간색이 10%를 넘는가?\n(> max_intermediate_frac)",
     "중간색 과다 — 제3의 색", "review/other"),
    (13.95, "파랑·초록이 하나도 없나?\n(n_blue+n_green = 0)", "전부 중간색",
     "review/other"),
]
prev = (XC, 2.70)   # start 아래
for i, (cy, q, why, folder) in enumerate(checks, start=1):
    d = dia(XC, cy, DW, DH, q)
    badge(XC - DW / 2 + 0.15, cy - DH / 2 + 0.15, i)
    flow(prev, d["t"], color=INK)
    box = result(XE, cy - EH / 2, EW, EH, "ABSTAIN",
                 f"{t(why)}   ·   {folder}", ABST_FILL, ABST_EC, INK2)
    flow(d["r"], box["l"], "예", color=RED)
    prev = d["b"]

# ── 6. 순수 파랑/초록? ──
d6 = dia(XC, 16.55, 6.0, 2.8,
         "순수 파랑 또는 초록인가?\n(f_blue≥0.98 & n_green<50\n또는 ≤0.02 & n_blue<50)",
         size=12)
badge(XC - 3.0 + 0.15, 16.55 - 1.4 + 0.15, 6)
flow(prev, d6["t"], color=INK)

# ── 7. 순수면 → 밝기 일관성 검사 → BLUE/GREEN ──
d7 = dia(12.00, 16.55, 5.0, 2.0, "밝기가 불일치하는가?\n(gap > 0.10)", size=13)
badge(12.00 - 2.5 + 0.15, 16.55 - 1.0 + 0.15, 7)
flow(d6["r"], d7["l"], "예 (순수)", color=GREEN)

incon = result(15.20, 15.85, 4.30, EH, "ABSTAIN", t("불일치·review/other"),
               ABST_FILL, ABST_EC, INK2)
flow(d7["r"], incon["l"], "예", color=RED)

blue_b = result(9.90, 18.15, 2.60, EH, "BLUE", t("→ blue/"), "#dbe8f8", BLUE,
                BLUE)
green_b = result(13.10, 18.15, 2.60, EH, "GREEN", t("→ green/"), "#d7ecdc",
                 GREEN, GREEN)
flow(d7["b"], (11.20, 18.15), "아니오", color=INK, ly=0.0)
flow((12.00, 17.55), (14.40, 18.15), color=INK)
label(ax, 17.70, 18.85, t("순수 파랑이면 BLUE\n순수 초록이면 GREEN"), size=11,
      color=MUTED, ha="center")

# ── 8. 순수가 아니면 → 하이브리드 또는 애매 ──
d8 = dia(XC, 20.40, 5.6, 2.1,
         "파랑·초록 둘 다 50장 이상?\nmin(n_blue, n_green) ≥ 50", size=13)
badge(XC - 2.8 + 0.15, 20.40 - 1.05 + 0.15, 8)
flow(d6["b"], d8["t"], "아니오", color=INK)

hybrid = result(8.60, 19.85, 3.60, EH, "HYBRID", t("혼합 · review/mixed"),
                "#e5e1f4", VIOLET, VIOLET)
flow(d8["r"], hybrid["l"], "예", color=VIOLET)

amb = result(1.30, 22.00, 7.20, EH, "ABSTAIN",
             t("애매함(소수파 부족) · review/other"), ABST_FILL, ABST_EC, INK2)
flow(d8["b"], amb["t"], "아니오", color=RED)

# 저신뢰 주석 (폴더를 바꾸지 않는다 — 코드 그대로)
rbox(ax, 12.40, 20.10, 7.40, 1.53, fc="#fbf1d8", ec=AMBER, lw=1.4,
     rounding=0.06, z=3)
ax.text(12.62, 20.87,
        t("게이트가 완화되면 '저신뢰' 표시가 붙지만\n"
          "폴더는 그대로 blue/green. (review 로 보내지 않음\n"
          "— results.csv 신뢰도 칸·요약에만 표시)"),
        fontsize=11 + FB, color=INK2, ha="left", va="center", zorder=6,
        linespacing=1.32, fontweight="bold")

out = Path(__file__).resolve().parent.parent / f"07-flowchart-rules{SUF}.png"
save(fig, out)
print("saved", out)
