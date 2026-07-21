import io

from colorsort.language import (
    SETTINGS_FILE, clear_saved_language, load_saved_language,
    prompt_for_language, resolve_language, save_language,
)


class _Tty(io.StringIO):
    """터미널인 척하는 입력 스트림."""

    def isatty(self) -> bool:
        return True


def test_saves_and_loads(tmp_path):
    save_language("en", tmp_path)
    assert load_saved_language(tmp_path) == "en"
    assert (tmp_path / SETTINGS_FILE).read_text(encoding="utf-8") == "en"


def test_load_returns_none_when_nothing_saved(tmp_path):
    assert load_saved_language(tmp_path) is None


def test_load_rejects_garbage(tmp_path):
    (tmp_path / SETTINGS_FILE).write_text("klingon", encoding="utf-8")
    assert load_saved_language(tmp_path) is None


def test_save_rejects_unsupported_language(tmp_path):
    save_language("klingon", tmp_path)
    assert load_saved_language(tmp_path) is None


def test_clear_removes_the_saved_choice(tmp_path):
    save_language("en", tmp_path)
    clear_saved_language(tmp_path)
    assert load_saved_language(tmp_path) is None
    assert not (tmp_path / SETTINGS_FILE).exists()


def test_clear_is_quiet_when_there_is_nothing_to_clear(tmp_path):
    clear_saved_language(tmp_path)  # 예외를 던지면 안 된다


def test_menu_lists_both_languages():
    out = io.StringIO()
    prompt_for_language(_Tty("1\n"), out)
    text = out.getvalue()
    assert "한국어" in text
    assert "English" in text
    assert "1)" in text and "2)" in text


def test_menu_choice_by_number():
    assert prompt_for_language(_Tty("2\n"), io.StringIO()) == "en"
    assert prompt_for_language(_Tty("1\n"), io.StringIO()) == "ko"


def test_menu_bare_enter_takes_the_first_option():
    assert prompt_for_language(_Tty("\n"), io.StringIO()) == "ko"


def test_menu_accepts_the_code_directly():
    assert prompt_for_language(_Tty("en\n"), io.StringIO()) == "en"


def test_menu_falls_back_on_nonsense():
    assert prompt_for_language(_Tty("99\n"), io.StringIO()) == "ko"


def test_explicit_flag_wins_and_is_not_saved(tmp_path):
    save_language("ko", tmp_path)
    assert resolve_language(explicit="en", root=tmp_path) == "en"
    assert load_saved_language(tmp_path) == "ko", "명시 지정은 저장을 덮지 않는다"


def test_saved_choice_is_used_without_prompting(tmp_path):
    save_language("en", tmp_path)
    out = io.StringIO()
    assert resolve_language(root=tmp_path, stream_in=_Tty(""), stream_out=out) == "en"
    assert out.getvalue() == "", "저장된 값이 있으면 묻지 않는다"


def test_prompts_and_saves_on_first_run(tmp_path):
    out = io.StringIO()
    lang = resolve_language(root=tmp_path, stream_in=_Tty("2\n"), stream_out=out)
    assert lang == "en"
    assert load_saved_language(tmp_path) == "en"
    assert "English" in out.getvalue()


def test_reset_clears_and_asks_again(tmp_path):
    save_language("en", tmp_path)
    lang = resolve_language(reset=True, root=tmp_path,
                            stream_in=_Tty("1\n"), stream_out=io.StringIO())
    assert lang == "ko"
    assert load_saved_language(tmp_path) == "ko"


def test_non_interactive_never_prompts(tmp_path):
    """자동 실행이 프롬프트에서 멈추면 안 된다."""
    out = io.StringIO()
    lang = resolve_language(root=tmp_path,
                            stream_in=io.StringIO(""),   # isatty() == False
                            stream_out=out)
    assert lang == "ko"
    assert out.getvalue() == ""
    assert load_saved_language(tmp_path) is None, "묻지 않았으니 저장도 하지 않는다"


def test_explicit_flag_does_not_touch_the_disk(tmp_path):
    """--lang 을 주면 저장 파일을 읽지도 쓰지도 않는다.

    자동 실행이 작업 폴더에 흔적을 남기면 안 되고, 저장 파일을 못 읽는 환경에서도
    --lang 은 항상 통해야 한다.
    """
    assert resolve_language(explicit="en", root=tmp_path) == "en"
    assert not (tmp_path / SETTINGS_FILE).exists()


def test_unsupported_explicit_value_falls_through_to_the_saved_choice(tmp_path):
    save_language("en", tmp_path)
    assert resolve_language(explicit="klingon", root=tmp_path) == "en"


def test_non_interactive_reset_clears_without_asking(tmp_path):
    """--lang-reset 을 자동 실행에서 써도 멈추지 않는다."""
    save_language("en", tmp_path)
    lang = resolve_language(reset=True, root=tmp_path,
                            stream_in=io.StringIO(""), stream_out=io.StringIO())
    assert lang == "ko"
    assert load_saved_language(tmp_path) is None, "지우기만 하고 새로 저장하지 않는다"
