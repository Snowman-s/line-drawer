from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QVBoxLayout, QLabel, QDialog, QProgressBar
)

class ProgressBarDialog(QDialog):
    def __init__(self, parent=None, title="Progress", message="Processing..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        layout = QVBoxLayout(self)
        self.label = QLabel(message)
        layout.addWidget(self.label)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
