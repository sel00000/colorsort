"""05-sequence-gui.png / 05-sequence-gui-en.png — GUI에서 사진을 분류하는 시퀀스.

읽은 코드: colorsortgui/qt/mainwindow.py, colorsortgui/project.py,
colorsortgui/qt/detail.py. 세로 생명선 8개, 시간은 위→아래.
비동기 경계(QThread·QThreadPool·시그널)는 점선으로 표시한다.
주의: open_folder는 start() 뒤 worker.wait()로 끝까지 기다린다 → 정렬 동안 UI 블록.

실행: python3 gen_05_sequence_gui.py ko | en
글자 +20pt·bold 는 _common.py 가 자동 적용한다. 생명선을 가로지르는 메시지
라벨만 흰 받침(pad=True)을 깔아 읽히게 한다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, label, line, arrow, lifeline, activation,
                     self_msg, note_box, phase_tag, save, get_lang, suffix, FB,
                     INK, INK2, MUTED, FAINT, GRID, WHITE, BLUE, GREEN,
                     VIOLET, TEAL, AMBER, ACTOR)

LANG = get_lang()
SUF = suffix(LANG)

# ── 영어 번역표 (키 = 한글 원문 그대로, 줄바꿈 포함) ──
# 식별자(open_project(), _set_human, decisions.json …)는 번역하지 않는다.
# GUI 버튼명은 colorsortgui/i18n.py 의 실제 영문 문자열을 쓴다.
EN = {
    "GUI로 사진을 분류하는 순서": "Sequence: Sorting Photos in the GUI",
    "폴더를 고르면 자동 분류 → 썸네일 → 크게 보기 → 사람이 [파랑/초록] 확정 → 되돌리기까지.\n"
    "점선 화살표 = 비동기(시그널·백그라운드), 실선 = 직접 호출.":
        "Pick a folder: auto sort → thumbnails → detail view → human confirms "
        "[Blue/Green] → undo.\nDashed arrow = async (signal/background), "
        "solid = direct call.",
    # 생명선
    "사용자": "User", "(사람)": "(person)",
    "메인 창": "main window",
    "창구 모듈": "gateway module",
    "판정 코어": "verdict core",
    "확정 저장": "confirmations",
    "썸네일 풀": "Thumb pool",
    "크게 보기": "detail view",
    # 구간 딱지
    "A. 자동 분류": "A. Auto sort",
    "B. 화면 채우기": "B. Fill the screen",
    "C. 크게 보기": "C. Detail view",
    "D. 사람이 [파랑/초록] 확정": "D. Human confirms [Blue/Green]",
    "E. 되돌리기": "E. Undo",
    # 식별자뿐인 메시지 — 번역하지 않지만 t()를 거치므로 그대로 등록한다
    "open_project()": "open_project()",
    "apply_copies()": "apply_copies()",
    "set_human(state, item, 'BLUE')": "set_human(state, item, 'BLUE')",
    "store.set() → decisions.json": "store.set() → decisions.json",
    # 메시지
    "폴더 선택·드롭\n→ open_folder()": "Pick / drop a folder\n→ open_folder()",
    "start()  워커 시작": "start()  worker begins",
    "worker.wait(): 분류가 끝날 때까지 기다린다\n— 정렬 동안 UI는 잠시 멈춤(블록)":
        "worker.wait(): waits until sorting finishes\n"
        "— the UI is blocked during the sort",
    "v1_run()  스캔·측정·판정": "v1_run()  scan · measure · decide",
    "출력폴더·run.json 마커 폴더는 스캔 제외":
        "output folder & run.json markers skipped",
    "results  (판정 결과 목록)": "results  (list of verdicts)",
    "장마다 file_fingerprint + store.get()":
        "per photo: file_fingerprint + store.get()",
    "기억된 사람 확정을 겹침": "remembered human confirmations",
    "results.csv · run.json 기록 → execute_copies 로\n"
    "blue/ · green/ · review/ 폴더에 사본을 자동 복사":
        "results.csv · run.json written → execute_copies\n"
        "copies photos into blue/ · green/ · review/",
    "finished_state 시그널": "finished_state signal",
    "비동기 경계 — 시그널이 큐를 거쳐 전달":
        "async boundary — the signal is queued",
    "_populate()  그리드 채움": "_populate()  fills the grid",
    "_ThumbRunner 시작 (QThreadPool)": "_ThumbRunner starts (QThreadPool)",
    "백그라운드 — 둘러보는 동안 계속": "background — while you browse",
    "done 시그널 → _set_thumb()  아이콘": "done signal → _set_thumb()  icon",
    "썸네일 더블클릭\n→ _open_detail()":
        "double-click a thumbnail\n→ _open_detail()",
    "show_item()  자동 보정 뷰": "show_item()  auto-corrected view",
    "[파랑으로] 클릭": "[To Blue] clicked",
    "to_blue 시그널 → _set_human('BLUE')":
        "to_blue signal → _set_human('BLUE')",
    "＋ _move_copy(사본 이동) · _append_move_log(moves-log.csv)\n＋ undo_stack 에 쌓기":
        "＋ _move_copy (move the copy) · _append_move_log(moves-log.csv)\n"
        "＋ push onto undo_stack",
    "[되돌리기] 클릭": "[Undo] clicked",
    "undone 시그널 → _undo() → undo(state)\n(store 복원 · 사본 원위치 · moves-log 기록)":
        "undone signal → _undo() → undo(state)\n"
        "(store restored · copy moved back · moves-log written)",
}


def t(s):
    """ko면 원문, en이면 번역표에서 찾는다. 누락 시 KeyError로 즉시 실패."""
    return s if LANG == "ko" else EN[s]


W, H = 23.4, 25.5
fig, ax = new_fig(W, H)

# 생명선 8개 (예전 X 값 ×1.29 — 인접 간격 2.65~2.90 확보)
X = {"user": 1.87, "main": 4.67, "worker": 7.47, "proj": 10.27,
     "core": 12.96, "store": 15.61, "pool": 18.51, "detail": 21.35}
YT, YB = 2.10, 25.05
lifeline(ax, X["user"], t("사용자"), t("(사람)"), YT, YB, color=ACTOR)
lifeline(ax, X["main"], "MainWindow", t("메인 창"), YT, YB, color=VIOLET)
lifeline(ax, X["worker"], "SortWorker", "QThread", YT, YB, color=VIOLET)
# project 머리는 영어 부제('gateway module')가 길어 조금 넓힌다 (2.3 → 2.6)
lifeline(ax, X["proj"], "project", t("창구 모듈"), YT, YB, color=TEAL, w=2.6)
lifeline(ax, X["core"], "colorsort", t("판정 코어"), YT, YB, color=BLUE)
lifeline(ax, X["store"], "DecisionStore", t("확정 저장"), YT, YB, color=TEAL)
lifeline(ax, X["pool"], t("썸네일 풀"), "QThreadPool", YT, YB, color=VIOLET)
lifeline(ax, X["detail"], "DetailPage", t("크게 보기"), YT, YB, color=VIOLET)

# 제목
label(ax, W / 2, 0.55, t("GUI로 사진을 분류하는 순서"),
      size=25, weight="bold", color=INK)
label(ax, W / 2, 1.45,
      t("폴더를 고르면 자동 분류 → 썸네일 → 크게 보기 → 사람이 [파랑/초록] 확정 → 되돌리기까지.\n"
        "점선 화살표 = 비동기(시그널·백그라운드), 실선 = 직접 호출."),
      size=12.5, color=MUTED)


def sep(y, tag, color):
    line(ax, (0.45, y), (W - 0.45, y), color=GRID, lw=1.2, ls=(0, (2, 3)))
    phase_tag(ax, 0.5, y, t(tag), color=color)


def msg(y, x1, x2, text, color=INK, dashed=False, size=13, off=0.15, ms=14,
        pad=False):
    """가로 메시지 화살표 + 위쪽 글자.

    _common.seq_arrow 와 같지만, 라벨이 생명선을 가로지를 때 흰 받침을 깔 수
    있다(pad=True). 받침이 없으면 점선 생명선이 글자를 뚫고 지나가 읽기 어렵다.
    """
    arrow(ax, (x1, y), (x2, y), color=color, lw=1.9,
          ls=((0, (5, 3)) if dashed else "-"), style="-|>", ms=ms, z=5,
          shrinkA=1, shrinkB=1)
    kw = {"bbox": dict(boxstyle="round,pad=0.15", fc=WHITE, ec="none",
                       alpha=0.85)} if pad else {}
    ax.text((x1 + x2) / 2, y - off, t(text), fontsize=size + FB, color=color,
            ha="center", va="bottom", zorder=6, linespacing=1.3,
            fontweight="bold", **kw)


# 활성 막대(누가 일하는가)
activation(ax, X["worker"], 5.46, 11.85, VIOLET)     # 백그라운드 스레드
activation(ax, X["proj"], 7.25, 10.50, TEAL)         # open_project 내부
activation(ax, X["main"], 4.85, 11.85, VIOLET, w=0.1)  # wait로 블록

# ── Phase A: 폴더를 고르면 자동 분류 ──
sep(3.50, "A. 자동 분류", BLUE)
msg(4.75, X["user"], X["main"], "폴더 선택·드롭\n→ open_folder()", color=INK)
msg(5.46, X["main"], X["worker"], "start()  워커 시작", color=VIOLET)
note_box(ax, 5.00, 5.56, 7.4, 1.00,
         t("worker.wait(): 분류가 끝날 때까지 기다린다\n— 정렬 동안 UI는 잠시 멈춤(블록)"),
         color=AMBER, fill="#fbf1d8", ec=AMBER)
msg(7.25, X["worker"], X["proj"], "open_project()", color=TEAL)
msg(7.97, X["proj"], X["core"], "v1_run()  스캔·측정·판정", color=BLUE)
note_box(ax, 14.20, 8.15, 6.6, 0.66, t("출력폴더·run.json 마커 폴더는 스캔 제외"),
         color=INK2, fill="#eef4fc", ec=BLUE)
msg(8.69, X["core"], X["proj"], "results  (판정 결과 목록)", color=BLUE,
    dashed=True)
msg(9.41, X["proj"], X["store"], "장마다 file_fingerprint + store.get()",
    color=TEAL, pad=True)
note_box(ax, 16.30, 9.55, 5.35, 0.66, t("기억된 사람 확정을 겹침"), color=INK2,
         fill="#ecf7f0", ec=TEAL)
msg(10.13, X["worker"], X["proj"], "apply_copies()", color=TEAL)
note_box(ax, 8.50, 10.23, 7.4, 1.00,
         t("results.csv · run.json 기록 → execute_copies 로\n"
           "blue/ · green/ · review/ 폴더에 사본을 자동 복사"),
         color=INK2, fill="#f4f0ea", ec=FAINT)
msg(11.85, X["worker"], X["main"], "finished_state 시그널", color=VIOLET,
    dashed=True)
note_box(ax, 3.90, 11.95, 6.05, 0.66, t("비동기 경계 — 시그널이 큐를 거쳐 전달"),
         color=VIOLET, fill="#f3f0fb", ec=VIOLET)

# ── Phase B: 그리드 + 썸네일 ──
sep(13.05, "B. 화면 채우기", VIOLET)
self_msg(ax, X["main"], 13.60, t("_populate()  그리드 채움"), color=VIOLET,
         w=0.85, h=0.55)
msg(14.87, X["main"], X["pool"], "_ThumbRunner 시작 (QThreadPool)",
    color=VIOLET, dashed=True, pad=True)
note_box(ax, 18.15, 15.03, 5.0, 0.66, t("백그라운드 — 둘러보는 동안 계속"),
         color=VIOLET, fill="#f3f0fb", ec=VIOLET)
msg(15.59, X["pool"], X["main"], "done 시그널 → _set_thumb()  아이콘",
    color=VIOLET, dashed=True, pad=True)

# ── Phase C: 크게 보기 ──
sep(16.00, "C. 크게 보기", VIOLET)
msg(17.30, X["user"], X["main"], "썸네일 더블클릭\n→ _open_detail()", color=INK)
msg(18.02, X["main"], X["detail"], "show_item()  자동 보정 뷰", color=VIOLET,
    pad=True)

# ── Phase D: 사람이 확정 ──
sep(18.47, "D. 사람이 [파랑/초록] 확정", GREEN)
msg(19.19, X["user"], X["detail"], "[파랑으로] 클릭", color=INK, pad=True)
msg(19.91, X["detail"], X["main"], "to_blue 시그널 → _set_human('BLUE')",
    color=VIOLET, dashed=True, pad=True)
msg(20.63, X["main"], X["proj"], "set_human(state, item, 'BLUE')", color=TEAL,
    pad=True)
msg(21.35, X["proj"], X["store"], "store.set() → decisions.json", color=TEAL,
    pad=True)
note_box(ax, 7.80, 21.45, 10.15, 1.00,
         t("＋ _move_copy(사본 이동) · _append_move_log(moves-log.csv)\n"
           "＋ undo_stack 에 쌓기"),
         color=INK2, fill="#ecf7f0", ec=TEAL)

# ── Phase E: 되돌리기(짧게) ──
sep(22.90, "E. 되돌리기", AMBER)
msg(23.62, X["user"], X["detail"], "[되돌리기] 클릭", color=INK, pad=True)
msg(24.76, X["detail"], X["main"],
    "undone 시그널 → _undo() → undo(state)\n(store 복원 · 사본 원위치 · moves-log 기록)",
    color=VIOLET, dashed=True, pad=True)

out = Path(__file__).resolve().parent.parent / f"05-sequence-gui{SUF}.png"
save(fig, out)
print("saved", out)
