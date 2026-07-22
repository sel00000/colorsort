"""사진 스캔이 PNG만이 아니라 여러 형식을 대소문자 무관하게 잡는지 검증.

_input_photos 는 파일을 열지 않고 확장자만 본다. 그래서 스캔 테스트는 실제
이미지 데이터가 필요 없다 — 확장자만 맞으면 빈 파일이라도 걸려야 한다. 반대로
load_image 가 JPG를 실제로 읽는지는 진짜 JPG 한 장으로 따로 확인한다.

형식 확장은 2026-07-22 사용자 승인으로 추가된 스캔 동작이며 판정 로직과 무관하다.
run.json 마커 제외 자체는 test_scan_markers.py 가 다룬다 — 여기서는 그 제외가
형식과 무관하게 동작하는지에 집중한다.
"""
import numpy as np
from PIL import Image

from colorsort.cli import _input_photos
from colorsort.loading import load_image


def _touch(path, data=b"\x00"):
    """확장자만 있으면 되는 빈 파일. _input_photos 는 열지 않으므로 내용은 무의미하다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def test_common_photo_formats_are_found(tmp_path):
    # 지원 형식 전부 — 대문자 .JPG 포함해 하나도 빠지면 안 된다.
    for name in ("a.jpg", "b.jpeg", "c.JPG", "d.png", "e.bmp",
                 "f.gif", "g.webp", "h.tif", "i.tiff"):
        _touch(tmp_path / name)
    kept, excluded = _input_photos(tmp_path, tmp_path / "out")
    names = [p.name for p in kept]
    assert set(names) == {
        "a.jpg", "b.jpeg", "c.JPG", "d.png", "e.bmp",
        "f.gif", "g.webp", "h.tif", "i.tiff",
    }
    assert names == sorted(names)  # 결과 순서는 결정론적이어야 한다
    assert excluded == 0


def test_extension_case_is_ignored(tmp_path):
    # 대소문자 무관 — Windows 든 Linux 든 똑같이 걸려야 한다. 과거 rglob("*.png") 는
    # Linux 에서 대문자 .PNG 를 놓쳤다. 이 테스트가 그 회귀를 막는다.
    for name in ("A.PNG", "B.JpG", "C.Webp", "D.TIFF"):
        _touch(tmp_path / name)
    kept, _ = _input_photos(tmp_path, tmp_path / "out")
    assert {p.name for p in kept} == {"A.PNG", "B.JpG", "C.Webp", "D.TIFF"}


def test_non_photo_files_are_ignored(tmp_path):
    # 사진이 아닌 파일은 아예 목록에 없다 — 제외 개수에도 잡히지 않는다.
    _touch(tmp_path / "keep.jpg")
    _touch(tmp_path / "notes.txt")
    _touch(tmp_path / "clip.mp4")
    _touch(tmp_path / "data.json")
    _touch(tmp_path / "archive.zip")
    kept, excluded = _input_photos(tmp_path, tmp_path / "out")
    assert [p.name for p in kept] == ["keep.jpg"]
    assert excluded == 0


def test_marker_exclusion_still_works_for_non_png_photos(tmp_path):
    # run.json 마커 폴더 제외가 형식과 무관해야 한다 — jpg·webp 사본도 빠져야 한다.
    _touch(tmp_path / "sub" / "a.jpg")
    _touch(tmp_path / "sub" / "results" / "blue" / "copy.jpg")
    _touch(tmp_path / "sub" / "results" / "green" / "copy.webp")
    (tmp_path / "sub" / "results" / "run.json").write_text("{}", encoding="utf-8")
    kept, excluded = _input_photos(tmp_path, tmp_path / "out")
    assert [p.name for p in kept] == ["a.jpg"]
    assert excluded == 2


def test_output_folder_exclusion_still_works_for_non_png(tmp_path):
    # 출력 폴더 안 사진 제외도 형식과 무관해야 한다.
    _touch(tmp_path / "orig.jpg")
    out = tmp_path / "out"
    _touch(out / "blue" / "orig.jpg")
    kept, excluded = _input_photos(tmp_path, out)
    assert len(kept) == 1
    assert kept[0] == tmp_path / "orig.jpg"
    assert excluded == 1


def test_load_image_reads_a_jpg_without_palette_or_transparency(tmp_path):
    # loading.py 의 서술(JPG는 PIL로 그냥 읽히고 팔레트/투명 분기를 지나침)을 실제
    # 파일로 확인한다. 코드는 이미 이렇게 동작한다 — 회귀 방지용 안전망이다.
    p = tmp_path / "photo.jpg"
    arr = np.zeros((8, 8, 3), dtype=np.uint8)
    arr[..., 2] = 200  # 파란 채널만 채운다
    Image.fromarray(arr).save(p)
    loaded = load_image(p)
    assert loaded.load_error is None
    assert loaded.has_transparent_pixels is False
    assert loaded.palette_size is None
    assert loaded.width == 8 and loaded.height == 8
    assert loaded.rgb[..., 2].max() > 0  # RGB 로 읽혀 파란 채널이 살아 있다
