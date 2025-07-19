from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QImage

class SaveCanvasDialog(QDialog):
    def __init__(self, parent=None, preview_image: QImage = None):
        super().__init__(parent)
        self.setWindowTitle("キャンバス保存")
        self.setFixedSize(400, 320)
        layout = QVBoxLayout()
        hlayout_file = QHBoxLayout()
        self.file_edit = QLineEdit("canvas.png")
        file_btn = QPushButton("...")
        hlayout_file.addWidget(QLabel("ファイル名:"))
        hlayout_file.addWidget(self.file_edit)
        hlayout_file.addWidget(file_btn)
        layout.addLayout(hlayout_file)
        # プレビュー
        self.preview_label = QLabel("プレビュー:")
        layout.addWidget(self.preview_label)
        self.preview_view = QGraphicsView()
        self.preview_scene = QGraphicsScene()
        self.preview_view.setScene(self.preview_scene)
        self.preview_view.setFixedHeight(160)
        layout.addWidget(self.preview_view)
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
        if preview_image is not None:
            self.set_preview_image(preview_image)
    def open_file_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存先", self.file_edit.text(), "PNG Files (*.png);;All Files (*)")
        if path:
            self.file_edit.setText(path)
    def get_params(self):
        return self.file_edit.text()
    def set_preview_image(self, qimage: QImage):
        pixmap = QPixmap.fromImage(qimage)
        self.preview_scene.clear()
        self.preview_scene.addPixmap(pixmap)
        self.preview_view.fitInView(self.preview_scene.itemsBoundingRect())
