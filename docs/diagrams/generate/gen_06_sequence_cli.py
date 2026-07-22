"""06-sequence-cli.png — CLI(명령줄) 실행 시퀀스.

읽은 코드: colorsort/cli.py, colorsort/language.py. 생명선 7개.
UML loop/alt 프레임으로 '사진마다 반복'과 '미리보기 vs --apply' 분기를 표시한다.
언어 결정 우선순위는 코드(resolve_language) 그대로: --lang → 저장값 → 터미널 질문 → 기본값.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, rbox, label, line, lifeline, activation,
                     seq_arrow, self_msg, note_box, phase_tag, save,
                     INK, INK2, MUTED, FAINT, AXIS, GRID, WHITE, BLUE, GREEN,
                     VIOLET, TEAL, AMBER, RED, ACTOR)

W, H = 17.2, 21.0
fig, ax = new_fig(W, H)

X = {"user": 1.4, "main": 3.8, "lang": 6.15, "run": 8.5, "core": 10.85,
     "sort": 13.2, "report": 15.65}
YT, YB = 1.25, 20.5
lifeline(ax, X["user"], "사용자", "명령 프롬프트", YT, YB, color=ACTOR)
lifeline(ax, X["main"], "cli.main", "진입점", YT, YB, color=BLUE)
lifeline(ax, X["lang"], "language", "언어 결정", YT, YB, color=AMBER)
lifeline(ax, X["run"], "run", "파이프라인", YT, YB, color=BLUE)
lifeline(ax, X["core"], "코어", "load·measure·rules", YT, YB, color=BLUE)
lifeline(ax, X["sort"], "sorting", "복사 계획·실행", YT, YB, color=TEAL)
lifeline(ax, X["report"], "report", "결과 파일 쓰기", YT, YB, color=VIOLET)

label(ax, W / 2, 0.4, "명령줄(CLI)로 실행하는 순서",
      size=25, weight="bold", color=INK)
label(ax, W / 2, 0.78,
      "폴더를 훑어 판정하고, 기본은 미리보기(복사 없음)·--apply면 사본 생성. "
      "점선 = 반환값, 실선 = 호출.  loop = 사진마다 반복,  alt = 둘 중 하나.",
      size=12.5, color=MUTED)


def sec(y, tag, color):
    line(ax, (0.45, y), (W - 0.45, y), color=GRID, lw=1.2, ls=(0, (2, 3)))
    phase_tag(ax, 0.5, y, tag, color=color)


def frame(x, y, w, h, tag, color):
    rbox(ax, x, y, w, h, fc="none", ec=color, lw=1.5, rounding=0.05, z=1)
    tw = 0.45 + 0.17 * len(tag)
    rbox(ax, x, y, tw, 0.42, fc=WHITE, ec=color, lw=1.4, rounding=0.03, z=3)
    label(ax, x + 0.18, y + 0.21, tag, size=11.5, color=color, ha="left",
          weight="bold", z=4)


def guard(x1, x2, y, text, color):
    line(ax, (x1, y), (x2, y), color=color, lw=1.3, ls=(0, (5, 4)), z=2)
    ax.text(x1 + 0.35, y, text, fontsize=11.5, color=color, ha="left",
            va="center", zorder=4, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc=WHITE, ec=color, lw=1.2))


# 활성 막대
activation(ax, X["main"], 2.9, 20.15, BLUE, w=0.1)
activation(ax, X["run"], 7.65, 12.75, BLUE)

# ── 1. 언어 정하기 ──
sec(2.4, "1. 언어 정하기", AMBER)
seq_arrow(ax, 2.98, X["user"], X["main"],
          "py -3 -m colorsort .\n--output results  [--apply]", color=INK)
seq_arrow(ax, 3.8, X["main"], X["lang"], "resolve_language(explicit, reset)",
          color=AMBER)
note_box(ax, 6.55, 4.0, 9.9, 1.0,
         "언어 우선순위 (코드 그대로):\n① --lang 지정 → 그 값    ② 저장된 .colorsort-lang → 그 값\n"
         "③ 터미널이면 메뉴로 질문(고르면 저장)    ④ 아니면 기본값(영어)",
         color=INK2, fill="#fbf1d8", ec=AMBER, size=11.5)
seq_arrow(ax, 5.45, X["lang"], X["main"], "lang  (예: 'ko')", color=AMBER,
          dashed=True)
self_msg(ax, X["main"], 5.95, "_build_parser(lang) · parse_args()", color=BLUE,
         w=0.8, h=0.42)
note_box(ax, 4.9, 6.45, 5.6, 0.46, "입력이 폴더가 아니면 오류로 종료",
         color=INK2, fill="#eef4fc", ec=BLUE, size=11.5)

# ── 2. 분석 파이프라인 ──
sec(7.1, "2. 분석 파이프라인  run()", BLUE)
seq_arrow(ax, 7.6, X["main"], X["run"], "run(input, output, config, apply)",
          color=BLUE)
self_msg(ax, X["run"], 8.1, "_input_photos()", color=BLUE, w=0.8, h=0.42)
note_box(ax, 11.2, 8.2, 5.25, 0.46,
         "출력폴더·run.json 마커 폴더 제외", color=INK2, fill="#eef4fc", ec=BLUE,
         size=11.5)

frame(8.05, 8.85, 3.55, 2.95, "loop  [사진마다]", BLUE)
seq_arrow(ax, 9.65, X["run"], X["core"], "load_image(path)", color=BLUE)
seq_arrow(ax, 10.15, X["core"], X["run"], "LoadResult", color=BLUE, dashed=True)
seq_arrow(ax, 10.65, X["run"], X["core"], "measure() → Measurements", color=BLUE)
seq_arrow(ax, 11.2, X["run"], X["core"], "decide() → Decision", color=BLUE)
note_box(ax, 11.95, 10.35, 4.5, 0.62,
         "읽기 실패해도 measure는 통과\n(그 파일 판정은 ABSTAIN)", color=INK2,
         fill="#f4f0ea", ec=FAINT, size=11)

self_msg(ax, X["run"], 12.15, "crosscheck_file_sizes()", color=BLUE, w=0.8,
         h=0.42)
seq_arrow(ax, 12.95, X["run"], X["sort"], "plan_copies() → CopyItem 목록",
          color=TEAL)
seq_arrow(ax, 13.5, X["run"], X["main"], "results · items · n_excluded",
          color=BLUE, dashed=True)

# ── 3. 기록 & 출력 ──
sec(14.0, "3. 기록 & 화면 출력", VIOLET)
self_msg(ax, X["main"], 14.5, "n_excluded 알림 / results 없으면 종료", color=BLUE,
         w=0.8, h=0.42)
seq_arrow(ax, 15.3, X["main"], X["sort"], "find_collisions()", color=TEAL)
note_box(ax, 3.1, 15.43, 4.3, 0.46, "충돌 있으면 오류로 종료(복사 안 함)",
         color=RED, fill="#f6dcdb", ec=RED, size=11)
seq_arrow(ax, 15.95, X["main"], X["report"],
          "write_results_csv() → results.csv\nwrite_run_json() → run.json",
          color=VIOLET, off=0.12)
note_box(ax, 10.95, 16.12, 5.5, 0.42, "표·이력은 미리보기에서도 항상 기록",
         color=INK2, fill="#f3f0fb", ec=VIOLET, size=11)

frame(1.05, 16.6, 15.5, 3.05, "alt  [복사 여부]", INK)
guard(1.05, 16.55, 17.15, "[--apply]  실제 복사", GREEN)
seq_arrow(ax, 17.6, X["main"], X["sort"], "execute_copies() → 사본 생성",
          color=TEAL)
seq_arrow(ax, 18.05, X["main"], X["report"], "write_copy_log() → copy-log.csv",
          color=VIOLET)
seq_arrow(ax, 18.5, X["report"], X["user"], "요약: n장 중 copied장 복사",
          color=INK, dashed=True)
guard(1.05, 16.55, 18.85, "[기본]  미리보기 — 복사 없음", MUTED)
seq_arrow(ax, 19.35, X["main"], X["report"],
          "summarize() → 폴더별 개수 표만 화면에", color=VIOLET)

seq_arrow(ax, 20.15, X["main"], X["user"],
          "끝: results.csv 위치 안내 (미리보기·복사 공통)", color=INK, dashed=True)

out = Path(__file__).resolve().parent.parent / "06-sequence-cli.png"
save(fig, out)
print("saved", out)
