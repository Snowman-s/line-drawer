from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QColorDialog, QFileDialog
from PyQt6.QtGui import QColor

class SaveCanvasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("キャンバス保存")
        self.setFixedSize(400, 120)
        layout = QVBoxLayout()
        hlayout_file = QHBoxLayout()
        self.file_edit = QLineEdit("canvas.png")
        file_btn = QPushButton("...")
        hlayout_file.addWidget(QLabel("ファイル名:"))
        hlayout_file.addWidget(self.file_edit)
        hlayout_file.addWidget(file_btn)
        layout.addLayout(hlayout_file)
        ok_btn = QPushButton("保存")
        cancel_btn = QPushButton("キャンセル")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        file_btn.clicked.connect(self.open_file_dialog)
    # 背景色関連のUI・処理は削除
    def open_file_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存先", self.file_edit.text(), "PNG Files (*.png);;All Files (*)")
        if path:
            self.file_edit.setText(path)
    def get_params(self):
        return self.file_edit.text()
