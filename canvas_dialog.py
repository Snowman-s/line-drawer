from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QColorDialog, QFileDialog

class CanvasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("キャンバス生成")
        self.setFixedSize(300, 180)
        layout = QVBoxLayout()

        hlayout_w = QHBoxLayout()
        hlayout_h = QHBoxLayout()
        hlayout_n = QHBoxLayout()
        self.width_edit = QLineEdit("800")
        self.height_edit = QLineEdit("600")
        self.linecount_edit = QLineEdit("20")
        hlayout_w.addWidget(QLabel("幅:"))
        hlayout_w.addWidget(self.width_edit)
        hlayout_h.addWidget(QLabel("高さ:"))
        hlayout_h.addWidget(self.height_edit)
        hlayout_n.addWidget(QLabel("線の数:"))
        hlayout_n.addWidget(self.linecount_edit)

        layout.addLayout(hlayout_w)
        layout.addLayout(hlayout_h)
        layout.addLayout(hlayout_n)

        self.create_btn = QPushButton("生成")
        self.create_btn.clicked.connect(self.accept)
        layout.addWidget(self.create_btn)
        self.setLayout(layout)

    def get_canvas_params(self):
        try:
            w = int(self.width_edit.text())
            h = int(self.height_edit.text())
            n = int(self.linecount_edit.text())
            return w, h, n
        except ValueError:
            return 800, 600, 20
