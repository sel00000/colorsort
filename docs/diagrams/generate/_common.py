"""공용 도우미: 맑은 고딕 등록 + 팔레트 + 그리기 함수.

다이어그램 5장이 공유한다. 좌표계는 '인치'로 통일한다(1 데이터 단위 = 1 inch).
dpi 200에서 1 inch = 200px 이므로 폭 계산이 단순하다(예: 가로 15in = 3000px).
색은 dataviz 검증 팔레트를 따르되, 파랑/초록 의미색만은 실제 파랑/초록 계열을 쓴다.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Circle
from matplotlib.lines import Line2D

# ── 맑은 고딕 등록 (없으면 한글이 □로 깨진다) ──
for _f in ("/home/pc/.local/share/fonts/win-kr/malgun.ttf",
           "/home/pc/.local/share/fonts/win-kr/malgunbd.ttf"):
    font_manager.fontManager.addfont(_f)
rcParams["font.family"] = "Malgun Gothic"
rcParams["axes.unicode_minus"] = False

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
    """인치 좌표계 축 하나를 가진 figure를 만든다. 1 데이터 단위 = 1 inch."""
    fig = plt.figure(figsize=(w_in, h_in), dpi=200)
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
    """둥근 모서리 박스. (x, y)는 좌상단, 크기는 인치."""
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={rounding}",
                       fc=fc, ec=ec, lw=lw, zorder=z, linestyle=ls)
    ax.add_patch(p)
    return p


def label(ax, x, y, s, size=13, color=INK, weight="normal", ha="center",
          va="center", z=6, style="normal", family=None):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                   ha=ha, va=va, zorder=z, style=style, fontfamily=family,
                   linespacing=1.35)


def arrow(ax, p1, p2, color=INK, lw=1.9, ls="-", z=4, style="-|>", ms=13,
          cs=None, shrinkA=3, shrinkB=3):
    """실선/점선 화살표(FancyArrowPatch — 화살촉은 패치라 글리프 걱정 없음)."""
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms,
                        color=color, lw=lw, linestyle=ls, zorder=z,
                        shrinkA=shrinkA, shrinkB=shrinkB, connectionstyle=cs)
    ax.add_patch(a)
    return a


def line(ax, p1, p2, color=AXIS, lw=1.4, ls="-", z=1):
    ax.add_line(Line2D([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw,
                       linestyle=ls, zorder=z))


def diamond(ax, cx, cy, r=0.11, fc=INK, ec=INK, z=5):
    """UML 집합(◆) 표식 — 실제 폴리곤으로 그린다."""
    pts = [(cx, cy - r * 1.3), (cx + r, cy), (cx, cy + r * 1.3), (cx - r, cy)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=1.3, zorder=z))


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
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=1.6, zorder=z))


def checkmark(ax, cx, cy, s=0.12, color=GREEN, lw=2.6, z=7):
    """✓ 글리프는 맑은 고딕에 없다 → 선 두 개로 직접 그린다."""
    ax.add_line(Line2D([cx - s, cx - s * 0.15], [cy + s * 0.05, cy + s * 0.7],
                       color=color, lw=lw, zorder=z,
                       solid_capstyle="round"))
    ax.add_line(Line2D([cx - s * 0.15, cx + s * 1.05], [cy + s * 0.7, cy - s * 0.75],
                       color=color, lw=lw, zorder=z,
                       solid_capstyle="round"))


# ── 시퀀스 다이어그램 도우미 ──
def lifeline(ax, x, name, sub, y_top, y_bot, color=INK, w=1.95, fill=WHITE):
    """세로 생명선: 위쪽 머리 상자 + 아래로 뻗는 점선."""
    rbox(ax, x - w / 2, y_top, w, 0.66, fc=fill, ec=color, lw=1.9,
         rounding=0.08, z=3)
    label(ax, x, y_top + 0.25, name, size=13.5, weight="bold", color=color)
    if sub:
        label(ax, x, y_top + 0.49, sub, size=11, color=MUTED, style="italic")
    ax.add_line(Line2D([x, x], [y_top + 0.66, y_bot], color=AXIS, lw=1.4,
                       linestyle=(0, (4, 4)), zorder=1))


def activation(ax, x, y1, y2, color=INK, w=0.17):
    """활성 막대: 그 생명선이 일하는 구간."""
    ax.add_patch(FancyBboxPatch((x - w / 2, y1), w, y2 - y1,
                 boxstyle="round,pad=0,rounding_size=0.03",
                 fc=WHITE, ec=color, lw=1.5, zorder=2))


def seq_arrow(ax, y, x1, x2, text, color=INK, dashed=False, size=13,
              off=0.15, ms=14):
    """가로 메시지 화살표 + 위쪽 글자. 점선이면 비동기(시그널/반환)."""
    arrow(ax, (x1, y), (x2, y), color=color, lw=1.9,
          ls=((0, (5, 3)) if dashed else "-"), style="-|>", ms=ms, z=5,
          shrinkA=1, shrinkB=1)
    ax.text((x1 + x2) / 2, y - off, text, fontsize=size, color=color,
            ha="center", va="bottom", zorder=6, linespacing=1.3)


def self_msg(ax, x, y, text, color=INK, w=0.95, h=0.5, size=13, side=1):
    """자기 호출 고리(오른쪽으로 갔다 돌아옴) + 글자."""
    ex = x + side * w
    ax.add_line(Line2D([x, ex], [y, y], color=color, lw=1.8, zorder=5))
    ax.add_line(Line2D([ex, ex], [y, y + h], color=color, lw=1.8, zorder=5))
    arrow(ax, (ex, y + h), (x, y + h), color=color, lw=1.8, style="-|>",
          ms=13, z=5, shrinkA=1, shrinkB=1)
    ax.text(ex + side * 0.16 if side > 0 else ex - 0.16, y + h / 2, text,
            fontsize=size, color=color, ha=("left" if side > 0 else "right"),
            va="center", zorder=6, linespacing=1.3)


def note_box(ax, x, y, w, h, text, color=INK2, fill="#fbf7ec", size=11.5,
             ec=None):
    """설명 쪽지."""
    rbox(ax, x, y, w, h, fc=fill, ec=(ec or color), lw=1.3, rounding=0.06, z=4)
    ax.text(x + 0.16, y + h / 2, text, fontsize=size, color=color, ha="left",
            va="center", zorder=6, linespacing=1.32)


def phase_tag(ax, x, y, text, color=INK, size=13):
    """구간(Phase) 딱지."""
    ax.text(x, y, text, fontsize=size, color=color, ha="left", va="center",
            fontweight="bold", zorder=6,
            bbox=dict(boxstyle="round,pad=0.3", fc=WHITE, ec=color, lw=1.4))


def save(fig, out_path):
    fig.savefig(out_path, dpi=200, facecolor=WHITE,
                bbox_inches=None, pad_inches=0)
    plt.close(fig)
