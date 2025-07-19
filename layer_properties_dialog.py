from typing import List
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup
from canvas import Layer

class LayerPropertiesDialog(QDialog):
    def __init__(self, parent=None, layer_name=""):
        super().__init__(parent)
        self.setWindowTitle("レイヤー情報編集")
        self.setFixedSize(500, 240)
        layout = QVBoxLayout()
        hlayout_name = QHBoxLayout()
        self.name_edit = QLineEdit(layer_name)
        hlayout_name.addWidget(QLabel("レイヤー名:"))
        hlayout_name.addWidget(self.name_edit)
        layout.addLayout(hlayout_name)
        # 保存モード選択（ラジオボタン）
        self.save_mode_group = QButtonGroup(self)
        self.save_mode_radios: List[QRadioButton] = []
        mode_labels = Layer.save_mode_enum
        for i, label in enumerate(mode_labels):
            radio = QRadioButton(label)
            self.save_mode_group.addButton(radio, i)
            self.save_mode_radios.append(radio)
        layout.addWidget(QLabel("保存モード:"))
        for radio in self.save_mode_radios:
            layout.addWidget(radio)
        self.save_mode_radios[0].setChecked(True)
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
    def get_save_mode(self):
        return self.save_mode_group.checkedId()

