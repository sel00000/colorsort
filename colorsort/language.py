"""언어 선택. 메뉴를 띄우고, 고른 값을 저장하고, 다음부터 묻지 않는다.

저장 위치는 홈 디렉터리가 아니라 현재 작업 폴더다. 도구가 사용자 홈을 건드리지 않게
하고, 프로젝트별로 다른 언어를 쓸 수 있게 하기 위함이다.
"""

import sys
from pathlib import Path
from typing import TextIO

from .messages import DEFAULT_LANG, LANG_NAMES, SUPPORTED_LANGS, t

SETTINGS_FILE = Path(".colorsort-lang")


def load_saved_language(root: Path = Path(".")) -> str | None:
    """저장된 선택을 읽는다. 없거나 이상하면 None."""
    path = root / SETTINGS_FILE
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value if value in SUPPORTED_LANGS else None


def save_language(lang: str, root: Path = Path(".")) -> None:
    """선택을 저장한다. 실패해도 프로그램을 멈추지 않는다."""
    if lang not in SUPPORTED_LANGS:
        return
    try:
        (root / SETTINGS_FILE).write_text(lang, encoding="utf-8")
    except OSError:
        pass  # 저장 못 해도 이번 실행은 정상 동작해야 한다


def clear_saved_language(root: Path = Path(".")) -> None:
    """저장 파일 하나만 지운다.

    이 도구에서 무언가를 지우는 유일한 곳이다. 사진과 폴더는 어떤 경우에도 지우지 않는다.
    """
    try:
        (root / SETTINGS_FILE).unlink()
    except OSError:
        pass


def prompt_for_language(stream_in: TextIO, stream_out: TextIO) -> str:
    """번호를 골라 언어를 정하는 메뉴. 제목은 두 언어를 함께 보여준다.

    아직 어떤 언어를 쓸지 모르는 상태이므로, 메뉴 자체는 양쪽 언어를 병기한다.
    """
    options = list(SUPPORTED_LANGS)
    print("", file=stream_out)
    print(t("lang.prompt_title", DEFAULT_LANG), file=stream_out)
    print("", file=stream_out)
    for i, lang in enumerate(options, start=1):
        print(f"    {i}) {LANG_NAMES[lang]}", file=stream_out)
    print("", file=stream_out)
    stream_out.write(t("lang.prompt_enter", DEFAULT_LANG))
    stream_out.flush()

    raw = stream_in.readline().strip()
    if not raw:
        return options[0]                        # 그냥 엔터 = 첫 번째
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1]
    if raw.lower() in SUPPORTED_LANGS:            # "ko" / "en" 을 직접 쳐도 받아준다
        return raw.lower()
    return options[0]                             # 이상한 입력은 기본값으로


def resolve_language(explicit: str | None = None, reset: bool = False,
                     root: Path = Path("."),
                     stream_in: TextIO | None = None,
                     stream_out: TextIO | None = None) -> str:
    """어떤 언어로 출력할지 정한다. 우선순위는 Task 7 머리말 참조."""
    if explicit in SUPPORTED_LANGS:
        return explicit                           # 명시 지정은 저장하지 않는다

    if reset:
        clear_saved_language(root)
    else:
        saved = load_saved_language(root)
        if saved:
            return saved

    stream_in = stream_in or sys.stdin
    stream_out = stream_out or sys.stdout

    # 터미널이 아니면 묻지 않는다. 자동 실행이 프롬프트에서 멈추면 안 된다.
    if not (hasattr(stream_in, "isatty") and stream_in.isatty()):
        return DEFAULT_LANG

    chosen = prompt_for_language(stream_in, stream_out)
    save_language(chosen, root)
    print(t("lang.saved", chosen), file=stream_out)
    return chosen
