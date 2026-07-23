"""06-sequence-cli.png / 06-sequence-cli-en.png — CLI(명령줄) 실행 시퀀스.

읽은 코드: colorsort/cli.py, colorsort/language.py. 생명선 7개.
UML loop/alt 프레임으로 '사진마다 반복'과 '미리보기 vs --apply' 분기를 표시한다.
언어 결정 우선순위는 코드(resolve_language) 그대로: --lang → 저장값 → 터미널 질문 → 기본값.

실행: python3 gen_06_sequence_cli.py ko | en
글자 +20pt·bold 는 _common.py 가 자동 적용한다. 직접 ax.text 를 쓰는 guard()만
+FB·bold·외곽선을 손으로 적용한다. frame() 딱지 폭은 글자 수가 아니라 em 폭으로
계산한다 — 한글 1자는 영문 1자의 두 배라 len()으로는 한/영이 어긋난다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, rbox, label, line, lifeline, activation,
                     seq_arrow, self_msg, note_box, phase_tag, save,
                     get_lang, suffix, heavy_effect, FB, S,
                     INK, INK2, MUTED, FAINT, GRID, WHITE, BLUE, GREEN,
                     VIOLET, TEAL, AMBER, RED, ACTOR)

LANG = get_lang()
SUF = suffix(LANG)

# ── 영어 번역표 (키 = 한글 원문 그대로, 줄바꿈 포함) ──
# 식별자·명령줄 옵션(run(), --apply, results.csv …)은 번역하지 않는다.
EN = {
    "명령줄(CLI)로 실행하는 순서":
        "Sequence: Running from the Command Line (CLI)",
    "폴더를 훑어 판정하고, 기본은 미리보기(복사 없음)·--apply면 사본 생성.\n"
    "점선 = 반환값, 실선 = 호출.  loop = 사진마다 반복,  alt = 둘 중 하나.":
        "Scan the folder and decide; default is a preview (no copying), "
        "--apply creates copies.\nDashed = return value, solid = call.  "
        "loop = per photo,  alt = one of two.",
    # 생명선
    "사용자": "User", "명령 프롬프트": "command prompt",
    "진입점": "entry point",
    "언어 결정": "language pick",
    "파이프라인": "pipeline",
    "코어": "core",
    "복사 계획·실행": "plan & copy",
    "결과 파일 쓰기": "result files",
    # 구간 딱지 · 프레임
    "1. 언어 정하기": "1. Choose the language",
    "2. 분석 파이프라인  run()": "2. Analysis pipeline  run()",
    "3. 기록 & 화면 출력": "3. Records & screen output",
    "loop  [사진마다]": "loop  [per photo]",
    "alt  [복사 여부]": "alt  [copy or not]",
    "[--apply]  실제 복사": "[--apply]  real copies",
    "[기본]  미리보기 — 복사 없음": "[default]  preview — nothing copied",
    # 식별자뿐인 메시지 — 번역하지 않지만 t()를 거치므로 그대로 등록한다
    "py -3 -m colorsort .\n--output results  [--apply]":
        "py -3 -m colorsort .\n--output results  [--apply]",
    "resolve_language(explicit, reset)": "resolve_language(explicit, reset)",
    "_build_parser(lang) · parse_args()": "_build_parser(lang) · parse_args()",
    "run(input, output, config, apply)": "run(input, output, config, apply)",
    "_input_photos()": "_input_photos()",
    "load_image(path)": "load_image(path)",
    "LoadResult": "LoadResult",
    "measure() → Measurements": "measure() → Measurements",
    "decide() → Decision": "decide() → Decision",
    "crosscheck_file_sizes()": "crosscheck_file_sizes()",
    "results · items · n_excluded": "results · items · n_excluded",
    "find_collisions()": "find_collisions()",
    "write_results_csv() → results.csv\nwrite_run_json() → run.json":
        "write_results_csv() → results.csv\nwrite_run_json() → run.json",
    "write_copy_log() → copy-log.csv": "write_copy_log() → copy-log.csv",
    # 메시지·쪽지
    "언어 우선순위 (코드 그대로):\n"
    "① --lang 지정 → 그 값    ② 저장된 .colorsort-lang → 그 값\n"
    "③ 터미널이면 메뉴로 질문(고르면 저장)    ④ 아니면 기본값(영어)":
        "Language priority (straight from the code):\n"
        "① --lang given → that value    ② saved .colorsort-lang → that value\n"
        "③ if a terminal, ask with a menu (saves the pick)    "
        "④ otherwise the default (English)",
    "lang  (예: 'ko')": "lang  (e.g. 'ko')",
    "입력이 폴더가 아니면 오류로 종료": "not a folder → exit with an error",
    "출력폴더·run.json 마커 폴더 제외": "output folder & run.json markers skipped",
    "읽기 실패해도 measure는 통과\n(그 파일 판정은 ABSTAIN)":
        "measure still runs after a read failure\n"
        "(that file's verdict is ABSTAIN)",
    "plan_copies() → CopyItem 목록": "plan_copies() → list of CopyItem",
    "n_excluded 알림 / results 없으면 종료":
        "report n_excluded / exit if no results",
    "충돌 있으면 오류로 종료(복사 안 함)": "collision → exit, nothing copied",
    "표·이력은 미리보기에서도 항상 기록":
        "table & history written even in preview",
    "execute_copies() → 사본 생성": "execute_copies() → makes copies",
    # messages.py 의 실제 영어 출력("Checked {n} images, copied {copied}.")을 줄임.
    # 중괄호를 살려 n·copied 가 자리표시자임이 드러나게 한다.
    "요약: {n}장 중 {copied}장 복사": "summary: checked {n}, copied {copied}",
    "summarize() → 폴더별 개수 표만 화면에":
        "summarize() → just a per-folder count table",
    "끝: results.csv 위치 안내\n(미리보기·복사 공통)":
        "done: tells you where results.csv is\n(preview and copy alike)",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


def em(s):
    """대략적인 글자 폭(em). 한글·기호 1.0 · 공백 0.3 · 그 밖(영문) 0.5.

    len(s)로 폭을 재면 한글 1자가 영문 1자의 두 배라 한/영이 어긋난다.
    """
    return sum(1.0 if ord(c) > 0x2000 else 0.3 if c == " " else 0.5 for c in s)


W, H = 21.9, 27.4
fig, ax = new_fig(W, H)

# 생명선 7개 (예전 X 값 ×1.27 — 인접 간격 약 3.0 확보)
X = {"user": 1.78, "main": 4.83, "lang": 7.81, "run": 10.80, "core": 13.78,
     "sort": 16.76, "report": 19.88}
YT, YB = 2.10, 27.10
# 사용자 머리 상자는 부제('command prompt')가 길어 조금 넓힌다 (2.3 → 2.75)
lifeline(ax, X["user"], t("사용자"), t("명령 프롬프트"), YT, YB, color=ACTOR,
         w=2.75)
lifeline(ax, X["main"], "cli.main", t("진입점"), YT, YB, color=BLUE)
lifeline(ax, X["lang"], "language", t("언어 결정"), YT, YB, color=AMBER)
lifeline(ax, X["run"], "run", t("파이프라인"), YT, YB, color=BLUE)
# 코어는 부제('load·measure·rules')가 길어 머리 상자만 넓힌다 (2.3 → 3.3)
lifeline(ax, X["core"], t("코어"), "load·measure·rules", YT, YB, color=BLUE,
         w=3.3)
lifeline(ax, X["sort"], "sorting", t("복사 계획·실행"), YT, YB, color=TEAL)
lifeline(ax, X["report"], "report", t("결과 파일 쓰기"), YT, YB, color=VIOLET)

label(ax, W / 2, 0.55, t("명령줄(CLI)로 실행하는 순서"),
      size=25, weight="bold", color=INK)
label(ax, W / 2, 1.45,
      t("폴더를 훑어 판정하고, 기본은 미리보기(복사 없음)·--apply면 사본 생성.\n"
        "점선 = 반환값, 실선 = 호출.  loop = 사진마다 반복,  alt = 둘 중 하나."),
      size=12.5, color=MUTED)


def sec(y, tag, color):
    line(ax, (0.45, y), (W - 0.45, y), color=GRID, lw=1.2, ls=(0, (2, 3)))
    phase_tag(ax, 0.5, y, t(tag), color=color)


def frame(x, y, w, h, tag, color):
    """UML loop/alt 프레임 + 왼쪽 위 딱지. 딱지 폭은 em 폭으로 계산한다."""
    txt = t(tag)
    rbox(ax, x, y, w, h, fc="none", ec=color, lw=1.5, rounding=0.05, z=1)
    # 딱지 폭은 한/영 중 넓은 쪽에 맞춘다 — 두 언어 그림의 도형을 똑같이 유지한다
    tw = 0.30 + max(em(tag), em(EN[tag])) * 0.302 + 0.30
    rbox(ax, x, y, tw, 0.60, fc=WHITE, ec=color, lw=1.4, rounding=0.03, z=3)
    label(ax, x + 0.28, y + 0.30, txt, size=11.5, color=color, ha="left",
          weight="bold", z=4)


def guard(x1, x2, y, text, color):
    """alt 분기 조건. 직접 ax.text 라 +FB·bold·외곽선을 손으로 적용한다."""
    line(ax, (x1, y), (x2, y), color=color, lw=1.3, ls=(0, (5, 4)), z=2)
    ax.text(x1 + 0.35, y, t(text), fontsize=11.5 + FB, color=color, ha="left",
            va="center", zorder=4, fontweight="bold",
            path_effects=heavy_effect(color),
            bbox=dict(boxstyle="round,pad=0.25", fc=WHITE, ec=color,
                      lw=1.2 * S))


def msg(y, x1, x2, text, **kw):
    """seq_arrow 에 번역을 끼운 얇은 껍데기."""
    seq_arrow(ax, y, x1, x2, t(text), **kw)


# 활성 막대
activation(ax, X["main"], 4.05, 26.50, BLUE, w=0.1)
activation(ax, X["run"], 9.15, 16.75, BLUE)

# ── 1. 언어 정하기 ──
sec(3.25, "1. 언어 정하기", AMBER)
msg(4.50, X["user"], X["main"], "py -3 -m colorsort .\n--output results  [--apply]",
    color=INK)
msg(5.18, X["main"], X["lang"], "resolve_language(explicit, reset)", color=AMBER)
note_box(ax, 8.40, 5.28, 12.6, 1.40,
         t("언어 우선순위 (코드 그대로):\n"
           "① --lang 지정 → 그 값    ② 저장된 .colorsort-lang → 그 값\n"
           "③ 터미널이면 메뉴로 질문(고르면 저장)    ④ 아니면 기본값(영어)"),
         color=INK2, fill="#fbf1d8", ec=AMBER, size=11.5)
msg(5.86, X["lang"], X["main"], "lang  (예: 'ko')", color=AMBER, dashed=True)
self_msg(ax, X["main"], 6.80, t("_build_parser(lang) · parse_args()"),
         color=BLUE, w=0.8, h=0.55)
note_box(ax, 6.20, 7.45, 5.4, 0.56, t("입력이 폴더가 아니면 오류로 종료"),
         color=INK2, fill="#eef4fc", ec=BLUE, size=11.5)

# ── 2. 분석 파이프라인 ──
sec(8.40, "2. 분석 파이프라인  run()", BLUE)
msg(9.15, X["main"], X["run"], "run(input, output, config, apply)", color=BLUE)
self_msg(ax, X["run"], 9.65, t("_input_photos()"), color=BLUE, w=0.8, h=0.55)
note_box(ax, 14.20, 10.30, 6.45, 0.56, t("출력폴더·run.json 마커 폴더 제외"),
         color=INK2, fill="#eef4fc", ec=BLUE, size=11.5)

frame(10.05, 11.10, 4.85, 3.55, "loop  [사진마다]", BLUE)
msg(12.30, X["run"], X["core"], "load_image(path)", color=BLUE)
msg(12.96, X["core"], X["run"], "LoadResult", color=BLUE, dashed=True)
msg(13.62, X["run"], X["core"], "measure() → Measurements", color=BLUE)
msg(14.28, X["run"], X["core"], "decide() → Decision", color=BLUE)
note_box(ax, 15.10, 13.10, 5.9, 1.00,
         t("읽기 실패해도 measure는 통과\n(그 파일 판정은 ABSTAIN)"), color=INK2,
         fill="#f4f0ea", ec=FAINT, size=11)

self_msg(ax, X["run"], 14.90, t("crosscheck_file_sizes()"), color=BLUE, w=0.8,
         h=0.55)
msg(16.05, X["run"], X["sort"], "plan_copies() → CopyItem 목록", color=TEAL)
msg(16.71, X["run"], X["main"], "results · items · n_excluded", color=BLUE,
    dashed=True)

# ── 3. 기록 & 출력 ──
sec(17.20, "3. 기록 & 화면 출력", VIOLET)
self_msg(ax, X["main"], 17.75, t("n_excluded 알림 / results 없으면 종료"),
         color=BLUE, w=0.8, h=0.55)
msg(18.90, X["main"], X["sort"], "find_collisions()", color=TEAL)
note_box(ax, 3.90, 19.00, 5.4, 0.56, t("충돌 있으면 오류로 종료(복사 안 함)"),
         color=RED, fill="#f6dcdb", ec=RED, size=11)
msg(20.10, X["main"], X["report"],
    "write_results_csv() → results.csv\nwrite_run_json() → run.json",
    color=VIOLET, off=0.12)
note_box(ax, 13.30, 20.20, 6.0, 0.56, t("표·이력은 미리보기에서도 항상 기록"),
         color=INK2, fill="#f3f0fb", ec=VIOLET, size=11)

frame(1.05, 21.10, 19.8, 4.65, "alt  [복사 여부]", INK)
guard(1.05, 20.85, 22.10, "[--apply]  실제 복사", GREEN)
msg(22.90, X["main"], X["sort"], "execute_copies() → 사본 생성", color=TEAL)
msg(23.56, X["main"], X["report"], "write_copy_log() → copy-log.csv",
    color=VIOLET)
msg(24.22, X["report"], X["user"], "요약: {n}장 중 {copied}장 복사", color=INK,
    dashed=True)
guard(1.05, 20.85, 24.75, "[기본]  미리보기 — 복사 없음", MUTED)
msg(25.55, X["main"], X["report"], "summarize() → 폴더별 개수 표만 화면에",
    color=VIOLET)

msg(26.85, X["main"], X["user"], "끝: results.csv 위치 안내\n(미리보기·복사 공통)",
    color=INK, dashed=True)

out = Path(__file__).resolve().parent.parent / f"06-sequence-cli{SUF}.png"
save(fig, out)
print("saved", out)
