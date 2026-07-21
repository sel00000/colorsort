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


def test_copy_log_never_records_a_copy_that_did_not_happen(tmp_path):
    """사용자가 직접 넣어둔 파일의 자리는 복사 기록에 남지 않는다.

    복사 기록은 되돌리기용이다. 하지도 않은 복사가 적혀 있으면, 그 기록을 보고
    되돌리려는 사용자가 이 도구가 만들지도 않은 자기 파일을 지우게 된다.
    원본을 건드리지 않는다는 약속은 지켜지지만 되돌리기 기록이 엉뚱한 곳을 가리킨다.
    """
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"
    mine = out / "blue" / "b.png"
    mine.parent.mkdir(parents=True)
    mine.write_text("사용자가 직접 넣어둔 소중한 파일", encoding="utf-8")

    assert main([str(src), "--output", str(out), "--apply", "--lang", "ko"]) == 0

    assert mine.read_text(encoding="utf-8") == "사용자가 직접 넣어둔 소중한 파일"
    logged = [r["사본경로"] for r in _rows(out / "copy-log.csv")]
    assert logged == [], f"하지 않은 복사가 되돌리기 기록에 남았다: {logged}"


def test_files_inside_the_output_folder_are_reported_not_dropped_in_silence(tmp_path, capsys):
    """--output 이 이미 사진이 든 폴더를 가리키면 몇 장이 빠졌는지 말해야 한다.

    실제 자료 폴더가 A/ 와 B/ 이므로 --output A 는 충분히 일어날 수 있는 실수다.
    말없이 빼면 사용자는 검사되지 않은 사진이 있다는 사실조차 알 수 없다.
    """
    root = tmp_path / "in"
    _write_png(root / "A" / "1.png", (0, 0, 17))
    _write_png(root / "A" / "2.png", (0, 17, 2))
    _write_png(root / "B" / "3.png", (0, 0, 17))

    assert main([str(root), "--output", str(root / "A"), "--lang", "ko"]) == 0
    ko = capsys.readouterr().out
    assert "총 1장" in ko
    assert "제외한 파일: 2장" in ko, f"제외한 사실을 알리지 않았다: {ko}"

    assert main([str(root), "--output", str(root / "A"), "--lang", "en"]) == 0
    en = capsys.readouterr().out
    assert "Excluded 2 file(s)" in en, f"제외한 사실을 알리지 않았다: {en}"


def test_a_hard_copy_failure_shows_up_in_the_exit_code(tmp_path, capsys):
    """복사가 전부 실패했는데 0을 돌려주면 자동 실행이 실패를 알아채지 못한다.

    목적지 폴더가 놓일 자리에 같은 이름의 '파일'을 두면 mkdir 이 OSError 를 낸다.
    """
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"
    out.mkdir()
    (out / "blue").write_text("폴더 자리를 막고 있는 파일", encoding="utf-8")

    code = main([str(src), "--output", str(out), "--apply", "--lang", "ko"])
    captured = capsys.readouterr()

    assert code == 1, "복사가 하나도 되지 않았는데 성공으로 끝났다"
    assert "복사 실패" in captured.err
    assert "0장을 복사했습니다" in captured.out, (
        f"한 장도 복사하지 못했는데 복사했다고 말한다: {captured.out}")


def test_unwritable_output_folder_reports_a_sentence_not_a_traceback(tmp_path, capsys):
    """결과를 쓸 수 없으면 파이썬 추적 대신 문장을 보여준다.

    --output 이 보호된 폴더나 동기화 폴더를 가리키는 일은 Windows 에서 충분히 일어난다.
    그때 나오던 PermissionError 추적은 이 도구를 쓸 사람에게 읽을 수도 없고 무엇을
    해야 할지도 알려주지 않는 출력이었다.

    출력 폴더가 놓일 자리에 같은 이름의 '파일'을 두어 mkdir 이 OSError 를 내게 한다.
    권한 비트와 달리 관리자로 실행해도, 어느 운영체제에서도 똑같이 막힌다.
    """
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))

    for lang, needle in (("ko", "저장할 수 없습니다"),
                         ("en", "could not write the results")):
        blocked = tmp_path / f"out-{lang}"
        blocked.write_text("출력 폴더 자리를 막고 있는 파일", encoding="utf-8")

        code = main([str(src), "--output", str(blocked), "--lang", lang])
        captured = capsys.readouterr()

        assert code == 1
        assert "Traceback" not in captured.err
        assert needle in captured.err, f"사람이 읽는 문장이 아니다: {captured.err}"
        assert str(blocked) in captured.err, (
            f"어느 경로가 막혔는지 말하지 않았다: {captured.err}")


def test_a_failed_copy_log_still_reports_what_was_copied(tmp_path, capsys):
    """복사 기록을 남기지 못해도 이미 한 복사는 사실대로 알린다.

    이 시점에는 복사가 이미 끝나 있다. 기록 실패를 이유로 말없이 돌아가면 사용자는
    자기 디스크에 무엇이 생겼는지 모른 채 남는다. 실패는 실패대로 알리고 한 일은
    한 일대로 알려야 한다.

    copy-log.csv 자리에 폴더를 두어 파일을 여는 순간 OSError 가 나게 한다.
    """
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"
    (out / "copy-log.csv").mkdir(parents=True)

    code = main([str(src), "--output", str(out), "--apply", "--lang", "ko"])
    captured = capsys.readouterr()

    assert code == 1
    assert "Traceback" not in captured.err
    assert "저장할 수 없습니다" in captured.err, (
        f"사람이 읽는 문장이 아니다: {captured.err}")
    assert (out / "blue" / "b.png").exists(), "복사 자체는 되었어야 한다"
    assert "1장을 복사했습니다" in captured.out, (
        f"복사를 해놓고 알리지 않았다: {captured.out}")


def test_skipping_an_existing_copy_is_still_a_success(tmp_path, capsys):
    """이미 있어 건너뛴 것은 실패가 아니다. 같은 명령의 재실행은 그냥 성공이어야 한다."""
    src = tmp_path / "in"
    _write_png(src / "b.png", (0, 0, 17))
    out = tmp_path / "out"

    assert main([str(src), "--output", str(out), "--apply", "--lang", "ko"]) == 0
    capsys.readouterr()

    assert main([str(src), "--output", str(out), "--apply", "--lang", "ko"]) == 0
    again = capsys.readouterr()
    assert "이미 존재하여 건너뜀" in again.err
    assert "0장을 복사했습니다" in again.out, (
        f"건너뛰기만 했는데 복사했다고 말한다: {again.out}")
