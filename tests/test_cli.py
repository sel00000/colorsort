import csv
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from colorsort.cli import _preparse_lang, main
from colorsort.messages import t


def _write_png(path: Path, color, size=(20, 20)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    a = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    a[..., 0], a[..., 1], a[..., 2] = color
    Image.fromarray(a, mode="RGB").save(path)


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def test_dry_run_is_the_default_and_copies_nothing(tmp_path, capsys):
    src = tmp_path / "in"
    _write_png(src / "sub" / "b.png", (0, 0, 17))
    _write_png(src / "sub" / "g.png", (0, 17, 2))
    out = tmp_path / "out"

    code = main([str(src), "--output", str(out), "--lang", "ko"])
    captured = capsys.readouterr().out

    assert code == 0
    assert "총 2장" in captured
    assert "--apply" in captured
    assert not (out / "blue").exists(), "미리보기에서는 복사하지 않는다"


def test_apply_actually_copies_and_leaves_originals(tmp_path):
    src = tmp_path / "in"
    _write_png(src / "sub" / "b.png", (0, 0, 17))
    _write_png(src / "sub" / "g.png", (0, 17, 2))
    out = tmp_path / "out"

    code = main([str(src), "--output", str(out), "--apply", "--lang", "ko"])

    assert code == 0
    assert (out / "blue" / "sub__b.png").exists()
    assert (out / "green" / "sub__g.png").exists()
    assert (src / "sub" / "b.png").exists(), "원본이 남아야 한다"
    assert (src / "sub" / "g.png").exists()


def test_apply_writes_csv_and_logs(tmp_path):
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"

    main([str(src), "--output", str(out), "--apply", "--lang", "ko"])

    assert (out / "results.csv").exists()
    assert (out / "copy-log.csv").exists()
    assert (out / "run.json").exists()


def test_dry_run_still_writes_the_report(tmp_path):
    """미리보기에서도 표는 만든다. 무엇이 어디로 갈지 확인할 수 있어야 한다."""
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"

    main([str(src), "--output", str(out), "--lang", "ko"])

    assert (out / "results.csv").exists()
    assert not (out / "copy-log.csv").exists(), "복사하지 않았으므로 복사 기록은 없다"


def test_english_output(tmp_path, capsys):
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"

    code = main([str(src), "--output", str(out), "--lang", "en"])
    captured = capsys.readouterr().out

    assert code == 0
    assert "Checked 1 images." in captured
    assert "--apply" in captured
    assert "총" not in captured, "영어를 골랐으면 한국어가 섞이면 안 된다"


def test_csv_headers_follow_the_chosen_language(tmp_path):
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))

    main([str(src), "--output", str(tmp_path / "ko"), "--lang", "ko"])
    main([str(src), "--output", str(tmp_path / "en"), "--lang", "en"])

    ko_head = (tmp_path / "ko" / "results.csv").read_text(encoding="utf-8-sig").splitlines()[0]
    en_head = (tmp_path / "en" / "results.csv").read_text(encoding="utf-8-sig").splitlines()[0]
    assert "판정" in ko_head
    assert "verdict" in en_head


def test_folder_names_do_not_change_with_language(tmp_path):
    """언어가 폴더를 갈라놓으면 결과가 두 곳으로 쪼개진다. 반드시 같아야 한다."""
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))

    main([str(src), "--output", str(tmp_path / "o1"), "--apply", "--lang", "ko"])
    main([str(src), "--output", str(tmp_path / "o2"), "--apply", "--lang", "en"])

    ko_dirs = sorted(p.name for p in (tmp_path / "o1").iterdir() if p.is_dir())
    en_dirs = sorted(p.name for p in (tmp_path / "o2").iterdir() if p.is_dir())
    assert ko_dirs == en_dirs == ["blue"]


def test_run_json_records_the_language(tmp_path):
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"

    main([str(src), "--output", str(out), "--lang", "en"])
    data = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert data["표시언어"] == "en"


def test_missing_input_folder_reports_clearly(tmp_path, capsys):
    code = main([str(tmp_path / "nope"), "--output", str(tmp_path / "out"), "--lang", "ko"])
    assert code == 1
    assert "찾을 수 없" in capsys.readouterr().err


def test_missing_input_folder_reports_clearly_in_english(tmp_path, capsys):
    code = main([str(tmp_path / "nope"), "--output", str(tmp_path / "out"), "--lang", "en"])
    assert code == 1
    assert "not found" in capsys.readouterr().err


