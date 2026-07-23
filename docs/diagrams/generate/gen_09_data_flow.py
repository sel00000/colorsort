"""09-data-flow.png / 09-data-flow-en.png — 데이터 흐름도.

읽은 코드: colorsort/loading·measure·rules·sorting·report, colorsortgui/foldering.
가로 흐름: PNG → LoadResult → Measurements → Decision → FileResult → CopyItem → results/.
각 데이터 상자 아래 '이 단계에서 아는 것' 한 줄. 아래에 기록 파일 5종이 어느 단계에서
나오는지 표시. foldering.dest_subfolder 가 라벨→폴더 매핑.

실행: python3 gen_09_data_flow.py ko | en   (en 이면 파일명에 -en 이 붙는다)
글자 +20pt·bold 는 _common.py 가 자동 적용한다. 직접 ax.text 를 쓰는 두 곳
(fn_arrow 딱지·보라 쪽지)만 +FB·bold 를 손으로 적용한다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, rbox, label, line, arrow, save, get_lang, suffix,
                     heavy_effect, FB, S,
                     INK, INK2, MUTED, FAINT, AXIS, GRID, WHITE, BLUE, GREEN,
                     VIOLET, TEAL, BLUE_FILL, NEUTRAL_FILL)

LANG = get_lang()
SUF = suffix(LANG)

# ── 영어 번역표 (키 = 한글 원문 그대로, 줄바꿈 포함) ──
# 식별자·폴더명(load_image(), results/, blue/ …)은 번역하지 않는다.
EN = {
    "데이터 흐름 — 사진 한 장이 결과가 되기까지":
        "Data Flow — How One Photo Becomes a Result",
    "왼쪽 원본에서 오른쪽 폴더까지. 화살표 위 글자가 그 일을 하는 함수. "
    "상자 아래 한 줄이 '그 단계에서 아는 것'.":
        "Left to right: original photo → sorted folders. The label above each "
        "arrow is the function doing the work;\nthe line inside each box is "
        "what is known at that stage.",
    # 파이프라인 상자
    "PNG 파일": "PNG file",
    "원본 사진\n(안 건드림)": "Original photo\n(untouched)",
    "픽셀 배열 +\n파일 정보": "Pixel array +\nfile info",
    "픽셀 통계\n(색 비율)": "Pixel stats\n(color ratios)",
    "판정 + 이유\n(Msg)": "Verdict + why\n(Msg)",
    "한 장의\n전체 결과": "Full result for\none photo",
    "복사 계획\n(원본→목적지)": "Copy plan\n(source→dest)",
    "results/ 폴더": "results/ folder",
    "묶기": "bundle",
    # 왼쪽 원칙
    "이 흐름의 원칙": "Principles of this flow",
    "원본 사진은 절대 수정하지 않는다 —\n사본만 폴더로 복사(shutil.copy2).":
        "Originals are never modified — only\ncopies are placed in folders "
        "(shutil.copy2).",
    "폴더 이름은 (판정, 이유)로 정해진다 —\nfoldering.dest_subfolder.":
        "Folder names come from (verdict, reason) —\nfoldering.dest_subfolder.",
    "언어를 바꿔도 폴더 이름은\n그대로(영문 고정) — 결과가 갈라지지 않게.":
        "Folder names stay English even if the UI\nlanguage changes, so results "
        "never diverge.",
    "기본은 미리보기(복사 없음),\n--apply 일 때만 실제 사본 생성.":
        "Preview by default (nothing is copied);\nreal copies only with --apply.",
    "GUI(v2)는 이 결과 위에 사람 확정을 겹쳐\n파일 두 개를 더 남긴다.":
        "The GUI (v2) layers human confirmation on\ntop and leaves two more "
        "files.",
    # 오른쪽 기록 파일
    "실행이 남기는 기록 파일 5종  ·  어느 단계에서?":
        "5 record files a run leaves behind  ·  from which stage?",
    "모든 판정 한 줄씩 (report)": "every verdict, one row (report)",
    "실행 설정·이력 (report)": "run settings & history (report)",
    "만든 사본 목록 (execute_copies)": "copies created (execute_copies)",
    "사람 확정 (지문=열쇠)": "human confirmation (hash=key)",
    "사본 이동 기록": "where copies were moved",
    "항상": "always",
    "--apply 시": "with --apply",
    "GUI 확정": "GUI confirm",
    "위 3개는 CLI·GUI 공통.\n아래 2개는 GUI에서\n[파랑/초록] 누를 때만.":
        "Top 3: CLI and GUI alike.\nBottom 2: only on [Blue/Green]\nin the GUI.",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


W, H = 23.4, 13.0
fig, ax = new_fig(W, H)

# ── 제목 ──
label(ax, W / 2, 0.75, t("데이터 흐름 — 사진 한 장이 결과가 되기까지"),
      size=24, weight="bold", color=INK)
label(ax, W / 2, 1.45 if LANG == "ko" else 1.40,
      t("왼쪽 원본에서 오른쪽 폴더까지. 화살표 위 글자가 그 일을 하는 함수. "
        "상자 아래 한 줄이 '그 단계에서 아는 것'."), size=12.5, color=MUTED)

# ── 파이프라인 상자 ──
CY, BW, BH = 3.50, 2.70, 1.90


def dbox(cx, title, knows, color, fill):
    rbox(ax, cx - BW / 2, CY - BH / 2, BW, BH, fc=fill, ec=color, lw=2.0,
         rounding=0.09, z=3)
    label(ax, cx, CY - 0.45, title, size=13.5, weight="bold", color=color)
    label(ax, cx, CY + 0.42, knows, size=11, color=INK2)


def fn_arrow(x1, x2, fname, below=False):
    """화살표 + 함수명 딱지. 딱지는 직접 ax.text 라 +FB·bold·외곽선을 손으로 적용."""
    arrow(ax, (x1, CY), (x2, CY), color=INK, lw=2.2, style="-|>", ms=16, z=4,
          shrinkA=2, shrinkB=2)
    fy = 5.90 if below else 2.20
    ax.text((x1 + x2) / 2, fy, fname, fontsize=11.5 + FB,
            color=BLUE, ha="center", va="center", zorder=6, fontweight="bold",
            path_effects=heavy_effect(BLUE),
            bbox=dict(boxstyle="round,pad=0.22", fc="#eef4fc", ec=BLUE,
                      lw=1.1 * S))


CX = [1.75, 4.90, 8.05, 11.20, 14.35, 17.50]
dbox(CX[0], t("PNG 파일"), t("원본 사진\n(안 건드림)"), MUTED, NEUTRAL_FILL)
dbox(CX[1], "LoadResult", t("픽셀 배열 +\n파일 정보"), BLUE, BLUE_FILL)
dbox(CX[2], "Measurements", t("픽셀 통계\n(색 비율)"), BLUE, BLUE_FILL)
dbox(CX[3], "Decision", t("판정 + 이유\n(Msg)"), BLUE, BLUE_FILL)
dbox(CX[4], "FileResult", t("한 장의\n전체 결과"), BLUE, "#cfe0f5")
dbox(CX[5], "CopyItem", t("복사 계획\n(원본→목적지)"), TEAL, "#d7ecdc")

# results/ 폴더 나무 — 폴더 이름은 설계상 영문 고정이라 번역하지 않는다
rx, ry, rw, rh = 19.30, 2.05, 3.40, 3.55
rbox(ax, rx, ry, rw, rh, fc="#f1f4ef", ec=GREEN, lw=2.0, rounding=0.08, z=3)
label(ax, rx + rw / 2, ry + 0.55, t("results/ 폴더"), size=13, weight="bold",
      color=GREEN)
tree = ["├ blue/", "├ green/", "└ review/", "     ├ no-signal/",
        "     ├ mixed/", "     └ other/"]
tcol = [BLUE, GREEN, INK2, INK2, VIOLET, INK2]
for i, (tr, c) in enumerate(zip(tree, tcol)):
    label(ax, rx + 0.24, ry + 1.15 + i * 0.40, tr, size=11, color=c, ha="left")

for i, fname in enumerate(["load_image()", "measure()", "decide()", t("묶기"),
                           "plan_copies()"]):
    fn_arrow(CX[i] + BW / 2, CX[i + 1] - BW / 2, fname)
fn_arrow(CX[5] + BW / 2, rx, "execute_copies()", below=True)

# ── 구분선 ──
line(ax, (0.4, 6.25), (W - 0.4, 6.25), color=GRID, lw=1.4, ls=(0, (2, 3)))

# ── 왼쪽: 파이프라인 원칙 ──
rbox(ax, 0.40, 6.55, 10.90, 6.10, fc="#faf9f5", ec=AXIS, lw=1.3, rounding=0.06,
     z=2)
label(ax, 0.78, 7.05, t("이 흐름의 원칙"), size=13.5, weight="bold", color=INK,
      ha="left")
bullets = [
    "원본 사진은 절대 수정하지 않는다 —\n사본만 폴더로 복사(shutil.copy2).",
    "폴더 이름은 (판정, 이유)로 정해진다 —\nfoldering.dest_subfolder.",
    "언어를 바꿔도 폴더 이름은\n그대로(영문 고정) — 결과가 갈라지지 않게.",
    "기본은 미리보기(복사 없음),\n--apply 일 때만 실제 사본 생성.",
    "GUI(v2)는 이 결과 위에 사람 확정을 겹쳐\n파일 두 개를 더 남긴다.",
]
for i, b in enumerate(bullets):
    y = 7.75 + i * 1.00
    label(ax, 1.00, y, "•", size=13, color=TEAL, ha="left", va="top")
    label(ax, 1.42, y, t(b), size=11.5, color=INK2, ha="left", va="top")

# ── 오른쪽: 기록 파일 5종 ──
label(ax, 11.75, 7.05, t("실행이 남기는 기록 파일 5종  ·  어느 단계에서?"),
      size=13.5, weight="bold", color=INK, ha="left")


def rec(x, y, name, desc, trig, color):
    w, h = 5.30, 1.50
    rbox(ax, x, y, w, h, fc=WHITE, ec=color, lw=1.7, rounding=0.06, z=3)
    rbox(ax, x, y, 0.19, h, fc=color, ec=color, lw=1, rounding=0.0, z=4)
    label(ax, x + 0.42, y + 0.50, name, size=13, weight="bold", color=INK,
          ha="left")
    label(ax, x + 0.42, y + 1.05, t(desc), size=11, color=INK2, ha="left")
    label(ax, x + w - 0.18, y + 0.50, t(trig), size=11, color=color, ha="right",
          weight="bold")


rec(11.75, 7.75, "results.csv", "모든 판정 한 줄씩 (report)", "항상", BLUE)
rec(11.75, 9.40, "run.json", "실행 설정·이력 (report)", "항상", BLUE)
rec(11.75, 11.05, "copy-log.csv", "만든 사본 목록 (execute_copies)",
    "--apply 시", GREEN)
rec(17.25, 7.75, "decisions.json", "사람 확정 (지문=열쇠)", "GUI 확정", TEAL)
rec(17.25, 9.40, "moves-log.csv", "사본 이동 기록", "GUI 확정", TEAL)
rbox(ax, 17.25, 11.05, 5.30, 1.50, fc="#f3f0fb", ec=VIOLET, lw=1.4,
     rounding=0.06, z=3)
ax.text(17.52, 11.80,
        t("위 3개는 CLI·GUI 공통.\n아래 2개는 GUI에서\n[파랑/초록] 누를 때만."),
        fontsize=11 + FB, color=VIOLET, ha="left", va="center", zorder=6,
        linespacing=1.32, fontweight="bold")

# 연결 점선: 판정 단계 → results.csv/run.json,  결과 폴더 → 사본·GUI 기록
arrow(ax, (14.35, CY + BH / 2), (13.5, 7.62), color=FAINT, lw=1.5, style="-|>",
      ms=11, ls=(0, (3, 3)), z=2)
arrow(ax, (21.0, ry + rh), (19.9, 7.62), color=FAINT, lw=1.5, style="-|>",
      ms=11, ls=(0, (3, 3)), z=2)

out = Path(__file__).resolve().parent.parent / f"09-data-flow{SUF}.png"
save(fig, out)
print("saved", out)
