"""첫 실행 언어 선택. GUI exe에는 콘솔이 없으므로 v1의 키보드 메뉴를 쓸 수 없다."""
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QRadioButton,
                               QVBoxLayout)


class LanguageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Language / 언어")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Choose your language. / 언어를 고르세요."))
        self.en = QRadioButton("English")
        self.ko = QRadioButton("한국어")
        self.en.setChecked(True)                 # 기본 English
        lay.addWidget(self.en)
        lay.addWidget(self.ko)
        box = QDialogButtonBox(QDialogButtonBox.Ok)
        box.accepted.connect(self.accept)
        lay.addWidget(box)

    def selected(self) -> str:
        return "ko" if self.ko.isChecked() else "en"
