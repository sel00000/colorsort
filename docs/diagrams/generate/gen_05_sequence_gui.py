"""05-sequence-gui.png — GUI에서 사진을 분류하는 시퀀스.

읽은 코드: colorsortgui/qt/mainwindow.py, colorsortgui/project.py,
colorsortgui/qt/detail.py. 세로 생명선 8개, 시간은 위→아래.
비동기 경계(QThread·QThreadPool·시그널)는 점선으로 표시한다.
주의: open_folder는 start() 뒤 worker.wait()로 끝까지 기다린다 → 정렬 동안 UI 블록.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (new_fig, rbox, label, line, lifeline, activation,
                     seq_arrow, self_msg, note_box, phase_tag, save,
                     INK, INK2, MUTED, FAINT, AXIS, GRID, WHITE, BLUE, GREEN,
                     VIOLET, TEAL, AMBER, ACTOR)

W, H = 18.4, 19.4
fig, ax = new_fig(W, H)

# 생명선 8개
X = {"user": 1.45, "main": 3.62, "worker": 5.79, "proj": 7.96,
     "core": 10.05, "store": 12.1, "pool": 14.35, "detail": 16.55}
YT, YB = 1.25, 18.9
lifeline(ax, X["user"], "사용자", "(사람)", YT, YB, color=ACTOR)
lifeline(ax, X["main"], "MainWindow", "메인 창", YT, YB, color=VIOLET)
lifeline(ax, X["worker"], "SortWorker", "QThread", YT, YB, color=VIOLET)
lifeline(ax, X["proj"], "project", "창구 모듈", YT, YB, color=TEAL)
lifeline(ax, X["core"], "colorsort", "판정 코어", YT, YB, color=BLUE)
lifeline(ax, X["store"], "DecisionStore", "확정 저장", YT, YB, color=TEAL)
lifeline(ax, X["pool"], "썸네일 풀", "QThreadPool", YT, YB, color=VIOLET)
lifeline(ax, X["detail"], "DetailPage", "크게 보기", YT, YB, color=VIOLET)

# 제목
label(ax, W / 2, 0.4, "GUI로 사진을 분류하는 순서",
      size=25, weight="bold", color=INK)
label(ax, W / 2, 0.78,
      "폴더를 고르면 자동 분류 → 썸네일 → 크게 보기 → 사람이 [파랑/초록] 확정 → 되돌리기까지. "
      "점선 화살표 = 비동기(시그널·백그라운드), 실선 = 직접 호출.",
      size=12.5, color=MUTED)


def sep(y, tag, color):
    line(ax, (0.45, y), (W - 0.45, y), color=GRID, lw=1.2, ls=(0, (2, 3)))
    phase_tag(ax, 0.5, y, tag, color=color)


# 활성 막대(누가 일하는가)
activation(ax, X["worker"], 3.6, 8.98, VIOLET)    # 백그라운드 스레드
activation(ax, X["proj"], 5.05, 8.05, TEAL)       # open_project 내부
activation(ax, X["main"], 3.05, 8.98, VIOLET, w=0.1)  # wait로 블록

# ── Phase A: 폴더를 고르면 자동 분류 ──
sep(2.4, "A. 자동 분류", BLUE)
seq_arrow(ax, 2.95, X["user"], X["main"], "폴더 선택·드롭\n→ open_folder()", color=INK)
seq_arrow(ax, 3.6, X["main"], X["worker"], "start()  워커 시작", color=VIOLET)
note_box(ax, 4.15, 3.8, 5.1, 0.62,
         "worker.wait(): 분류가 끝날 때까지 기다린다\n— 정렬 동안 UI는 잠시 멈춤(블록)",
         color=AMBER, fill="#fbf1d8", ec=AMBER)
seq_arrow(ax, 5.05, X["worker"], X["proj"], "open_project()", color=TEAL)
seq_arrow(ax, 5.6, X["proj"], X["core"], "v1_run()  스캔·측정·판정", color=BLUE)
note_box(ax, 10.2, 5.76, 4.35, 0.5,
         "출력폴더·run.json 마커 폴더는 스캔 제외", color=INK2, fill="#eef4fc",
         ec=BLUE)
seq_arrow(ax, 6.42, X["core"], X["proj"], "results  (판정 결과 목록)", color=BLUE,
          dashed=True)
seq_arrow(ax, 6.97, X["proj"], X["store"], "장마다 file_fingerprint + store.get()",
          color=TEAL)
note_box(ax, 12.68, 6.62, 3.95, 0.5, "기억된 사람 확정을 겹침", color=INK2,
         fill="#ecf7f0", ec=TEAL)
seq_arrow(ax, 7.6, X["worker"], X["proj"], "apply_copies()", color=TEAL)
note_box(ax, 7.9, 8.08, 8.5, 0.6,
         "results.csv · run.json 기록 → execute_copies 로\nblue/ · green/ · review/ 폴더에 사본을 자동 복사",
         color=INK2, fill="#f4f0ea", ec=FAINT)
seq_arrow(ax, 8.98, X["worker"], X["main"], "finished_state 시그널", color=VIOLET,
          dashed=True)
note_box(ax, 3.05, 9.08, 4.6, 0.5, "비동기 경계 — 시그널이 큐를 거쳐 전달",
         color=VIOLET, fill="#f3f0fb", ec=VIOLET)

# ── Phase B: 그리드 + 썸네일 ──
sep(9.9, "B. 화면 채우기", VIOLET)
self_msg(ax, X["main"], 10.25, "_populate()  그리드 채움", color=VIOLET, w=0.85,
         h=0.42)
seq_arrow(ax, 11.15, X["main"], X["pool"], "_ThumbRunner 시작 (QThreadPool)",
          color=VIOLET, dashed=True)
note_box(ax, 14.35, 11.28, 3.85, 0.5, "백그라운드 — 둘러보는 동안 계속",
         color=VIOLET, fill="#f3f0fb", ec=VIOLET)
seq_arrow(ax, 11.9, X["pool"], X["main"], "done 시그널 → _set_thumb()  아이콘",
          color=VIOLET, dashed=True)

# ── Phase C: 크게 보기 ──
sep(12.5, "C. 크게 보기", VIOLET)
seq_arrow(ax, 13.05, X["user"], X["main"], "썸네일 더블클릭\n→ _open_detail()",
          color=INK)
seq_arrow(ax, 13.7, X["main"], X["detail"], "show_item()  자동 보정 뷰",
          color=VIOLET)

# ── Phase D: 사람이 확정 ──
sep(14.3, "D. 사람이 [파랑/초록] 확정", GREEN)
seq_arrow(ax, 14.8, X["user"], X["detail"], "[파랑으로] 클릭", color=INK)
seq_arrow(ax, 15.35, X["detail"], X["main"], "to_blue 시그널 → _set_human('BLUE')",
          color=VIOLET, dashed=True)
seq_arrow(ax, 15.9, X["main"], X["proj"], "set_human(state, item, 'BLUE')",
          color=TEAL)
seq_arrow(ax, 16.45, X["proj"], X["store"], "store.set() → decisions.json",
          color=TEAL)
note_box(ax, 6.2, 16.58, 5.6, 0.62,
         "＋ _move_copy(사본 이동) · _append_move_log(moves-log.csv)\n＋ undo_stack 에 쌓기",
         color=INK2, fill="#ecf7f0", ec=TEAL)

# ── Phase E: 되돌리기(짧게) ──
sep(17.45, "E. 되돌리기", AMBER)
seq_arrow(ax, 17.9, X["user"], X["detail"], "[되돌리기] 클릭", color=INK)
seq_arrow(ax, 18.55, X["detail"], X["main"],
          "undone 시그널 → _undo() → undo(state)\n(store 복원 · 사본 원위치 · moves-log 기록)",
          color=VIOLET, dashed=True)

out = Path(__file__).resolve().parent.parent / "05-sequence-gui.png"
save(fig, out)
print("saved", out)
