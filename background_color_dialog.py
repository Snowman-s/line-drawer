from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QColorDialog
from PyQt6.QtGui import QColor

class BackgroundColorDialog(QDialog):
    def __init__(self, parent=None, default_bg=(255,255,255,255)):
        super().__init__(parent)
        self.setWindowTitle("背景色を選択")
        self.setFixedSize(300, 120)
        layout = QVBoxLayout()
        self.bg_btn = QPushButton()
        self.bg_rgba = default_bg
        self.update_bg_btn()
        layout.addWidget(QLabel("背景色:"))
        layout.addWidget(self.bg_btn)
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("キャンセル")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.bg_btn.clicked.connect(self.open_bg_color_dialog)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
    def update_bg_btn(self):
        r,g,b,a = self.bg_rgba
        self.bg_btn.setStyleSheet(f"background-color: rgba({r},{g},{b},{a}); width:40px; height:24px;")
        self.bg_btn.setText(f"RGBA: {r},{g},{b},{a}")
    def open_bg_color_dialog(self):
        dlg = QColorDialog(self)
        dlg.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        dlg.setWindowTitle("背景色を選択")
        r,g,b,a = self.bg_rgba
        dlg.setCurrentColor(QColor(r,g,b,a))
        if dlg.exec():
            qcolor = dlg.currentColor()
            self.bg_rgba = (qcolor.red(), qcolor.green(), qcolor.blue(), qcolor.alpha())
            self.update_bg_btn()
    def get_bg_color(self):
        return self.bg_rgba
