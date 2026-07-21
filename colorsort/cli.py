"""명령줄 인터페이스. 파싱하고 호출하고 출력만 한다. 판정 로직을 넣지 않는다."""

import argparse
import sys
from pathlib import Path

from .config import DEFAULT_CONFIG, Config
from .language import resolve_language
from .loading import load_image
from .measure import measure
from .messages import SUPPORTED_LANGS, render, t
from .models import CopyItem, Decision, FileResult
from .report import summarize, write_copy_log, write_results_csv, write_run_json
from .rules import crosscheck_file_sizes, decide
from .sorting import execute_copies, find_collisions, plan_copies


def _input_pngs(input_root: Path, output_root: Path) -> tuple[list[Path], int]:
    """훑을 PNG 목록과, 출력 폴더 안이라 제외한 개수.

    README 는 입력 '.' 에 --output results 를 권하므로 출력 폴더가 입력 폴더 안에
    있는 것이 보통이다. 걸러내지 않으면 한 번 --apply 한 뒤의 재실행이 자기 사본을
    원본으로 세어 196 -> 392 -> 784 로 불어난다.

    제외한 개수도 함께 돌려준다. --output 이 이미 사진이 들어있는 폴더를 가리키면
    원본이 말없이 빠지므로, 몇 장이 빠졌는지 반드시 알려야 하기 때문이다.

    출력 폴더가 입력 폴더 밖이면 걸리는 것이 없으므로 동작이 달라지지 않는다.
    """
    out_resolved = output_root.resolve()
    found = sorted(p for p in input_root.rglob("*.png") if p.is_file())
    kept = [p for p in found if out_resolved not in p.resolve().parents]
    return kept, len(found) - len(kept)


def run(input_root: Path, output_root: Path, config: Config,
        apply: bool) -> tuple[list[FileResult], list[CopyItem], int]:
    """전체 파이프라인. 파일명은 판정에 사용하지 않는다.

    언어를 전혀 모르는 채로 동작한다. 문장은 출력 단계에서만 만들어진다.

    복사는 하지 않는다. apply 는 받아만 두고 쓰지 않으며, 실제 복사는 main 이
    execute_copies 로 한다. 반환값은 (판정 결과, 복사 계획, 제외한 파일 수) 다.
    """
    paths, n_excluded = _input_pngs(input_root, output_root)

    results: list[FileResult] = []
    for path in paths:
        loaded = load_image(path)
        # 읽기에 실패해도 measure 는 통과시킨다. 빈 배열 가드가 있어 안전하고,
        # 그래야 파일 크기 같은 값이 표에 남는다.
        m = measure(loaded, config)
        if loaded.load_error:
            # load_error 는 이미 Msg 다. 다시 Msg 로 감싸면 문장 대신 객체가 찍힌다.
            results.append(FileResult(path, m, Decision("ABSTAIN", loaded.load_error, True)))
            continue
        results.append(FileResult(path, m, decide(m, config)))

    results = crosscheck_file_sizes(results, config)
    items = plan_copies(results, input_root, output_root, config)
    return results, items, n_excluded


def _build_parser(lang: str) -> argparse.ArgumentParser:
    """도움말도 선택된 언어로 나온다."""
    parser = argparse.ArgumentParser(prog="colorsort", description=t("help.description", lang))
    parser.add_argument("input", type=Path, help=t("help.input", lang))
    parser.add_argument("--output", type=Path, default=Path("results"),
                        help=t("help.output", lang))
    parser.add_argument("--apply", action="store_true", help=t("help.apply", lang))
    parser.add_argument("--lang", choices=SUPPORTED_LANGS, help=t("help.lang", lang))
    parser.add_argument("--lang-reset", action="store_true", help=t("help.lang_reset", lang))
    return parser


def _preparse_lang(argv: list[str] | None) -> tuple[str | None, bool]:
    """도움말을 만들기 전에 언어부터 알아야 하므로 --lang 만 먼저 훑는다."""
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--lang", choices=SUPPORTED_LANGS)
    pre.add_argument("--lang-reset", action="store_true")
    known, _ = pre.parse_known_args(argv)
    return known.lang, known.lang_reset


def main(argv: list[str] | None = None) -> int:
    explicit, reset = _preparse_lang(argv)
    lang = resolve_language(explicit=explicit, reset=reset)

    parser = _build_parser(lang)
    args = parser.parse_args(argv)

    input_root: Path = args.input
    output_root: Path = args.output
    config = DEFAULT_CONFIG

    if not input_root.is_dir():
        print(t("error.no_input_dir", lang, path=input_root), file=sys.stderr)
        return 1

    results, items, n_excluded = run(input_root, output_root, config, args.apply)

    if n_excluded:
        print(t("notice.excluded", lang, n=n_excluded))

    if not results:
        # 전부 출력 폴더 안이라 빠진 것이라면 '없다'고 하지 않는다. 파일은 분명히
        # 있고, 위의 알림이 무슨 일이 일어났는지 이미 사실대로 말한다.
        if not n_excluded:
            print(t("error.no_png", lang, path=input_root), file=sys.stderr)
        return 1

    collisions = find_collisions(items)
    if collisions:
        print(t("error.collision", lang), file=sys.stderr)
        for dest, sources in collisions[:10]:
            print(t("error.collision_row", lang, dest=dest, n=len(sources)), file=sys.stderr)
        return 1

    # 미리보기에서도 사본 경로를 채운다. 어디로 갈지 보려고 미리보기를 하는 것이므로
    # 그 칸이 비어 있으면 미리보기의 목적이 사라진다.
    write_results_csv(results, items, output_root / "results.csv", lang)
    write_run_json(output_root / "run.json", config, len(results), args.apply, lang)

    print()
    exit_code = 0
    if args.apply:
        # 보고하기 전에 먼저 복사한다. 순서가 반대면 하지도 않은 복사를 알리게 된다.
        copied, errors = execute_copies(items)
        # 실제로 만들어진 사본만 기록한다. 되돌리기용 기록이므로, 하지 않은 복사가
        # 적혀 있으면 그것을 보고 되돌리는 사용자가 자기 파일을 지우게 된다.
        failed = {e.params["dest"] for e in errors}
        write_copy_log([i for i in items if i.dest not in failed],
                       output_root / "copy-log.csv")
        print(t("summary.copied", lang, n=len(results), copied=copied))
        if errors:
            print(t("summary.problems", lang, n=len(errors)), file=sys.stderr)
            for e in errors[:10]:
                # execute_copies 는 Msg 를 돌려준다. 렌더링하지 않으면 객체가 찍힌다.
                print(f"      {render(e, lang)}", file=sys.stderr)
            # 이미 있어 건너뛴 것은 실패가 아니다. 같은 명령의 재실행은 성공이어야 한다.
            if any(e.key == "error.copy_failed" for e in errors):
                exit_code = 1
        print(t("summary.out_dir", lang, path=output_root))
    else:
        print(summarize(results, config, lang))

    print(t("summary.table", lang, path=output_root / "results.csv"))
    print()
    return exit_code
