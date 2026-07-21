"""복사 계획 수립과 실행.

plan_copies와 find_collisions는 순수 함수다. 파일 시스템을 건드리지 않으므로
실제 파일 없이 테스트할 수 있다. execute_copies만 부작용을 가진다.

원본은 절대 수정하지 않는다. shutil.copy2만 쓰고 이동·삭제는 하지 않는다.
"""

import shutil
from collections import defaultdict
from pathlib import Path

from .config import Config
from .models import CopyItem, FileResult, Msg


def _dest_name(source: Path, input_root: Path) -> str:
    """출처 폴더를 접두어로 붙여 이름 충돌을 없앤다.

    A/L picture/11-blue.png -> "A__L picture__11-blue.png"
    서로 다른 폴더의 같은 이름 파일이 덮어써지는 것을 막는다.
    """
    try:
        rel = source.relative_to(input_root)
    except ValueError:
        return source.name
    parts = rel.parts[:-1]
    if not parts:
        return source.name
    return "__".join(parts) + "__" + source.name


def plan_copies(results: list[FileResult], input_root: Path, output_root: Path,
                config: Config) -> list[CopyItem]:
    """어떤 파일이 어디로 갈지의 목록을 만든다. 파일을 건드리지 않는다.

    폴더 이름은 Config에서 온다. 언어를 따라 바뀌지 않는다 — 언어를 바꿔 다시 돌리면
    폴더가 둘로 갈라져 결과가 쪼개지기 때문이다.
    """
    input_root = Path(input_root)
    output_root = Path(output_root)
    items = []
    for r in results:
        dest = output_root / r.decision.folder(config) / _dest_name(r.path, input_root)
        items.append(CopyItem(source=r.path, dest=dest, label=r.decision.label))
    return items


def find_collisions(items: list[CopyItem]) -> list[tuple[Path, list[Path]]]:
    """같은 목적지로 가는 원본이 둘 이상인 경우를 찾는다."""
    grouped: dict[Path, list[Path]] = defaultdict(list)
    for item in items:
        grouped[item.dest].append(item.source)
    return [(dest, sources) for dest, sources in grouped.items() if len(sources) > 1]


def execute_copies(items: list[CopyItem]) -> tuple[int, list[Msg]]:
    """실제로 복사한다. 이미 있는 파일은 덮어쓰지 않고 오류로 보고한다.

    반환: (성공 개수, 오류 메시지 목록)
    """
    copied = 0
    errors: list[Msg] = []
    for item in items:
        try:
            item.dest.parent.mkdir(parents=True, exist_ok=True)
            if item.dest.exists():
                errors.append(Msg("error.copy_exists", {"dest": item.dest}))
                continue
            shutil.copy2(item.source, item.dest)
            copied += 1
        except OSError as exc:
            errors.append(Msg("error.copy_failed",
                              {"source": item.source, "dest": item.dest, "error": str(exc)}))
    return copied, errors
