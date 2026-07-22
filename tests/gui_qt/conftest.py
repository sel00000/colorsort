import os
import types                       # fake_project(오리 상태)와 스텁 주입 양쪽에서 쓴다

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication




@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def fake_project(monkeypatch):
    """[C1 주의: 이 fixture는 지우지 말고 그대로 유지한다 — 위 sys.modules 주입 스텁과
    수명이 다르다.] mainwindow의 배선(populate·count·filter)을 통제된 3장 가짜 상태로
    검증한다. project 창구의 open_project/apply_copies를 monkeypatch로 갈아끼우므로
    project가 주입 스텁이든(지금) 실물이든(C1 이후) 무관하게 동작한다 — 실물 open_project가
    존재하지 않는 /fake 폴더를 훑어 0장을 내는 것을 원천 차단한다.
    오리 타이핑 상태라 실제 FileResult가 필요 없다(mainwindow가 쓰는 속성만 갖춘다)."""
    import types
    from pathlib import Path

    import colorsortgui.project as project

    def _item(name, sub):
        return types.SimpleNamespace(
            path=Path("/fake") / name, rel=name, fp=name.replace(".", "_"),
            result=None, machine_sub=sub, human=None, effective_sub=sub,
            dest=f"{sub}/{name}")

    items = [_item("b.png", "blue"), _item("g.png", "green"),
             _item("dark.png", "review/no-signal")]

    def _counts():
        c = {"all": len(items), "blue": 0, "green": 0, "review": 0,
             "no-signal": 0, "mixed": 0, "other": 0}
        for it in items:
            sub = it.effective_sub
            if sub == "blue":
                c["blue"] += 1
            elif sub == "green":
                c["green"] += 1
            else:
                c["review"] += 1
                c[sub.split("/", 1)[1]] += 1
        return c

    state = types.SimpleNamespace(
        input_root=Path("/fake"), output_root=Path("/fake/results"),
        items=items, store=None, n_excluded=0, undo_stack=[], counts=_counts)

    monkeypatch.setattr(project, "open_project", lambda inp, out: state)
    monkeypatch.setattr(project, "apply_copies", lambda st: (len(st.items), []))
    yield state
