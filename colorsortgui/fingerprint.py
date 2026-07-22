"""파일 내용 지문. 이름·위치·드라이브 문자가 바뀌어도 같은 사진을 알아보는 열쇠."""
import hashlib
from pathlib import Path

def file_fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
