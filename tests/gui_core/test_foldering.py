import pytest
from colorsortgui.foldering import dest_subfolder, review_group

@pytest.mark.parametrize("label,reason,sub,group", [
    ("BLUE", "pure_blue", "blue", None),
    ("GREEN", "pure_green", "green", None),
    ("HYBRID", "mixed", "review/mixed", "mixed"),
    ("ABSTAIN", "no_signal", "review/no-signal", "no-signal"),
    ("ABSTAIN", "transparent", "review/other", "other"),
    ("ABSTAIN", "colorspace", "review/other", "other"),
    ("ABSTAIN", "intermediate", "review/other", "other"),
    ("ABSTAIN", "all_intermediate", "review/other", "other"),
    ("ABSTAIN", "inconsistent", "review/other", "other"),
    ("ABSTAIN", "ambiguous", "review/other", "other"),
    ("ABSTAIN", "unreadable", "review/other", "other"),   # 읽기 실패도 사람 검토
])
def test_map(label, reason, sub, group):
    assert dest_subfolder(label, reason) == sub
    assert review_group(label, reason) == group
