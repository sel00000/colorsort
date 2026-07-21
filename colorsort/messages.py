"""한국어·영어 문구 카탈로그. 순수 함수이며 파일 시스템을 모른다.

프로그램 어디에서도 사람이 읽는 문장을 직접 쓰지 않는다. 판정 로직은 Msg(열쇠 + 숫자)만
만들고, 실제 문장은 출력 직전에 여기서 만들어진다. 그래야 언어를 바꿀 수 있다.

두 카탈로그의 열쇠 집합은 완전히 같아야 한다. test_messages.py가 이를 강제한다.
"""

from .models import Msg

SUPPORTED_LANGS = ("ko", "en")
DEFAULT_LANG = "ko"

# 언어 선택 메뉴에 보여줄 이름. 자기 언어로 표기한다.
LANG_NAMES = {"ko": "한국어", "en": "English"}

CATALOG: dict[str, dict[str, str]] = {
    "ko": {
        # --- 판정 사유 ---
        "reason.pure_blue":
            "파랑 — 밝은 픽셀 {n_gated:,}개 중 {n_blue:,}개가 파랑 범위입니다. "
            "초록 범위는 {n_green}개입니다. 가장 밝은 값은 {peak}입니다.",
        "reason.pure_green":
            "초록 — 밝은 픽셀 {n_gated:,}개 중 {n_green:,}개가 초록 범위입니다. "
            "파랑 범위는 {n_blue}개입니다. 가장 밝은 값은 {peak}입니다.",
        "reason.mixed":
            "하이브리드 의심 — 파랑 {n_blue:,}개와 초록 {n_green:,}개가 함께 있습니다"
            "(파랑 비율 {f_blue:.3f}). 현재 데이터 형식에서는 드문 경우이므로 "
            "직접 확인해 주세요.",
        "reason.no_signal":
            "신호 없음(검출 한계 이하) — 밝기 1 이상인 픽셀이 {needed}개 필요한데 "
            "{found}개 발견했습니다. 가장 밝은 값은 {peak}입니다. "
            "파일 크기는 {file_bytes:,}바이트입니다.",
        "reason.all_intermediate":
            "밝은 픽셀 {n_gated:,}개가 모두 중간색이라 파랑/초록으로 나눌 수 없었습니다.",
        "reason.intermediate":
            "파랑도 초록도 아닌 중간색이 {percent:.1f}%입니다. 두 색이 섞인 것이 아니라 "
            "제3의 색으로 보이므로 판정하지 않았습니다.",
        "reason.transparent":
            "투명한 픽셀이 있습니다. 투명한 부분은 검정 배경과 구분할 수 없어 판정하지 "
            "않았습니다. 원본을 직접 확인해 주세요.",
        "reason.colorspace":
            "빨간색 성분이 있습니다(최대 {max_red}). 이 도구는 초록과 파랑만 있는 "
            "사진을 전제로 하므로 판정하지 않았습니다.",
        "reason.inconsistent":
            "픽셀 개수 비율({f_blue:.3f})과 밝기 비율({f_blue_energy:.3f})이 크게 "
            "어긋납니다. 이상한 입력일 수 있어 판정하지 않았습니다.",
        "reason.ambiguous":
            "애매함 — 파랑 {n_blue:,}개, 초록 {n_green:,}개(파랑 비율 {f_blue:.3f}). "
            "어느 한쪽으로 단정하기에도, 하이브리드로 보기에도 근거가 부족합니다.",
        "reason.load_error": "파일을 읽을 수 없습니다: {error}",
        "suffix.low_confidence": " 신호가 약해 신뢰도가 낮습니다.",

        # --- 경고 ---
        "warn.empty_but_large":
            "파일 크기가 {file_bytes:,}바이트로 전체 중앙값({median:,.0f}바이트)에 비해 "
            "큽니다. 픽셀은 비었는데 파일이 크므로 원본을 직접 확인해 보세요.",

        # --- 알림 ---
        "notice.excluded": "  출력 폴더 안에 있어 제외한 파일: {n}장",

        # --- 요약 출력 ---
        "summary.total": "  총 {n}장을 검사했습니다.",
        "summary.review_detail": "      (검토 내역: {detail})",
        "summary.low_confidence": "    신호가 약해 신뢰도 낮음: {n}장",
        "summary.next_step": "  실제로 복사하려면 --apply 를 붙여 다시 실행하세요.",
        "summary.originals_safe": "  원본은 어떤 경우에도 변경되지 않습니다.",
        "summary.copied": "  총 {n}장을 검사하고 {copied}장을 복사했습니다.",
        "summary.problems": "    문제 {n}건:",
        "summary.out_dir": "    결과 폴더: {path}",
        "summary.table": "    표: {path}",

        # --- 오류 ---
        "error.no_input_dir": "오류: 입력 폴더를 찾을 수 없습니다: {path}",
        "error.no_png": "오류: {path} 안에서 PNG 파일을 찾지 못했습니다.",
        "error.collision": "오류: 사본 이름이 겹칩니다. 덮어쓰지 않기 위해 중단합니다.",
        "error.collision_row": "  {dest} <- 원본 {n}개",
        "error.write_failed": "오류: 결과를 저장할 수 없습니다: {path} ({error})",
        "error.copy_exists": "이미 존재하여 건너뜀: {dest}",
        "error.copy_failed": "복사 실패 {source} -> {dest}: {error}",

        # --- 언어 메뉴 ---
        "lang.prompt_title": "  언어를 선택하세요 / Choose a language",
        "lang.prompt_enter": "  번호 입력 / Enter number [1]: ",
        "lang.saved": "  선택이 저장되었습니다. 바꾸려면 --lang 또는 --lang-reset 을 쓰세요.",

        # --- CLI 도움말 ---
        "help.description":
            "사진의 픽셀 색을 보고 파랑/초록으로 구별해 폴더로 정리합니다. "
            "파일 이름은 판정에 사용하지 않습니다.",
        "help.input": "사진이 들어있는 폴더 (하위 폴더까지 찾습니다)",
        "help.output": "결과를 넣을 폴더 (기본값: results)",
        "help.apply": "실제로 복사합니다. 붙이지 않으면 미리보기만 합니다.",
        "help.lang": "표시 언어 (ko 또는 en)",
        "help.lang_reset": "저장된 언어 선택을 지우고 다시 묻습니다.",

        # --- CSV 열 이름 ---
        "col.source": "원본경로",
        "col.dest": "사본경로",
        "col.label": "판정",
        "col.reason": "사유",
        "col.confidence": "신뢰도",
        "col.n_gated": "밝은픽셀수",
        "col.n_blue": "파랑픽셀수",
        "col.n_green": "초록픽셀수",
        "col.n_intermediate": "중간색픽셀수",
        "col.f_blue": "파랑비율",
        "col.peak": "최대밝기",
        "col.gate": "사용된게이트",
        "col.file_bytes": "파일크기",
        "col.warnings": "경고",
        "value.confidence_low": "낮음",
        "value.confidence_high": "높음",
    },
    "en": {
        # --- decision reasons ---
        "reason.pure_blue":
            "Blue — {n_blue:,} of {n_gated:,} lit pixels fall in the blue range. "
            "{n_green} fall in the green range. Peak brightness is {peak}.",
        "reason.pure_green":
            "Green — {n_green:,} of {n_gated:,} lit pixels fall in the green range. "
            "{n_blue} fall in the blue range. Peak brightness is {peak}.",
        "reason.mixed":
            "Possible hybrid — {n_blue:,} blue and {n_green:,} green pixels appear "
            "together (blue fraction {f_blue:.3f}). This is unusual for the current "
            "file format, so please check it yourself.",
        "reason.no_signal":
            "No signal (below detection floor) — needed {needed} pixels at brightness 1 "
            "or above, found {found}. Peak brightness is {peak}. "
            "File size is {file_bytes:,} bytes.",
        "reason.all_intermediate":
            "All {n_gated:,} lit pixels are intermediate colours, so they could not be "
            "split into blue and green.",
        "reason.intermediate":
            "{percent:.1f}% of pixels are neither blue nor green. This looks like a third "
            "colour rather than a mixture of two, so no verdict was given.",
        "reason.transparent":
            "This image has transparent pixels. Transparent areas cannot be told apart "
            "from a black background, so no verdict was given. Please check the original.",
        "reason.colorspace":
            "This image has a red component (max {max_red}). The tool assumes images "
            "contain only green and blue, so no verdict was given.",
        "reason.inconsistent":
            "The pixel-count fraction ({f_blue:.3f}) and the brightness fraction "
            "({f_blue_energy:.3f}) disagree sharply. This may be an unusual input, "
            "so no verdict was given.",
        "reason.ambiguous":
            "Ambiguous — {n_blue:,} blue and {n_green:,} green pixels (blue fraction "
            "{f_blue:.3f}). Not enough evidence to call it either one colour or a hybrid.",
        "reason.load_error": "Could not read the file: {error}",
        "suffix.low_confidence": " Signal is weak, so confidence is low.",

        # --- warnings ---
        "warn.empty_but_large":
            "File size is {file_bytes:,} bytes, large compared with the overall median "
            "({median:,.0f} bytes). The pixels are empty but the file is big, so please "
            "check the original.",

        # --- notices ---
        "notice.excluded": "  Excluded {n} file(s) inside the output folder.",

        # --- summary output ---
        "summary.total": "  Checked {n} images.",
        "summary.review_detail": "      (review breakdown: {detail})",
        "summary.low_confidence": "    Low confidence due to weak signal: {n}",
        "summary.next_step": "  To actually copy the files, run again with --apply.",
        "summary.originals_safe": "  Originals are never modified.",
        "summary.copied": "  Checked {n} images, copied {copied}.",
        "summary.problems": "    {n} problem(s):",
        "summary.out_dir": "    Output folder: {path}",
        "summary.table": "    Table: {path}",

        # --- errors ---
        "error.no_input_dir": "Error: input folder not found: {path}",
        "error.no_png": "Error: no PNG files found in {path}.",
        "error.collision": "Error: copy names collide. Stopping so nothing is overwritten.",
        "error.collision_row": "  {dest} <- {n} source file(s)",
        "error.write_failed": "Error: could not write the results: {path} ({error})",
        "error.copy_exists": "Already exists, skipped: {dest}",
        "error.copy_failed": "Copy failed {source} -> {dest}: {error}",

        # --- language menu ---
        "lang.prompt_title": "  언어를 선택하세요 / Choose a language",
        "lang.prompt_enter": "  번호 입력 / Enter number [1]: ",
        "lang.saved": "  Saved. Use --lang or --lang-reset to change it.",

        # --- CLI help ---
        "help.description":
            "Sorts photos into blue and green by pixel colour. "
            "Filenames are never used to decide.",
        "help.input": "Folder containing the photos (searched recursively)",
        "help.output": "Folder to write results into (default: results)",
        "help.apply": "Actually copy the files. Without it, preview only.",
        "help.lang": "Display language (ko or en)",
        "help.lang_reset": "Clear the saved language choice and ask again.",

        # --- CSV columns ---
        "col.source": "source_path",
        "col.dest": "copy_path",
        "col.label": "verdict",
        "col.reason": "reason",
        "col.confidence": "confidence",
        "col.n_gated": "lit_pixels",
        "col.n_blue": "blue_pixels",
        "col.n_green": "green_pixels",
        "col.n_intermediate": "intermediate_pixels",
        "col.f_blue": "blue_fraction",
        "col.peak": "peak_brightness",
        "col.gate": "gate_used",
        "col.file_bytes": "file_bytes",
        "col.warnings": "warnings",
        "value.confidence_low": "low",
        "value.confidence_high": "high",
    },
}

# CSV 열 순서. 열쇠 목록이므로 언어와 무관하다.
CSV_COLUMNS = (
    "col.source", "col.dest", "col.label", "col.reason", "col.confidence",
    "col.n_gated", "col.n_blue", "col.n_green", "col.n_intermediate",
    "col.f_blue", "col.peak", "col.gate", "col.file_bytes", "col.warnings",
)


def t(key: str, lang: str = DEFAULT_LANG, **params: object) -> str:
    """열쇠와 인자로 문장을 만든다. 없는 열쇠는 조용히 넘기지 않고 열쇠 자체를 돌려준다."""
    table = CATALOG.get(lang) or CATALOG[DEFAULT_LANG]
    template = table.get(key)
    if template is None:
        template = CATALOG[DEFAULT_LANG].get(key)
    if template is None:
        return key  # 누락을 눈에 띄게 남긴다. 테스트가 이런 상황을 먼저 잡는다.
    try:
        return template.format(**params)
    except (KeyError, IndexError, ValueError):
        return template


def render(msg: Msg, lang: str = DEFAULT_LANG) -> str:
    """Msg 하나를 선택된 언어의 문장으로 만든다."""
    return t(msg.key, lang, **dict(msg.params))
