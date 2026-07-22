import json
from colorsortgui.decisions import DecisionStore

def test_roundtrip(tmp_path):
    p = tmp_path / "decisions.json"
    s = DecisionStore(p)
    assert s.get("f" * 64) is None and s.count == 0
    s.set("f" * 64, "BLUE", "a.png")
    s2 = DecisionStore(p)                       # 새로 열어도 남아 있다
    assert s2.get("f" * 64) == "BLUE" and s2.count == 1

def test_remove(tmp_path):
    p = tmp_path / "decisions.json"
    s = DecisionStore(p); s.set("a" * 64, "GREEN", "g.png"); s.remove("a" * 64)
    assert DecisionStore(p).get("a" * 64) is None

def test_atomic_no_partial_file(tmp_path):
    p = tmp_path / "decisions.json"
    s = DecisionStore(p); s.set("a" * 64, "BLUE", "x.png")
    assert not list(tmp_path.glob("*.tmp*"))    # 임시 파일이 남지 않는다

def test_corrupt_file_recovers(tmp_path):
    p = tmp_path / "decisions.json"; p.write_text("{broken", encoding="utf-8")
    s = DecisionStore(p)                        # 죽지 않고 빈 상태로 연다
    assert s.count == 0
    assert (tmp_path / "decisions.json.bad").exists()   # 원본은 증거로 보존

def test_invalid_label_rejected(tmp_path):
    s = DecisionStore(tmp_path / "d.json")
    try:
        s.set("a" * 64, "PURPLE", "x.png"); assert False
    except ValueError:
        pass
