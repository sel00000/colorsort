from pathlib import Path

import pytest

from colorsort.config import DEFAULT_CONFIG, Config
from colorsort.models import Decision, FileResult, Measurements, Msg
from colorsort.sorting import execute_copies, find_collisions, plan_copies


def _m() -> Measurements:
    return Measurements(
        n_pixels=100, max_red=0, peak=17, n_lit_1=100, gate_used=5, n_gated=100,
        n_blue=100, n_green=0, n_intermediate=0, energy_blue=1700, energy_green=0,
        file_bytes=1000, has_transparent_pixels=False,
    )


def _r(rel: str, label: str) -> FileResult:
    return FileResult(Path("/in") / rel, _m(), Decision(label, Msg("reason.pure_blue"), False))


def test_routes_each_label_to_its_folder():
    items = plan_copies(
        [_r("a/1.png", "BLUE"), _r("a/2.png", "GREEN"),
         _r("a/3.png", "HYBRID"), _r("a/4.png", "ABSTAIN")],
        input_root=Path("/in"), output_root=Path("/out"), config=DEFAULT_CONFIG,
    )
    by_name = {i.source.name: i.dest for i in items}
    assert by_name["1.png"].parent.name == "blue"
    assert by_name["2.png"].parent.name == "green"
    assert by_name["3.png"].parent.name == "review"
    assert by_name["4.png"].parent.name == "review"


def test_folder_names_come_from_config_not_from_language():
    """언어를 바꿔도 폴더 이름은 그대로여야 한다. 갈라지면 결과가 두 곳으로 쪼개진다."""
    korean_folders = Config(folder_review="확인필요")
    items = plan_copies([_r("a/3.png", "HYBRID")], Path("/in"), Path("/out"), korean_folders)
    assert items[0].dest.parent.name == "확인필요"


def test_source_folder_is_prefixed_to_avoid_collisions():
    """서로 다른 폴더의 같은 이름 파일이 덮어써지면 안 된다."""
    items = plan_copies(
        [_r("A/L picture/11-blue.png", "BLUE"), _r("B/P1 Picture/11-blue.png", "BLUE")],
        input_root=Path("/in"), output_root=Path("/out"), config=DEFAULT_CONFIG,
    )
    dests = [i.dest for i in items]
    assert len(set(dests)) == 2, "두 사본의 경로가 서로 달라야 한다"
    assert all("11-blue.png" in d.name for d in dests)
    assert any("L picture" in d.name for d in dests)
    assert any("P1 Picture" in d.name for d in dests)


def test_file_at_input_root_gets_no_prefix():
    items = plan_copies([_r("top.png", "BLUE")],
                        input_root=Path("/in"), output_root=Path("/out"),
                        config=DEFAULT_CONFIG)
    assert items[0].dest.name == "top.png"


def test_find_collisions_reports_duplicates():
    a = _r("x/same.png", "BLUE")
    b = _r("x/same.png", "BLUE")
    items = plan_copies([a, b], input_root=Path("/in"), output_root=Path("/out"),
                        config=DEFAULT_CONFIG)
    collisions = find_collisions(items)
    assert len(collisions) == 1
    dest, sources = collisions[0]
    assert len(sources) == 2


def test_find_collisions_empty_when_all_unique():
    items = plan_copies([_r("a/1.png", "BLUE"), _r("b/2.png", "GREEN")],
                        input_root=Path("/in"), output_root=Path("/out"),
                        config=DEFAULT_CONFIG)
    assert find_collisions(items) == []


def test_execute_copies_creates_files_without_touching_source(tmp_path):
    src_dir = tmp_path / "in" / "sub"
    src_dir.mkdir(parents=True)
    src = src_dir / "pic.png"
    src.write_bytes(b"original content")
    before = src.read_bytes()

    out = tmp_path / "out"
    items = plan_copies([FileResult(src, _m(), Decision("BLUE", Msg("reason.pure_blue"), False))],
                        input_root=tmp_path / "in", output_root=out, config=DEFAULT_CONFIG)
    count, errors = execute_copies(items)

    assert count == 1
    assert errors == []
    assert (out / "blue" / "sub__pic.png").read_bytes() == b"original content"
    assert src.exists(), "원본이 남아 있어야 한다"
    assert src.read_bytes() == before, "원본이 변경되지 않아야 한다"


def test_execute_refuses_to_overwrite(tmp_path):
    src_dir = tmp_path / "in"
    src_dir.mkdir()
    src = src_dir / "pic.png"
    src.write_bytes(b"new")

    out = tmp_path / "out"
    (out / "blue").mkdir(parents=True)
    (out / "blue" / "pic.png").write_bytes(b"existing")

    items = plan_copies([FileResult(src, _m(), Decision("BLUE", Msg("reason.pure_blue"), False))],
                        input_root=src_dir, output_root=out, config=DEFAULT_CONFIG)
    count, errors = execute_copies(items)

    assert count == 0
    assert len(errors) == 1
    assert errors[0].key == "error.copy_exists"
    assert (out / "blue" / "pic.png").read_bytes() == b"existing", "덮어쓰지 않아야 한다"
