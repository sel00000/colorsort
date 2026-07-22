"""(판정, 이유) → 출력 하위 폴더. 영문 고정 — 언어를 따라가지 않는다(v1 원칙 유지)."""

def dest_subfolder(label: str, reason_code: str) -> str:
    if label == "BLUE":
        return "blue"
    if label == "GREEN":
        return "green"
    if label == "HYBRID":
        return "review/mixed"
    if reason_code == "no_signal":
        return "review/no-signal"
    return "review/other"

def review_group(label: str, reason_code: str) -> str | None:
    sub = dest_subfolder(label, reason_code)
    return sub.split("/", 1)[1] if sub.startswith("review/") else None
