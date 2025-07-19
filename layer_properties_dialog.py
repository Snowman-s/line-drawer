from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

class LayerPropertiesDialog(QDialog):
    def __init__(self, parent=None, layer_name=""):
        super().__init__(parent)
        self.setWindowTitle("レイヤー情報編集")
        self.setFixedSize(300, 120)
        layout = QVBoxLayout()
        hlayout_name = QHBoxLayout()
        self.name_edit = QLineEdit(layer_name)
        hlayout_name.addWidget(QLabel("レイヤー名:"))
        hlayout_name.addWidget(self.name_edit)
        layout.addLayout(hlayout_name)
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("キャンセル")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
    def get_name(self):
        return self.name_edit.text()
