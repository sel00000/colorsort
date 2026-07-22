import importlib
import os
import sys
import types

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication


# ==================== 통합 때 삭제 (START) ====================
# A 계층 스텁 주입. B 워크트리에는 A 코드(enhance/i18n/project/thumbcache)가 없으므로
# 인터페이스 계약과 동일한 시그니처의 미니 구현을 sys.modules로 주입한다.
# enhance/i18n은 순수 데이터 함수라 계약의 A4/A6 코드를 그대로 복사했다.
# Workstream C(C1)에서 "통합 때 삭제" 표식을 검색해 이 블록을 통째로 제거하고 실물로 연결한다.

def _install_stub(name: str, source: str) -> types.ModuleType:  # 통합 때 삭제
    mod = types.ModuleType(name)
    mod.__file__ = f"<stub {name}>"
    exec(compile(source, f"<stub {name}>", "exec"), mod.__dict__)
    sys.modules[name] = mod
    pkg_name, _, child = name.rpartition(".")
    if pkg_name:
        try:
            setattr(importlib.import_module(pkg_name), child, mod)
        except Exception:
            pass
    return mod


# 계약 A4 (colorsortgui/enhance.py) 그대로.
_ENHANCE_SRC = '''\
"""화면 표시 전용 변환. 판정에는 절대 닿지 않는다."""
import numpy as np

AUTO_GAMMA = 0.35
JUDGE_BLUE = (43, 109, 229)
JUDGE_GREEN = (52, 168, 107)
JUDGE_INTER = (128, 128, 128)

def peak_of(rgb) -> int:
    if rgb.size == 0:
        return 0
    return int(np.maximum(rgb[..., 1], rgb[..., 2]).max())

def auto_gain(rgb) -> float:
    peak = peak_of(rgb)
    return 255.0 / peak if peak > 0 else 1.0

def manual_view(rgb, gain: float, gamma: float) -> np.ndarray:
    g = rgb[..., 1].astype(np.float64)
    b = rgb[..., 2].astype(np.float64)
    inten = np.maximum(g, b)
    out = np.zeros(rgb.shape[:2] + (3,), dtype=np.uint8)
    if inten.max() <= 0:
        return out
    x = np.clip(inten * gain / 255.0, 0.0, 1.0)
    disp = 255.0 * np.power(x, gamma)
    scale = np.divide(disp, inten, out=np.zeros_like(disp), where=inten > 0)
    out[..., 1] = np.clip(g * scale, 0, 255).astype(np.uint8)
    out[..., 2] = np.clip(b * scale, 0, 255).astype(np.uint8)
    return out

def auto_view(rgb) -> np.ndarray:
    return manual_view(rgb, auto_gain(rgb), AUTO_GAMMA)

def judgment_masks(rgb, config):
    g = rgb[..., 1]
    b = rgb[..., 2]
    inten = np.maximum(g, b)
    gate_used, mask = None, None
    for gate in config.gates:
        candidate = inten >= gate
        if int(candidate.sum()) >= config.n_min:
            gate_used, mask = gate, candidate
            break
    shape = inten.shape
    if gate_used is None:
        empty = np.zeros(shape, dtype=bool)
        return empty, empty, empty, None
    denom = (g + b).astype(np.float64)
    rho = np.divide(b, denom, out=np.zeros_like(denom), where=denom > 0)
    mask_blue = mask & (rho >= config.rho_blue)
    mask_green = mask & (rho <= config.rho_green)
    mask_inter = mask & ~mask_blue & ~mask_green
    return mask_blue, mask_green, mask_inter, gate_used

def judgment_view(rgb, config) -> np.ndarray:
    mb, mg, mi, _ = judgment_masks(rgb, config)
    out = np.zeros(rgb.shape[:2] + (3,), dtype=np.uint8)
    out[mb] = JUDGE_BLUE
    out[mg] = JUDGE_GREEN
    out[mi] = JUDGE_INTER
    return out

def channel_view(rgb, channel: str) -> np.ndarray:
    idx = 1 if channel == "green" else 2
    ch = rgb[..., idx].astype(np.float64)
    out = np.zeros(rgb.shape[:2] + (3,), dtype=np.uint8)
    peak = ch.max()
    if peak <= 0:
        return out
    disp = 255.0 * np.power(np.clip(ch / peak, 0.0, 1.0), AUTO_GAMMA)
    out[..., idx] = disp.astype(np.uint8)
    return out

def probe(rgb, x: int, y: int):
    g = int(rgb[y, x, 1]); b = int(rgb[y, x, 2])
    rho = b / (g + b) if (g + b) > 0 else 0.0
    return g, b, round(rho, 4)
'''

