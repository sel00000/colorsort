import hashlib
from pathlib import Path
from colorsortgui.fingerprint import file_fingerprint

def test_same_bytes_same_fp(tmp_path):
    a = tmp_path / "a.png"; a.write_bytes(b"\x89PNG demo")
    b = tmp_path / "sub"; b.mkdir()
    c = b / "renamed.png"; c.write_bytes(b"\x89PNG demo")
    assert file_fingerprint(a) == file_fingerprint(c)          # 이름·위치 무관

def test_diff_bytes_diff_fp(tmp_path):
    a = tmp_path / "a"; a.write_bytes(b"one")
    b = tmp_path / "b"; b.write_bytes(b"two")
    assert file_fingerprint(a) != file_fingerprint(b)

def test_is_sha256_hex(tmp_path):
    a = tmp_path / "a"; a.write_bytes(b"x")
    fp = file_fingerprint(a)
    assert fp == hashlib.sha256(b"x").hexdigest() and len(fp) == 64
