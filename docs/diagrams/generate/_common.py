"""공용 도우미: 맑은 고딕 등록 + 팔레트 + 그리기 함수.

다이어그램 5장(04·05·06·07·09)이 공유한다. 좌표계는 예전 그대로 두고
figure만 S배 키운다: 스크립트의 좌표 1 단위 = S 인치. dpi 200 고정.
2026-07 '글자 크게' 개정: 모든 글자 +FB pt·bold, 원래 bold였던 글자는
같은 색 외곽선(STROKE pt)으로 한 단계 더 굵게 — 맑은 고딕에 bold 위
굵기가 없어 fontweight로는 더 굵어지지 않기 때문이다.
색은 dataviz 검증 팔레트를 따르되, 파랑/초록 의미색만은 실제 파랑/초록 계열을 쓴다.
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as _pe
from matplotlib import font_manager, rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Circle
from matplotlib.lines import Line2D

# ── 맑은 고딕 등록 (없으면 한글이 □로 깨진다) ──
for _f in ("/home/pc/.local/share/fonts/win-kr/malgun.ttf",
           "/home/pc/.local/share/fonts/win-kr/malgunbd.ttf"):
    font_manager.fontManager.addfont(_f)
rcParams["font.family"] = "Malgun Gothic"
rcParams["axes.unicode_minus"] = False

# ── 큰 글자 상수 (2026-07 확정 · 09번 실측 검증 — 9개 스크립트 공통) ──
S = 1.45       # 기하 배율: figure·선 굵기·화살촉이 S배
FB = 20        # 글자 가산치: 모든 fontsize에 +FB pt
STROKE = 1.1   # 이미 bold인 글자에 덧입히는 같은 색 외곽선(pt)


def get_lang():
    """명령행 인자에서 언어를 읽는다: 'ko'(기본) 또는 'en'."""
    return "en" if "en" in sys.argv[1:] else "ko"


def suffix(lang):
    """출력 파일명 꼬리: ko → '', en → '-en'."""
    return "" if lang == "ko" else "-en"


def heavy_effect(color):
    """bold 글자를 한 단계 더 굵게 보이게 하는 같은 색 외곽선."""
    return [_pe.withStroke(linewidth=STROKE, foreground=color)]


# ── 팔레트 ──
INK    = "#0b0b0b"   # 본문 글자
INK2   = "#43423f"   # 보조 글자
MUTED  = "#6f6d67"   # 흐린 설명 글자
FAINT  = "#9a988f"   # 아주 흐린 선
GRID   = "#e1e0d9"
AXIS   = "#c3c2b7"
WHITE  = "#ffffff"

# 의미색 (실제 파랑/초록 계열)
BLUE      = "#2a78d6"
BLUE_FILL = "#dbe8f8"
GREEN     = "#0a7a35"
GREEN_FILL= "#d7ecdc"
VIOLET    = "#4a3aa7"   # 하이브리드(혼합)
VIOLET_FILL = "#e5e1f4"
AMBER     = "#b57900"   # 검토/기권 경고 계열
AMBER_FILL= "#f9edcf"
RED       = "#c23b3a"   # 오류·강한 기권
RED_FILL  = "#f6dcdb"
GRAY_FILL = "#eceae4"   # 중립 기권·일반 박스
NEUTRAL_FILL = "#f6f6f3"

# 3그룹 배경 밴드 (아주 옅게)
BAND_CORE = "#eef4fc"   # colorsort 코어 데이터
BAND_GUI  = "#ecf7f0"   # colorsortgui 상태/로직
BAND_QT   = "#f3f0fb"   # Qt 화면

# 생명선/데이터 계열용 보조색
ACTOR   = "#111827"
TEAL    = "#158f7a"
ORANGE  = "#d2691e"


def new_fig(w_in, h_in):
    """좌표 1 단위 = S 인치인 축 하나를 가진 figure를 만든다.

    스크립트는 예전 좌표(w_in×h_in)를 그대로 쓰고, 그림만 S배 커진다.
    """
    fig = plt.figure(figsize=(w_in * S, h_in * S), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_in)
    ax.set_ylim(0, h_in)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.invert_yaxis()   # 위에서 아래로 그리는 다이어그램이 편하도록 y를 뒤집는다
    fig.patch.set_facecolor(WHITE)
    return fig, ax


def band(ax, x, y, w, h, color, z=0):
    """배경 밴드(그룹 구분용). 모서리 살짝 둥글게."""
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0,rounding_size=0.10",
                       fc=color, ec="none", zorder=z)
    ax.add_patch(p)
    return p


def rbox(ax, x, y, w, h, fc=WHITE, ec=INK, lw=1.6, rounding=0.09, z=2, ls="-"):
    """둥근 모서리 박스. (x, y)는 좌상단. 선 굵기는 S배로 자동 보정."""
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={rounding}",
                       fc=fc, ec=ec, lw=lw * S, zorder=z, linestyle=ls)
    ax.add_patch(p)
    return p


def label(ax, x, y, s, size=13, color=INK, weight="normal", ha="center",
          va="center", z=6, style="normal", family=None):
    """글자: 무조건 +FB pt·bold. 원래 bold였던 글자는 외곽선으로 더 굵게."""
    kw = {}
    if weight == "bold":
        kw["path_effects"] = heavy_effect(color)
    return ax.text(x, y, s, fontsize=size + FB, color=color, fontweight="bold",
                   ha=ha, va=va, zorder=z, style=style, fontfamily=family,
                   linespacing=1.32, **kw)


def arrow(ax, p1, p2, color=INK, lw=1.9, ls="-", z=4, style="-|>", ms=13,
          cs=None, shrinkA=3, shrinkB=3):
    """실선/점선 화살표. 선 굵기·화살촉은 S배로 자동 보정."""
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms * S,
                        color=color, lw=lw * S, linestyle=ls, zorder=z,
                        shrinkA=shrinkA, shrinkB=shrinkB, connectionstyle=cs)
    ax.add_patch(a)
    return a


def line(ax, p1, p2, color=AXIS, lw=1.4, ls="-", z=1):
    ax.add_line(Line2D([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw * S,
                       linestyle=ls, zorder=z))


def diamond(ax, cx, cy, r=0.11, fc=INK, ec=INK, z=5):
    """UML 집합(◆) 표식 — 실제 폴리곤으로 그린다."""
    pts = [(cx, cy - r * 1.3), (cx + r, cy), (cx, cy + r * 1.3), (cx - r, cy)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=1.3 * S, zorder=z))


def hollow_tri(ax, cx, cy, size=0.16, point="right", ec=INK, fc=WHITE, z=5):
    """UML 상속(◁) 표식 — 속이 빈 삼각형. point 방향이 부모(상위 클래스)를 가리킨다."""
    s = size
    if point == "right":
        pts = [(cx + s, cy), (cx - s, cy - s), (cx - s, cy + s)]
    elif point == "left":
        pts = [(cx - s, cy), (cx + s, cy - s), (cx + s, cy + s)]
    elif point == "up":
        pts = [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)]
    else:  # down
        pts = [(cx, cy + s), (cx - s, cy - s), (cx + s, cy - s)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=1.6 * S, zorder=z))


def checkmark(ax, cx, cy, s=0.12, color=GREEN, lw=2.6, z=7):
    """✓ 글리프는 맑은 고딕에 없다 → 선 두 개로 직접 그린다."""
    ax.add_line(Line2D([cx - s, cx - s * 0.15], [cy + s * 0.05, cy + s * 0.7],
                       color=color, lw=lw * S, zorder=z,
                       solid_capstyle="round"))
    ax.add_line(Line2D([cx - s * 0.15, cx + s * 1.05], [cy + s * 0.7, cy - s * 0.75],
                       color=color, lw=lw * S, zorder=z,
                       solid_capstyle="round"))


# ── 시퀀스 다이어그램 도우미 ──
def lifeline(ax, x, name, sub, y_top, y_bot, color=INK, w=2.3, fill=WHITE):
    """세로 생명선: 위쪽 머리 상자 + 아래로 뻗는 점선.

    머리 상자 1.95×0.66→2.3×0.80: +FB 글자 두 줄이 들어가도록 키웠다
    (예: 'DecisionStore' 13자 × 0.160 ≈ 2.1 데이터 단위).
    """
    rbox(ax, x - w / 2, y_top, w, 0.80, fc=fill, ec=color, lw=1.9,
         rounding=0.08, z=3)
    label(ax, x, y_top + 0.29, name, size=13.5, weight="bold", color=color)
    if sub:
        label(ax, x, y_top + 0.60, sub, size=11, color=MUTED, style="italic")
    ax.add_line(Line2D([x, x], [y_top + 0.80, y_bot], color=AXIS, lw=1.4 * S,
                       linestyle=(0, (4, 4)), zorder=1))


def activation(ax, x, y1, y2, color=INK, w=0.17):
    """활성 막대: 그 생명선이 일하는 구간."""
    ax.add_patch(FancyBboxPatch((x - w / 2, y1), w, y2 - y1,
                 boxstyle="round,pad=0,rounding_size=0.03",
                 fc=WHITE, ec=color, lw=1.5 * S, zorder=2))


def seq_arrow(ax, y, x1, x2, text, color=INK, dashed=False, size=13,
              off=0.15, ms=14):
    """가로 메시지 화살표 + 위쪽 글자. 점선이면 비동기(시그널/반환)."""
    arrow(ax, (x1, y), (x2, y), color=color, lw=1.9,
          ls=((0, (5, 3)) if dashed else "-"), style="-|>", ms=ms, z=5,
          shrinkA=1, shrinkB=1)
    ax.text((x1 + x2) / 2, y - off, text, fontsize=size + FB, color=color,
            ha="center", va="bottom", zorder=6, linespacing=1.3,
            fontweight="bold")


def self_msg(ax, x, y, text, color=INK, w=0.95, h=0.5, size=13, side=1):
    """자기 호출 고리(오른쪽으로 갔다 돌아옴) + 글자."""
    ex = x + side * w
    ax.add_line(Line2D([x, ex], [y, y], color=color, lw=1.8 * S, zorder=5))
    ax.add_line(Line2D([ex, ex], [y, y + h], color=color, lw=1.8 * S, zorder=5))
    arrow(ax, (ex, y + h), (x, y + h), color=color, lw=1.8, style="-|>",
          ms=13, z=5, shrinkA=1, shrinkB=1)
    ax.text(ex + side * 0.16 if side > 0 else ex - 0.16, y + h / 2, text,
            fontsize=size + FB, color=color, ha=("left" if side > 0 else "right"),
            va="center", zorder=6, linespacing=1.3, fontweight="bold")


def note_box(ax, x, y, w, h, text, color=INK2, fill="#fbf7ec", size=11.5,
             ec=None):
    """설명 쪽지."""
    rbox(ax, x, y, w, h, fc=fill, ec=(ec or color), lw=1.3, rounding=0.06, z=4)
    ax.text(x + 0.16, y + h / 2, text, fontsize=size + FB, color=color, ha="left",
            va="center", zorder=6, linespacing=1.32, fontweight="bold")


def phase_tag(ax, x, y, text, color=INK, size=13):
    """구간(Phase) 딱지."""
    ax.text(x, y, text, fontsize=size + FB, color=color, ha="left", va="center",
            fontweight="bold", zorder=6,
            path_effects=heavy_effect(color),
            bbox=dict(boxstyle="round,pad=0.3", fc=WHITE, ec=color, lw=1.4 * S))


def save(fig, out_path):
    fig.savefig(out_path, dpi=200, facecolor=WHITE,
                bbox_inches=None, pad_inches=0)
    plt.close(fig)