# 계약 A6 (colorsortgui/i18n.py) 그대로.
_I18N_SRC = '''\
"""GUI 문자열. v1 messages.py는 건드리지 않고 GUI만의 표를 따로 둔다. 기본 English."""
LANGS = ("en", "ko")
DEFAULT_LANG = "en"

T = {
 "en": {
  "app.title": "Colorsort",
  "nav.library": "Library", "nav.review": "Review", "nav.log": "Log",
  "nav.settings": "Settings", "nav.language": "Language",
  "btn.choose_folder": "Choose folder", "btn.sort": "Sort photos",
  "btn.apply": "Copy into folders", "btn.to_blue": "To Blue", "btn.to_green": "To Green",
  "btn.undo": "Undo", "btn.save_png": "Save corrected PNG", "btn.auto": "Auto",
  "btn.back": "Back",
  "tab.all": "All", "tab.blue": "Blue", "tab.green": "Green", "tab.review": "Review",
  "group.no-signal": "No signal", "group.mixed": "Blue+green", "group.other": "Other",
  "stat.scanned": "Scanned", "stat.blue": "Blue", "stat.green": "Green", "stat.review": "Review",
  "badge.human": "confirmed by you",
  "insp.title": "Inspector", "insp.peak": "Peak brightness", "insp.view": "View",
  "insp.lit": "Lit pixels", "insp.blue_share": "Blue share", "insp.reason": "Reason",
  "insp.auto_view": "\\u03b3 {gamma} \\u00b7 \\u00d7{gain} normalized",
  "view.original": "Original", "view.corrected": "Corrected", "view.judgment": "Judgment",
  "view.green_only": "Green only", "view.blue_only": "Blue only",
  "slider.brightness": "Brightness", "slider.gamma": "Gamma",
  "probe.line": "x {x}  y {y}   G {g}  B {b}  \\u03c1 {rho}",
  "msg.pick_or_drop": "Choose a photo folder, or drop one here.",
  "msg.progress": "Sorting\\u2026 {done} / {total}",
  "msg.done": "All done \\u2014 {total} photos sorted. {review} need your eyes.",
  "msg.excluded": "Skipped {n} files already inside the output folder.",
  "msg.no_signal": "No signal \\u2014 nothing to enhance.",
  "msg.moved": "Moved to {folder}.", "msg.undone": "Move undone.",
  "msg.saved_png": "Saved: {name}", "msg.copied": "Copied {copied} of {total} photos.",
  "lang.title": "Language", "lang.prompt": "Choose your language. You can change it later in Settings.",
  "err.no_folder": "That folder does not exist.",
  "err.no_png": "No PNG photos found in this folder.",
  "err.write_failed": "Could not write to {path}. Close files opened from it and try again.",
  "log.title": "Moves you made", "log.empty": "No moves yet.",
 },
 "ko": {
  "app.title": "Colorsort",
  "nav.library": "\\ub77c\\uc774\\ube0c\\ub7ec\\ub9ac", "nav.review": "\\ud655\\uc778 \\ud544\\uc694", "nav.log": "\\uae30\\ub85d",
  "nav.settings": "\\uc124\\uc815", "nav.language": "\\uc5b8\\uc5b4",
  "btn.choose_folder": "\\ud3f4\\ub354 \\uc120\\ud0dd", "btn.sort": "\\uc0ac\\uc9c4 \\ubd84\\ub958",
  "btn.apply": "\\ud3f4\\ub354\\ub85c \\ubcf5\\uc0ac", "btn.to_blue": "\\ud30c\\ub791\\uc73c\\ub85c", "btn.to_green": "\\ucd08\\ub85d\\uc73c\\ub85c",
  "btn.undo": "\\ub418\\ub3cc\\ub9ac\\uae30", "btn.save_png": "\\ubcf4\\uc815\\ubcf8 PNG \\uc800\\uc7a5", "btn.auto": "\\uc790\\ub3d9",
  "btn.back": "\\ub4a4\\ub85c",
  "tab.all": "\\uc804\\uccb4", "tab.blue": "\\ud30c\\ub791", "tab.green": "\\ucd08\\ub85d", "tab.review": "\\ud655\\uc778 \\ud544\\uc694",
  "group.no-signal": "\\uc2e0\\ud638 \\uc5c6\\uc74c", "group.mixed": "\\ud30c\\ub791+\\ucd08\\ub85d", "group.other": "\\uae30\\ud0c0",
  "stat.scanned": "\\uac80\\uc0ac", "stat.blue": "\\ud30c\\ub791", "stat.green": "\\ucd08\\ub85d", "stat.review": "\\ud655\\uc778 \\ud544\\uc694",
  "badge.human": "\\uc0ac\\uc6a9\\uc790 \\ud655\\uc815",
  "insp.title": "\\uac80\\uc0ac\\uad00", "insp.peak": "\\ucd5c\\ub300 \\ubc1d\\uae30", "insp.view": "\\ubcf4\\uae30",
  "insp.lit": "\\ubc1d\\uc740 \\ud53d\\uc140", "insp.blue_share": "\\ud30c\\ub791 \\ube44\\uc728", "insp.reason": "\\ud310\\uc815 \\uc774\\uc720",
  "insp.auto_view": "\\u03b3 {gamma} \\u00b7 {gain}\\ubc30 \\uc815\\uaddc\\ud654",
  "view.original": "\\uc6d0\\ubcf8", "view.corrected": "\\ubcf4\\uc815", "view.judgment": "\\ud310\\uc815 \\uc0c9\\uce60",
  "view.green_only": "\\ucd08\\ub85d\\ub9cc", "view.blue_only": "\\ud30c\\ub791\\ub9cc",
  "slider.brightness": "\\ubc1d\\uae30", "slider.gamma": "\\uac10\\ub9c8",
  "probe.line": "x {x}  y {y}   G {g}  B {b}  \\u03c1 {rho}",
  "msg.pick_or_drop": "\\uc0ac\\uc9c4 \\ud3f4\\ub354\\ub97c \\uc120\\ud0dd\\ud558\\uac70\\ub098 \\uc5ec\\uae30\\ub85c \\ub04c\\uc5b4\\ub2e4 \\ub193\\uc73c\\uc138\\uc694.",
  "msg.progress": "\\ubd84\\ub958 \\uc911\\u2026 {done} / {total}",
  "msg.done": "\\uc644\\ub8cc \\u2014 {total}\\uc7a5 \\ubd84\\ub958. {review}\\uc7a5\\uc740 \\ub208\\uc73c\\ub85c \\ud655\\uc778\\uc774 \\ud544\\uc694\\ud569\\ub2c8\\ub2e4.",
  "msg.excluded": "\\ucd9c\\ub825 \\ud3f4\\ub354 \\uc548\\uc774\\ub77c \\uc81c\\uc678\\ud55c \\ud30c\\uc77c: {n}\\uc7a5",
  "msg.no_signal": "\\uc2e0\\ud638 \\uc5c6\\uc74c \\u2014 \\ubcf4\\uc815\\ud560 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4.",
  "msg.moved": "{folder}\\ub85c \\uc728\\uacbc\\uc2b5\\ub2c8\\ub2e4.", "msg.undone": "\\uc774\\ub3d9\\uc744 \\ub418\\ub3cc\\ub838\\uc2b5\\ub2c8\\ub2e4.",
  "msg.saved_png": "\\uc800\\uc7a5\\ud568: {name}", "msg.copied": "{total}\\uc7a5 \\uc911 {copied}\\uc7a5\\uc744 \\ubcf5\\uc0ac\\ud588\\uc2b5\\ub2c8\\ub2e4.",
  "lang.title": "\\uc5b8\\uc5b4", "lang.prompt": "\\uc5b8\\uc5b4\\ub97c \\uace0\\ub974\\uc138\\uc694. \\ub098\\uc911\\uc5d0 \\uc124\\uc815\\uc5d0\\uc11c \\ubc14\\uafc0 \\uc218 \\uc788\\uc2b5\\ub2c8\\ub2e4.",
  "err.no_folder": "\\uadf8 \\ud3f4\\ub354\\uac00 \\uc5c6\\uc2b5\\ub2c8\\ub2e4.",
  "err.no_png": "\\uc774 \\ud3f4\\ub354\\uc5d0\\uc11c PNG \\uc0ac\\uc9c4\\uc744 \\ucc3e\\uc9c0 \\ubabb\\ud588\\uc2b5\\ub2c8\\ub2e4.",
  "err.write_failed": "{path}\\uc5d0 \\uc4f8 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4. \\uc5f4\\uc5b4 \\ub454 \\ud30c\\uc77c\\uc744 \\ub2eb\\uace0 \\ub2e4\\uc2dc \\uc2dc\\ub3c4\\ud558\\uc138\\uc694.",
  "log.title": "\\uc728\\uae34 \\uae30\\ub85d", "log.empty": "\\uc544\\uc9c1 \\uc728\\uae34 \\uac83\\uc774 \\uc5c6\\uc2b5\\ub2c8\\ub2e4.",
 },
}

def tr(key: str, lang: str, **params) -> str:
    text = T[lang][key]
    return text.format(**params) if params else text
'''

_install_stub("colorsortgui.enhance", _ENHANCE_SRC)   # 통합 때 삭제
_install_stub("colorsortgui.i18n", _I18N_SRC)         # 통합 때 삭제
# ==================== 통합 때 삭제 (END) ====================


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