def test_empty_input_folder_reports_clearly(tmp_path, capsys):
    src = tmp_path / "in"
    src.mkdir()
    code = main([str(src), "--output", str(tmp_path / "out"), "--lang", "ko"])
    assert code == 1
    assert "PNG" in capsys.readouterr().err


def test_help_text_follows_the_language(capsys):
    for lang, needle in (("ko", "미리보기"), ("en", "preview")):
        with pytest.raises(SystemExit):
            main(["--lang", lang, "--help"])
        assert needle in capsys.readouterr().out


def test_preparse_reads_the_language_flags_before_the_rest():
    """도움말을 어느 언어로 만들지는 본 파싱 전에 알아야 한다."""
    assert _preparse_lang(["in", "--lang", "en"]) == ("en", False)
    assert _preparse_lang(["in", "--lang-reset"]) == (None, True)
    assert _preparse_lang(["in"]) == (None, False)


def test_name_collision_stops_before_copying_anything(tmp_path, capsys):
    """사본 이름이 겹치면 덮어쓰기 전에 멈춘다.

    'a/x.png' 와 'a__x.png' 는 둘 다 사본 이름이 'a__x.png' 가 된다.
    """
    src = tmp_path / "in"
    _write_png(src / "a" / "x.png", (0, 0, 17))
    _write_png(src / "a__x.png", (0, 0, 17))
    out = tmp_path / "out"

    code = main([str(src), "--output", str(out), "--apply", "--lang", "ko"])

    assert code == 1
    assert "겹칩니다" in capsys.readouterr().err
    assert not out.exists(), "충돌이면 아무것도 만들지 않는다"


# --- 모듈 사이 이음매 회귀 시험 -------------------------------------------------
# 아래 두 개는 각 모듈을 따로 볼 때는 보이지 않고, 이어 붙였을 때만 드러나는 결함을 막는다.


def test_load_failure_reason_is_a_readable_sentence_in_both_languages(tmp_path):
    """읽을 수 없는 파일의 사유가 사람이 읽는 문장이어야 한다.

    loading 이 돌려주는 load_error 는 이미 Msg 다. 그것을 또 다른 Msg 의 인자로
    감싸면 CSV 에 Msg(key=..., params=...) 객체 표현이 그대로 찍힌다. 로더 시험도
    보고서 시험도 이 이음매를 지나가지 않으므로 여기서 잡는다.
    """
    src = tmp_path / "in"
    src.mkdir()
    (src / "broken.png").write_bytes(b"this is not a PNG at all")

    for lang, needle in (("ko", "파일을 읽을 수 없습니다"),
                         ("en", "Could not read the file")):
        out = tmp_path / lang
        assert main([str(src), "--output", str(out), "--lang", lang]) == 0

        reason = _rows(out / "results.csv")[0][t("col.reason", lang)]
        assert "Msg(" not in reason, f"Msg 객체가 그대로 찍혔다: {reason}"
        assert "reason.load_error" not in reason, f"열쇠가 그대로 찍혔다: {reason}"
        assert needle in reason, f"사람이 읽는 문장이 아니다: {reason}"


def test_rerunning_does_not_count_its_own_copies(tmp_path, capsys):
    """출력 폴더가 입력 폴더 안에 있어도 사본을 원본으로 세지 않는다.

    README 는 입력 '.' 에 --output results 를 권한다. 즉 출력 폴더가 입력 폴더
    안에 있다. 훑을 때 걸러내지 않으면 두 번째 실행이 196 -> 392 -> 784 로 불어난다.

    두 번째 실행은 목적지가 이미 있으므로 건너뛴다. 그 오류는 Msg 이므로
    렌더링하지 않으면 객체 표현이 그대로 찍힌다. 그것도 여기서 함께 잡는다.
    """
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    _write_png(src / "g.png", (0, 17, 2))
    out = src / "results"          # 출력 폴더가 입력 폴더 안에 있다

    assert main([str(src), "--output", str(out), "--apply", "--lang", "ko"]) == 0
    first = _rows(out / "results.csv")
    capsys.readouterr()            # 첫 실행의 출력은 버린다

    assert main([str(src), "--output", str(out), "--apply", "--lang", "ko"]) == 0
    second = _rows(out / "results.csv")
    captured = capsys.readouterr()

    assert len(first) == 2
    assert len(second) == len(first), (
        f"두 번째 실행이 자기 사본을 원본으로 셌다: {len(first)}장 -> {len(second)}장")
    assert "총 2장" in captured.out

    assert "Msg(" not in captured.err, f"복사 오류가 Msg 객체로 찍혔다: {captured.err}"
    assert "이미 존재하여 건너뜀" in captured.err
