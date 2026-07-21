"""결과 출력. CSV, 복사 기록, 실행 이력, 사람이 읽는 요약."""

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from . import RULES_VERSION, __version__
from .config import Config
from .messages import CSV_COLUMNS, DEFAULT_LANG, render, t
from .models import CopyItem, FileResult

# 엑셀이 한글을 제대로 열려면 BOM이 필요하다.
_ENCODING = "utf-8-sig"


def write_results_csv(results: list[FileResult], items: list[CopyItem], path: Path,
                      lang: str = DEFAULT_LANG) -> None:
    """파일당 한 줄. 나중에 왜 그렇게 분류됐는지 추적할 수 있어야 한다.

    열 이름과 사유는 선택된 언어로 나간다. 판정 값(BLUE/GREEN/...)은 기계용이므로
    번역하지 않는다 — 집계와 비교에 쓰이기 때문이다.
    """
    dest_by_source = {item.source: item.dest for item in items}
    headers = [t(key, lang) for key in CSV_COLUMNS]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=_ENCODING, newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        for r in results:
            m, d = r.measurements, r.decision
            writer.writerow([
                str(r.path),
                str(dest_by_source.get(r.path, "")),
                d.label,                                   # 번역하지 않는다
                render(d.reason, lang),
                t("value.confidence_low" if d.low_confidence else "value.confidence_high", lang),
                m.n_gated,
                m.n_blue,
                m.n_green,
                m.n_intermediate,
                f"{m.f_blue:.4f}",
                m.peak,
                m.gate_used if m.gate_used is not None else "",
                m.file_bytes,
                " | ".join(render(w, lang) for w in d.warnings),
            ])


def write_copy_log(items: list[CopyItem], path: Path) -> None:
    """되돌리기용 기록. 어떤 원본이 어디로 복사됐는지 전부 남긴다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=_ENCODING, newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["원본경로", "사본경로", "판정"])
        writer.writeheader()
        for item in items:
            writer.writerow({
                "원본경로": str(item.source),
                "사본경로": str(item.dest),
                "판정": item.label,
            })


def write_run_json(path: Path, config: Config, n_files: int, applied: bool,
                   lang: str = DEFAULT_LANG) -> None:
    """실행 이력. 몇 달 뒤 같은 결과를 재현하려면 이 정보가 필요하다.

    이 파일의 열쇠는 기계가 읽는 것이므로 번역하지 않는다. 선택된 언어는 값으로 기록한다.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "도구버전": __version__,
        "규칙버전": RULES_VERSION,
        "실행시각": datetime.now().isoformat(timespec="seconds"),
        "표시언어": lang,
        "파일수": n_files,
        "복사요청여부": applied,
        "폴더이름": {
            "blue": config.folder_blue,
            "green": config.folder_green,
            "review": config.folder_review,
        },
        "설정": {
            "rho_blue": config.rho_blue,
            "rho_green": config.rho_green,
            "gates": list(config.gates),
            "n_min": config.n_min,
            "minority_floor": config.minority_floor,
            "max_intermediate_frac": config.max_intermediate_frac,
            "purity_eps": config.purity_eps,
            "consistency_max": config.consistency_max,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize(results: list[FileResult], config: Config,
              lang: str = DEFAULT_LANG) -> str:
    """사람이 읽는 요약. 미리보기에서 그대로 보여준다."""
    folders = Counter(r.decision.folder(config) for r in results)
    review = config.folder_review
    reasons = Counter(r.decision.reason_code for r in results
                      if r.decision.folder(config) == review)
    low = sum(1 for r in results if r.decision.low_confidence
              and r.decision.folder(config) != review)

    lines = [t("summary.total", lang, n=len(results)), ""]
    for name in (config.folder_blue, config.folder_green, review):
        lines.append(f"    {name + '/':14s} {folders.get(name, 0):4d}")

    if reasons:
        detail = ", ".join(f"{code} {n}" for code, n in sorted(reasons.items()))
        lines.append(t("summary.review_detail", lang, detail=detail))
    if low:
        lines.append(t("summary.low_confidence", lang, n=low))

    lines += [
        "",
        t("summary.next_step", lang),
        t("summary.originals_safe", lang),
    ]
    return "\n".join(lines)
