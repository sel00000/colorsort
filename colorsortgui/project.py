"""GUI가 부르는 유일한 창구. v1 판정 파이프라인을 그대로 쓰고 사람 결정을 겹친다."""
import csv
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from colorsort.cli import run as v1_run
from colorsort.config import DEFAULT_CONFIG
from colorsort.models import CopyItem, FileResult, Msg
from colorsort.report import write_copy_log, write_results_csv, write_run_json
from colorsort.sorting import _dest_name, execute_copies, find_collisions

from .decisions import DecisionStore
from .fingerprint import file_fingerprint
from .foldering import dest_subfolder, review_group

@dataclass
class PhotoItem:
    path: Path
    rel: str
    fp: str
    result: FileResult
    machine_sub: str
    human: str | None

    @property
    def effective_sub(self) -> str:
        if self.human == "BLUE":
            return "blue"
        if self.human == "GREEN":
            return "green"
        return self.machine_sub

    @property
    def dest_name(self) -> str:
        return _dest_name(self.path, self._input_root)

    @property
    def dest(self) -> str:
        return f"{self.effective_sub}/{self.dest_name}"

    _input_root: Path = field(default=Path("."), repr=False)

@dataclass
class ProjectState:
    input_root: Path
    output_root: Path
    items: list[PhotoItem]
    store: DecisionStore
    n_excluded: int
    undo_stack: list = field(default_factory=list)

    def counts(self) -> dict:
        c = {"all": len(self.items), "blue": 0, "green": 0, "review": 0,
             "no-signal": 0, "mixed": 0, "other": 0}
        for i in self.items:
            sub = i.effective_sub
            if sub == "blue":
                c["blue"] += 1
            elif sub == "green":
                c["green"] += 1
            else:
                c["review"] += 1
                c[sub.split("/", 1)[1]] += 1
        return c

def open_project(input_root: Path, output_root: Path) -> ProjectState:
    input_root = Path(input_root)
    output_root = Path(output_root)
    results, _items, n_excluded = v1_run(input_root, output_root, DEFAULT_CONFIG, False)
    store = DecisionStore(output_root / "decisions.json")
    items = []
    for r in results:
        fp = file_fingerprint(r.path)
        item = PhotoItem(
            path=r.path,
            rel=r.path.relative_to(input_root).as_posix(),
            fp=fp,
            result=r,
            machine_sub=dest_subfolder(r.decision.label, r.decision.reason_code),
            human=store.get(fp),
        )
        item._input_root = input_root
        items.append(item)
    return ProjectState(input_root, output_root, items, store, n_excluded)

def _copy_items(state: ProjectState) -> list[CopyItem]:
    return [CopyItem(source=i.path, dest=state.output_root / i.dest, label=i.result.decision.label)
            for i in state.items]

def apply_copies(state: ProjectState) -> tuple[int, list[Msg]]:
    items = _copy_items(state)
    collisions = find_collisions(items)
    if collisions:
        return 0, [Msg("error.collision_row", {"dest": d, "n": len(s)}) for d, s in collisions[:10]]
    write_results_csv([i.result for i in state.items], items,
                      state.output_root / "results.csv", "en")
    write_run_json(state.output_root / "run.json", DEFAULT_CONFIG,
                   len(state.items), True, "en")
    copied, errors = execute_copies(items)
    failed = {e.params.get("dest") for e in errors}
    write_copy_log([i for i in items if i.dest not in failed],
                   state.output_root / "copy-log.csv")
    return copied, [e for e in errors if e.key == "error.copy_failed"]

def _append_move_log(state: ProjectState, item: PhotoItem, src: str, dst: str) -> None:
    path = state.output_root / "moves-log.csv"
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "file", "fingerprint", "from", "to"])
        w.writerow([datetime.now().isoformat(timespec="seconds"),
                    item.dest_name, item.fp, src, dst])

def _move_copy(state: ProjectState, item: PhotoItem, old_sub: str, new_sub: str) -> None:
    src = state.output_root / old_sub / item.dest_name
    dst = state.output_root / new_sub / item.dest_name
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.move(str(src), str(dst))

def set_human(state: ProjectState, item: PhotoItem, label: str) -> None:
    old_sub, old_human = item.effective_sub, item.human
    state.store.set(item.fp, label, item.path.name)
    item.human = label
    _move_copy(state, item, old_sub, item.effective_sub)
    _append_move_log(state, item, old_sub, item.effective_sub)
    state.undo_stack.append((item.fp, old_human))

def undo(state: ProjectState):
    if not state.undo_stack:
        return None
    fp, old_human = state.undo_stack.pop()
    item = next(i for i in state.items if i.fp == fp)
    cur_sub = item.effective_sub
    if old_human is None:
        state.store.remove(fp)
    else:
        state.store.set(fp, old_human, item.path.name)
    item.human = old_human
    _move_copy(state, item, cur_sub, item.effective_sub)
    _append_move_log(state, item, cur_sub, item.effective_sub)
    return item
