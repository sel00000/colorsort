import csv
import json
from pathlib import Path

from colorsort.config import DEFAULT_CONFIG
from colorsort.models import CopyItem, Decision, FileResult, Measurements, Msg
from colorsort.report import summarize, write_copy_log, write_results_csv, write_run_json


def _m(**kw) -> Measurements:
    base = dict(
        n_pixels=100, max_red=0, peak=17, n_lit_1=100, gate_used=5, n_gated=100,
        n_blue=100, n_green=0, n_intermediate=0, energy_blue=1700, energy_green=0,
        file_bytes=1000, has_transparent_pixels=False,
    )
    base.update(kw)
    return Measurements(**base)


_PARAMS = {"n_gated": 100, "n_blue": 100, "n_green": 0, "peak": 17, "f_blue": 1.0}


def _results() -> list[FileResult]:
    return [
        FileResult(Path("/in/a/1.png"), _m(),
                   Decision("BLUE", Msg("reason.pure_blue", _PARAMS), False)),
        FileResult(Path("/in/a/2.png"), _m(n_blue=0, n_green=100),
                   Decision("GREEN", Msg("reason.pure_green", _PARAMS), False)),
        FileResult(Path("/in/a/3.png"), _m(gate_used=None, n_blue=0, n_lit_1=0),
                   Decision("ABSTAIN",
                            Msg("reason.no_signal",
                                {"needed": 30, "found": 0, "peak": 0, "file_bytes": 267}),
                            True,
                            (Msg("warn.empty_but_large",
                                 {"file_bytes": 9000, "median": 1000.0}),))),
    ]


def test_csv_has_one_row_per_file_with_evidence(tmp_path):
    out = tmp_path / "results.csv"
    items = [CopyItem(Path("/in/a/1.png"), Path("/out/blue/a__1.png"), "BLUE")]
    write_results_csv(_results(), items, out, "ko")

    with out.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 3
    assert rows[0]["판정"] == "BLUE"
    assert "파랑" in rows[0]["사유"]
    assert rows[0]["파랑픽셀수"] == "100"
    assert rows[0]["사본경로"] == "/out/blue/a__1.png"
    assert rows[1]["판정"] == "GREEN"
    assert rows[2]["판정"] == "ABSTAIN"
    assert "파일 크기" in rows[2]["경고"]
    assert rows[2]["사본경로"] == "", "복사 계획에 없는 파일은 사본 경로가 비어야 한다"


def test_csv_headers_and_reasons_follow_the_language(tmp_path):
    ko, en = tmp_path / "ko.csv", tmp_path / "en.csv"
    write_results_csv(_results(), [], ko, "ko")
    write_results_csv(_results(), [], en, "en")

    with ko.open(encoding="utf-8-sig", newline="") as fh:
        ko_rows = list(csv.DictReader(fh))
    with en.open(encoding="utf-8-sig", newline="") as fh:
        en_rows = list(csv.DictReader(fh))

    assert "판정" in ko_rows[0]
    assert "verdict" in en_rows[0]
    assert "Blue" in en_rows[0]["reason"]
    assert en_rows[0]["verdict"] == "BLUE", "판정 값은 기계용이므로 번역하지 않는다"


def test_csv_is_utf8_bom_so_excel_shows_korean(tmp_path):
    """엑셀은 BOM 없는 UTF-8 CSV의 한글을 깨뜨린다."""
    out = tmp_path / "results.csv"
    write_results_csv(_results(), [], out, "ko")
    assert out.read_bytes().startswith(b"\xef\xbb\xbf")


def test_copy_log_records_source_and_dest(tmp_path):
    out = tmp_path / "copy-log.csv"
    items = [CopyItem(Path("/in/a/1.png"), Path("/out/blue/a__1.png"), "BLUE")]
    write_copy_log(items, out)
    with out.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["원본경로"] == "/in/a/1.png"
    assert rows[0]["사본경로"] == "/out/blue/a__1.png"


def test_run_json_records_provenance(tmp_path):
    out = tmp_path / "run.json"
    write_run_json(out, DEFAULT_CONFIG, n_files=196, applied=False, lang="en")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["파일수"] == 196
    assert data["실제복사여부"] is False
    assert data["표시언어"] == "en"
    assert data["폴더이름"]["review"] == "review"
    assert data["설정"]["rho_blue"] == 0.90
    assert "규칙버전" in data
    assert "실행시각" in data


def test_summary_counts_each_folder():
    text = summarize(_results(), DEFAULT_CONFIG, "ko")
    assert "196" not in text
    assert "blue" in text
    assert "green" in text
    assert "review" in text
    assert "총 3장" in text


def test_summary_explains_dry_run_next_step():
    text = summarize(_results(), DEFAULT_CONFIG, "ko")
    assert "--apply" in text
    assert "원본" in text


def test_summary_in_english():
    text = summarize(_results(), DEFAULT_CONFIG, "en")
    assert "Checked 3 images." in text
    assert "--apply" in text
    assert "총" not in text


def test_summary_folder_names_stay_the_same_across_languages():
    """숫자와 문장은 번역되지만 폴더 이름 줄은 양쪽에서 동일해야 한다."""
    ko = summarize(_results(), DEFAULT_CONFIG, "ko")
    en = summarize(_results(), DEFAULT_CONFIG, "en")
    for name in ("blue/", "green/", "review/"):
        assert name in ko and name in en
