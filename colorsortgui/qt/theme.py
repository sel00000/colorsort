"""VENOM 방향 토큰과 전역 QSS. 승인된 목업(2026-07-21)의 색을 그대로 쓴다."""

C = {
    "BG0": "#141014", "BG1": "#1B1216", "BG2": "#2A1418",
    "PANEL": "#171114", "CARD": "#221A1E", "HAIR": "#372A31",
    "TEXT": "#EFE9EA", "MUT": "#B9AEB1",
    "RED": "#D5323F", "RED_H": "#E04350",
    "BLUE": "#7FA5F7", "GREEN": "#54CD92", "AMBER": "#E8B04B",
    "CYAN": "#3EC6D6",
    "MONO": "Cascadia Mono, Consolas, monospace",
}

QSS = f"""
QMainWindow {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 {C['BG0']}, stop:0.55 {C['BG1']}, stop:1 {C['BG2']}); }}
QWidget {{ color: {C['TEXT']};
    font-family: "Segoe UI", "Malgun Gothic", sans-serif; font-size: 14px; }}
QFrame#sidebar {{ background: {C['PANEL']}; border: none; }}
QFrame.card {{ background: {C['CARD']}; border: 1px solid {C['HAIR']}; border-radius: 12px; }}
QLabel.k {{ color: {C['MUT']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; }}
QLabel.mut {{ color: {C['MUT']}; }}
QLabel.mono {{ font-family: {C['MONO']}; }}
QPushButton {{ background: rgba(255,255,255,0.06); border: 1px solid {C['HAIR']};
    border-radius: 9px; padding: 8px 15px; font-weight: 600; }}
QPushButton:hover {{ background: rgba(255,255,255,0.10); }}
QPushButton:focus {{ outline: none; border: 1px solid {C['MUT']}; }}
QPushButton#primary {{ background: {C['RED']}; border: none; color: white; font-weight: 700; }}
QPushButton#primary:hover {{ background: {C['RED_H']}; }}
QPushButton#toBlue {{ color: {C['BLUE']}; border-color: #31517E; }}
QPushButton#toGreen {{ color: {C['GREEN']}; border-color: #2A5C44; }}
QPushButton.nav {{ text-align: left; border: none; border-radius: 9px; padding: 9px 12px;
    color: {C['MUT']}; background: transparent; }}
QPushButton.nav:checked {{ background: rgba(213,50,63,0.16); color: {C['TEXT']}; font-weight: 600; }}
QPushButton.tab {{ border-radius: 14px; padding: 6px 14px; color: {C['MUT']};
    background: rgba(255,255,255,0.05); border: none; }}
QPushButton.tab:checked {{ background: {C['TEXT']}; color: {C['BG1']}; font-weight: 700; }}
QListWidget {{ background: transparent; border: none; }}
QListWidget::item {{ color: {C['MUT']}; border-radius: 10px; padding: 4px; }}
QListWidget::item:selected {{ background: rgba(213,50,63,0.18); }}
QSlider::groove:horizontal {{ height: 4px; background: {C['HAIR']}; border-radius: 2px; }}
QSlider::handle:horizontal {{ width: 14px; height: 14px; margin: -5px 0;
    border-radius: 7px; background: {C['TEXT']}; }}
QProgressBar {{ background: {C['HAIR']}; border: none; border-radius: 2px; height: 4px; text-align: center; }}
QProgressBar::chunk {{ background: {C['RED']}; border-radius: 2px; }}
QToolTip {{ background: {C['CARD']}; color: {C['TEXT']}; border: 1px solid {C['HAIR']}; }}
"""
