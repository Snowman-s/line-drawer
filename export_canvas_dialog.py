from typing import Callable
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QGraphicsView, QGraphicsScene, QProgressBar
from PyQt6.QtGui import QPixmap, QImage

class ExportCanvasDialog(QDialog):
    class PreviewWorker(QObject):
        finished = pyqtSignal(object)
        progressChanged = pyqtSignal(float)  # 0.0〜1.0
        def __init__(self, create_preview_image, antialiasing):
            super().__init__()
            self.create_preview_image = create_preview_image
            self.antialiasing = antialiasing
        def run(self):
            def progress_callback(value):
                self.progressChanged.emit(value)
            qimage = self.create_preview_image(self.antialiasing, progress_callback)
            self.finished.emit(qimage)

    def __init__(self, parent=None, create_preview_image: Callable[[bool, Callable[[float], None]], QImage]=lambda antialiasing, prog_callback: QImage()):
        super().__init__(parent)
        self.setWindowTitle("キャンバス保存")
        self.setFixedSize(400, 320)
        layout = QVBoxLayout()
        hlayout_file = QHBoxLayout()
        self.file_edit = QLineEdit("canvas.svg")
        file_btn = QPushButton("...")
        hlayout_file.addWidget(QLabel("ファイル名:"))
        hlayout_file.addWidget(self.file_edit)
        hlayout_file.addWidget(file_btn)
        layout.addLayout(hlayout_file)
        # アンチエイリアシング チェックボックス
        from PyQt6.QtWidgets import QCheckBox
        self.antialias_checkbox = QCheckBox("アンチエイリアシング")
        self.antialias_checkbox.setChecked(True)
        layout.addWidget(self.antialias_checkbox)
        # プレビュー
        self.preview_label = QLabel("プレビュー:")
        layout.addWidget(self.preview_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
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
        self.create_preview_image = create_preview_image
        self.preview_thread = None
        self.set_preview_image_async(create_preview_image, self.antialias_checkbox.isChecked())
        self.antialias_checkbox.stateChanged.connect(lambda: self.set_preview_image_async(self.create_preview_image, self.antialias_checkbox.isChecked()))

    def set_preview_image_async(self, create_preview_image, antialiasing):
        # 非同期でプレビュー画像を生成
        if self.preview_thread:
            self.preview_thread.quit()
            self.preview_thread.wait()
        self.preview_worker = self.PreviewWorker(create_preview_image, antialiasing)
        self.preview_thread = QThread()
        self.preview_worker.moveToThread(self.preview_thread)
        self.preview_thread.started.connect(self.preview_worker.run)
        self.preview_worker.finished.connect(self.set_preview_image)
        self.preview_worker.finished.connect(self.preview_thread.quit)
        self.preview_worker.progressChanged.connect(self.on_preview_progress)
        self.preview_thread.start()

    def update_preview_image(self):
        """
        Update the preview image according to the anti-aliasing checkbox state.
        """
        self.set_preview_image_async(self.create_preview_image, self.antialias_checkbox.isChecked())

    def on_preview_progress(self, value):
        self.progress_bar.setValue(int(value * 100))
    def open_file_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存先", self.file_edit.text(), "PNG Files (*.png);;SVG Files (*.svg);;All Files (*)")
        if path:
            self.file_edit.setText(path)
    def get_params(self):
        return self.file_edit.text()

    def is_antialiasing_enabled(self):
        """
        Returns True if anti-aliasing is enabled.
        """
        return self.antialias_checkbox.isChecked()
    
    def set_preview_image(self, qimage: QImage):
        pixmap = QPixmap.fromImage(qimage)
        self.preview_scene.clear()
        self.preview_scene.addPixmap(pixmap)
        self.preview_view.fitInView(self.preview_scene.itemsBoundingRect())
        self.progress_bar.setValue(100)
