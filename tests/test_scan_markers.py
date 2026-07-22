"""과거 실행의 결과 폴더(run.json 마커)를 입력에서 건너뛰는 규칙.

2026-07-22 사용자 승인으로 추가된 v1 스캔 동작 — 판정 로직과 무관하다.
"""
import numpy as np
from PIL import Image

from colorsort.cli import _input_photos


def _png(path, b=200):
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = np.zeros((8, 8, 3), dtype=np.uint8)
    arr[..., 2] = b
    Image.fromarray(arr).save(path)


def test_nested_results_with_marker_is_skipped(tmp_path):
    _png(tmp_path / "sub" / "a.png")
    _png(tmp_path / "sub" / "results" / "blue" / "copy.png")
    _png(tmp_path / "sub" / "results" / ".thumbs" / "ab" / "thumb.png")
    (tmp_path / "sub" / "results" / "run.json").write_text("{}", encoding="utf-8")
    kept, excluded = _input_photos(tmp_path, tmp_path / "out")
    assert [p.name for p in kept] == ["a.png"]
    assert excluded == 2


def test_plain_results_folder_without_marker_is_kept(tmp_path):
    # 이름만 results 인 진짜 사진 폴더는 건너뛰면 안 된다 — 마커가 기준이다.
    _png(tmp_path / "results" / "b.png")
    kept, excluded = _input_photos(tmp_path, tmp_path / "out")
    assert len(kept) == 1 and excluded == 0


def test_input_root_itself_with_marker_is_scanned(tmp_path):
    # 결과 폴더 자체를 입력으로 고른 것은 의도된 선택이므로 존중한다.
    _png(tmp_path / "c.png")
    (tmp_path / "run.json").write_text("{}", encoding="utf-8")
    kept, excluded = _input_photos(tmp_path, tmp_path / "out")
    assert len(kept) == 1 and excluded == 0
