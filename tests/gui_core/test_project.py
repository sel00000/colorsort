import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from colorsortgui.project import open_project, apply_copies, set_human, undo

def _png(path, g=0, b=0):
    arr = np.zeros((8, 8, 3), dtype=np.uint8)
    arr[..., 1] = g; arr[..., 2] = b
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(path)

def _corpus(root):
    _png(root / "in" / "b.png", b=200)                    # BLUE
    _png(root / "in" / "g.png", g=200)                    # GREEN (rho=0)
    _png(root / "in" / "dark.png")                        # ABSTAIN no_signal
    return root / "in", root / "out"

def test_open_counts_and_dests(tmp_path):
    inp, out = _corpus(tmp_path)
    st = open_project(inp, out)
    c = st.counts()
    assert (c["all"], c["blue"], c["green"], c["review"]) == (3, 1, 1, 1)
    assert c["no-signal"] == 1 and c["mixed"] == 0 and c["other"] == 0
    dark = next(i for i in st.items if i.path.name == "dark.png")
    assert dark.machine_sub == "review/no-signal" and dark.dest == "review/no-signal/dark.png"

def test_apply_copies_into_subfolders(tmp_path):
    inp, out = _corpus(tmp_path)
    st = open_project(inp, out)
    copied, errors = apply_copies(st)
    assert copied == 3 and not errors
    assert (out / "blue" / "b.png").exists()
    assert (out / "review" / "no-signal" / "dark.png").exists()
    assert (out / "results.csv").exists() and (out / "run.json").exists()

def test_set_human_moves_copy_and_persists(tmp_path):
    inp, out = _corpus(tmp_path)
    st = open_project(inp, out); apply_copies(st)
    dark = next(i for i in st.items if i.path.name == "dark.png")
    set_human(st, dark, "BLUE")
    assert (out / "blue" / "dark.png").exists()
    assert not (out / "review" / "no-signal" / "dark.png").exists()
    assert (out / "moves-log.csv").exists()
    st2 = open_project(inp, out)                          # 재실행해도 기억
    dark2 = next(i for i in st2.items if i.path.name == "dark.png")
    assert dark2.human == "BLUE" and dark2.effective_sub == "blue"
    assert st2.counts()["blue"] == 2 and st2.counts()["review"] == 0

def test_rename_survives(tmp_path):
    inp, out = _corpus(tmp_path)
    st = open_project(inp, out); apply_copies(st)
    dark = next(i for i in st.items if i.path.name == "dark.png")
    set_human(st, dark, "GREEN")
    (inp / "dark.png").rename(inp / "renamed.png")        # 원본 개명
    st2 = open_project(inp, out)
    ren = next(i for i in st2.items if i.path.name == "renamed.png")
    assert ren.human == "GREEN"                            # 지문이라 알아본다

def test_undo(tmp_path):
    inp, out = _corpus(tmp_path)
    st = open_project(inp, out); apply_copies(st)
    dark = next(i for i in st.items if i.path.name == "dark.png")
    set_human(st, dark, "BLUE")
    item = undo(st)
    assert item is dark and dark.human is None
    assert (out / "review" / "no-signal" / "dark.png").exists()
    assert undo(st) is None

def test_regression_196_same_judgments(tmp_path):
    """실제 196장: 판정 라벨·이유가 v1 CLI와 완전히 같아야 한다.

    계획서는 root=parents[2]에서 실사진 A/·B/를 직접 스캔한다. 그러나 이 저장소에서
    A/·B/는 .gitignore 대상이라 격리된 git 워크트리에는 없다(상위 본체 체크아웃에만
    있다). 그래서 상위로 올라가 실사진을 찾고, read-only 원본을 tmp_path로 복사해
    그 사본에서 v1·v2를 함께 돌린다. tmp_path가 곧 임시 출력 정리 fixture다([A] 이탈).
    """
    import colorsort.cli as cli
    from colorsort.config import DEFAULT_CONFIG
    src = None
    for parent in Path(__file__).resolve().parents:
        if (parent / "A").is_dir() and (parent / "B").is_dir():
            src = parent
            break
    if src is None:
        import pytest; pytest.skip("실사진 없음")
    corpus = tmp_path / "corpus"
    # 사용자가 GUI로 원본 폴더를 분류하면 그 안에 results/(사본·썸네일)가 생긴다.
    # 그것은 원본이 아니므로 말뭉치에서 뺀다 — 도구 자신도 자기 출력은 검사하지 않는다.
    skip_results = shutil.ignore_patterns("results")
    shutil.copytree(src / "A", corpus / "A", ignore=skip_results)
    shutil.copytree(src / "B", corpus / "B", ignore=skip_results)
    v1_results, _, _ = cli.run(corpus, tmp_path / "out1", DEFAULT_CONFIG, False)
    st = open_project(corpus, tmp_path / "out2")
    v1 = {r.path: (r.decision.label, r.decision.reason_code) for r in v1_results}
    v2 = {i.result.path: (i.result.decision.label, i.result.decision.reason_code) for i in st.items}
    assert v1 == v2
    assert len(v1) == 196
