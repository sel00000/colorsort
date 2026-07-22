"""09-data-flow.png — 데이터 흐름도.

읽은 코드: colorsort/loading·measure·rules·sorting·report, colorsortgui/foldering.
가로 흐름: PNG → LoadResult → Measurements → Decision → FileResult → CopyItem → results/.
각 데이터 상자 아래 '이 단계에서 아는 것' 한 줄. 아래에 기록 파일 5종이 어느 단계에서
나오는지 표시. foldering.dest_subfolder 가 라벨→폴더 매핑.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, rbox, label, line, arrow, save,
                     INK, INK2, MUTED, FAINT, AXIS, GRID, WHITE, BLUE, GREEN,
                     VIOLET, AMBER, TEAL, RED, BLUE_FILL, GREEN_FILL,
                     NEUTRAL_FILL)

W, H = 18.8, 9.7
fig, ax = new_fig(W, H)

label(ax, W / 2, 0.42, "데이터 흐름 — 사진 한 장이 결과가 되기까지",
      size=24, weight="bold", color=INK)
label(ax, W / 2, 0.78,
      "왼쪽 원본에서 오른쪽 폴더까지. 화살표 위 글자가 그 일을 하는 함수. "
      "상자 아래 한 줄이 '그 단계에서 아는 것'.", size=12.5, color=MUTED)


def dbox(cx, title, knows, color, fill, cy=2.75, w=2.15, h=1.3):
    rbox(ax, cx - w / 2, cy - h / 2, w, h, fc=fill, ec=color, lw=2.0,
         rounding=0.09, z=3)
    label(ax, cx, cy - 0.2, title, size=13.5, weight="bold", color=color)
    label(ax, cx, cy + 0.28, knows, size=11, color=INK2)
    return {"l": (cx - w / 2, cy), "r": (cx + w / 2, cy), "b": (cx, cy + h / 2),
            "t": (cx, cy - h / 2)}


def fn_arrow(x1, x2, cy, fname):
    arrow(ax, (x1, cy), (x2, cy), color=INK, lw=2.2, style="-|>", ms=16, z=4,
          shrinkA=2, shrinkB=2)
    ax.text((x1 + x2) / 2, cy - 0.42, fname, fontsize=11.5, color=BLUE,
            ha="center", va="center", zorder=6, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#eef4fc", ec=BLUE, lw=1.1))


CX = {"png": 1.5, "lr": 4.15, "ms": 6.8, "dc": 9.45, "fr": 12.1, "ci": 14.75}
png = dbox(CX["png"], "PNG 파일", "원본 사진(안 건드림)", MUTED, NEUTRAL_FILL)
lr = dbox(CX["lr"], "LoadResult", "픽셀 배열 + 파일정보", BLUE, BLUE_FILL)
ms = dbox(CX["ms"], "Measurements", "픽셀 통계(색 비율)", BLUE, BLUE_FILL)
dc = dbox(CX["dc"], "Decision", "판정 + 이유(Msg)", BLUE, BLUE_FILL)
fr = dbox(CX["fr"], "FileResult", "한 장의 전체 결과", BLUE, "#cfe0f5")
ci = dbox(CX["ci"], "CopyItem", "복사 계획(원본→목적지)", TEAL, "#d7ecdc")

# results/ 폴더 나무
rx, ry, rw, rh = 16.15, 1.5, 2.45, 2.55
rbox(ax, rx, ry, rw, rh, fc="#f1f4ef", ec=GREEN, lw=2.0, rounding=0.08, z=3)
label(ax, rx + rw / 2, ry + 0.28, "results/ 폴더", size=13, weight="bold",
      color=GREEN)
tree = ["├ blue/", "├ green/", "└ review/", "     ├ no-signal/", "     ├ mixed/",
        "     └ other/"]
tcol = [BLUE, GREEN, INK2, INK2, VIOLET, INK2]
for i, (t, c) in enumerate(zip(tree, tcol)):
    label(ax, rx + 0.2, ry + 0.66 + i * 0.31, t, size=11, color=c, ha="left")

fn_arrow(png["r"][0], lr["l"][0], 2.75, "load_image()")
fn_arrow(lr["r"][0], ms["l"][0], 2.75, "measure()")
fn_arrow(ms["r"][0], dc["l"][0], 2.75, "decide()")
fn_arrow(dc["r"][0], fr["l"][0], 2.75, "묶기")
fn_arrow(fr["r"][0], ci["l"][0], 2.75, "plan_copies()")
fn_arrow(ci["r"][0], rx, 2.75, "execute_copies()")

# ── 구분선 ──
line(ax, (0.5, 4.65), (W - 0.5, 4.65), color=GRID, lw=1.4, ls=(0, (2, 3)))

# ── 왼쪽: 파이프라인 원칙 ──
rbox(ax, 0.5, 5.0, 8.35, 4.05, fc="#faf9f5", ec=AXIS, lw=1.3, rounding=0.06, z=2)
label(ax, 0.75, 5.35, "이 흐름의 원칙", size=13.5, weight="bold", color=INK,
      ha="left")
bullets = [
    "원본 사진은 절대 수정하지 않는다 — 사본만 폴더로 복사(shutil.copy2).",
    "폴더 이름은 (판정, 이유)로 정해진다 — foldering.dest_subfolder.",
    "언어를 바꿔도 폴더 이름은 그대로(영문 고정) — 결과가 갈라지지 않게.",
    "기본은 미리보기(복사 없음), --apply 일 때만 실제 사본 생성.",
    "GUI(v2)는 이 결과 위에 사람 확정을 겹쳐 파일 두 개를 더 남긴다.",
]
for i, b in enumerate(bullets):
    label(ax, 0.9, 5.85 + i * 0.62, "•", size=13, color=TEAL, ha="left")
    label(ax, 1.2, 5.85 + i * 0.62, b, size=11.5, color=INK2, ha="left")

# ── 오른쪽: 기록 파일 5종 ──
label(ax, 9.3, 5.3, "실행이 남기는 기록 파일 5종  ·  어느 단계에서?",
      size=13.5, weight="bold", color=INK, ha="left")


def rec(x, y, name, desc, trig, color):
    w, h = 4.55, 0.95
    rbox(ax, x, y, w, h, fc=WHITE, ec=color, lw=1.7, rounding=0.06, z=3)
    rbox(ax, x, y, 0.16, h, fc=color, ec=color, lw=1, rounding=0.0, z=4)
    label(ax, x + 0.34, y + 0.32, name, size=13, weight="bold", color=INK,
          ha="left")
    label(ax, x + 0.34, y + 0.68, desc, size=11, color=INK2, ha="left")
    label(ax, x + w - 0.15, y + 0.32, trig, size=11, color=color, ha="right",
          weight="bold")


rec(9.3, 5.65, "results.csv", "모든 판정 한 줄씩 (report)", "항상", BLUE)
rec(9.3, 6.75, "run.json", "실행 설정·이력 (report)", "항상", BLUE)
rec(9.3, 7.85, "copy-log.csv", "만든 사본 목록 (execute_copies)", "--apply 시", GREEN)
rec(14.05, 5.65, "decisions.json", "사람 확정 (지문=열쇠)", "GUI 확정", TEAL)
rec(14.05, 6.75, "moves-log.csv", "사본 이동 기록", "GUI 확정", TEAL)
rbox(ax, 14.05, 7.85, 4.55, 0.95, fc="#f3f0fb", ec=VIOLET, lw=1.4, rounding=0.06,
     z=3)
ax.text(14.28, 8.32,
        "위 3개는 CLI·GUI 공통.\n아래 2개는 GUI에서 [파랑/초록] 누를 때만.",
        fontsize=11, color=VIOLET, ha="left", va="center", zorder=6,
        linespacing=1.3)

# 연결 점선: 판정 단계 → results.csv/run.json,  결과 폴더 → 사본·GUI 기록
arrow(ax, (12.1, 3.4), (11.5, 5.6), color=FAINT, lw=1.5, style="-|>", ms=11,
      ls=(0, (3, 3)), z=2)
arrow(ax, (17.3, 4.05), (16.3, 5.6), color=FAINT, lw=1.5, style="-|>", ms=11,
      ls=(0, (3, 3)), z=2)

out = Path(__file__).resolve().parent.parent / "09-data-flow.png"
save(fig, out)
print("saved", out)
