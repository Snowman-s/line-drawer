import sys
import PyQt6.QtCore as qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QMenuBar, QMenu, QLabel, QPushButton, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QSpinBox, QCheckBox
)
from canvas_dialog import CanvasDialog
from layer_properties_dialog import LayerPropertiesDialog
from save_canvas_dialog import SaveCanvasDialog
from PyQt6.QtGui import QAction, QPolygonF, QImage

from layer_properties_dialog import LayerPropertiesDialog

from canvas import Canvas, Layer

class MainWindow(QMainWindow):
    canvas = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Line Drawer")
        self.setGeometry(100, 100, 1000, 600)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu("ファイル", self)
        self.menu_bar.addMenu(file_menu)

        create_canvas_action = QAction("キャンバス生成", self)
        create_canvas_action.triggered.connect(self.open_canvas_dialog)
        file_menu.addAction(create_canvas_action)
        save_canvas_action = QAction("キャンバス保存", self)
        save_canvas_action.triggered.connect(self.save_canvas_dialog)
        file_menu.addAction(save_canvas_action)
        self.background_color = (255, 255, 255, 255)  # デフォルト白

        # 色選択UI（RGBAダイアログ）
        from PyQt6.QtWidgets import QPushButton
        self.color_rgba = (255, 0, 0, 255)  # 初期値:赤（塗り色）
        self.line_rgba = (0, 0, 0, 255)    # 初期値:黒（線色）
        color_label = QLabel("塗る色:")
        self.color_btn = QPushButton()
        self.update_color_btn()
        self.color_btn.clicked.connect(self.open_color_dialog)
        line_label = QLabel("線の色:")
        self.line_btn = QPushButton()
        self.update_line_btn()
        self.line_btn.clicked.connect(self.open_line_color_dialog)
        line_width_label = QLabel("線の太さ:")
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setRange(1, 40)
        self.line_width_spin.setValue(2)
        self.line_width_spin.valueChanged.connect(self.change_line_width)
        hlayout = QHBoxLayout()
        hlayout.addWidget(color_label)
        hlayout.addWidget(self.color_btn)
        hlayout.addWidget(line_label)
        hlayout.addWidget(self.line_btn)
        hlayout.addWidget(line_width_label)
        hlayout.addWidget(self.line_width_spin)
        hlayout.addStretch(1)
        self.line_count_spin = QSpinBox()
        self.line_count_spin.setRange(0, 200)
        self.line_count_spin.setValue(20)
        self.line_count_spin.setFixedWidth(60)
        hlayout.addWidget(QLabel("線の数:"))
        hlayout.addWidget(self.line_count_spin)
        regen_btn = QPushButton("レイヤー再生成")
        regen_btn.setFixedWidth(100)
        regen_btn.clicked.connect(self.regenerate_active_layer)
        hlayout.addWidget(regen_btn)
        color_widget = QWidget()
        color_widget.setLayout(hlayout)

        # 右側レイヤーパネル
        self.layer_panel = QWidget()
        self.layer_layout = QVBoxLayout()
        self.layer_list = QListWidget()
        self.layer_layout.addWidget(QLabel("レイヤー一覧"))
        self.layer_layout.addWidget(self.layer_list)
        self.add_layer_btn = QPushButton("レイヤー追加")
        self.del_layer_btn = QPushButton("レイヤー削除")
        self.layer_layout.addWidget(self.add_layer_btn)
        self.layer_layout.addWidget(self.del_layer_btn)
        self.layer_panel.setLayout(self.layer_layout)
        self.add_layer_btn.clicked.connect(self.add_layer)
        self.del_layer_btn.clicked.connect(self.delete_layer)
        self.layer_list.itemChanged.connect(self.layer_name_changed)

        # メインレイアウト
        self.central_widget = QWidget()
        self.vlayout = QHBoxLayout()
        self.left_vlayout = QVBoxLayout()
        self.left_vlayout.setContentsMargins(0,0,0,0)
        self.left_vlayout.setSpacing(0)
        self.left_vlayout.addWidget(color_widget)
        self.canvas = None
        self.left_vlayout.addWidget(QWidget()) # placeholder for canvas
        self.vlayout.addLayout(self.left_vlayout)
        self.vlayout.addWidget(self.layer_panel)
        self.central_widget.setLayout(self.vlayout)
        self.setCentralWidget(self.central_widget)

        # 初期キャンバス生成（共通化）
        self.init_canvas(800, 600, self.line_count_spin.value())

    def init_canvas(self, w, h, n):
        # キャンバスのクリア＋リサイズ
        if self.canvas:
            self.canvas.setParent(None)
        self.canvas = Canvas(w, h, self)
        self.canvas.lines = self.canvas.generate_lines(w, h, count=n)
        self.canvas.layers = [Layer("Layer 1")]
        self.canvas.layers[0].lines = self.canvas.lines
        self.canvas.layers[0].regions = self.canvas.create_regions(self.canvas.lines)
        self.canvas.layers[0].line_width = self.line_width_spin.value()
        self.left_vlayout.insertWidget(1, self.canvas)
        # レイヤー初期化
        self.layer_list.clear()
        for i, layer in enumerate(self.canvas.layers):
            item = QListWidgetItem()
            widget = LayerListItemWidget(layer.name, i, self, checked=layer.visible)
            self.layer_list.addItem(item)
            self.layer_list.setItemWidget(item, widget)
            # 初期レイヤー（選択中）はチェックボックス無効化
            if i == 0:
                widget.checkbox.setEnabled(False)
        self.layer_list.setCurrentRow(self.canvas.active_layer)
        self.layer_list.currentRowChanged.connect(self.change_active_layer)

    def update_color_btn(self):
        r, g, b, a = self.color_rgba
        self.color_btn.setStyleSheet(f"background-color: rgba({r},{g},{b},{a}); width:40px; height:24px;")
        self.color_btn.setText(f"RGBA: {r},{g},{b},{a}")

    def layer_name_changed(self, item):
        idx = self.layer_list.row(item)
        new_name = item.text()
        if self.canvas and 0 <= idx < len(self.canvas.layers):
            self.canvas.layers[idx].name = new_name
        # チェック状態（表示/非表示）も反映
        # 選択中レイヤーは必ず表示
        if self.canvas and 0 <= idx < len(self.canvas.layers):
            if idx == self.canvas.active_layer:
                item.setCheckState(qt.Qt.CheckState.Checked)
                self.canvas.layers[idx].visible = True
            else:
                self.canvas.layers[idx].visible = (item.checkState() == qt.Qt.CheckState.Checked)
            self.canvas.update()

    def change_line_width(self, value):
        if self.canvas:
            self.canvas.layers[self.canvas.active_layer].line_width = value
            self.canvas.update()

    def update_line_btn(self):
        # アクティブレイヤーの線色を表示
        if self.canvas:
            r, g, b, a = self.canvas.layers[self.canvas.active_layer].line_rgba
            self.line_width_spin.setValue(self.canvas.layers[self.canvas.active_layer].line_width)
        else:
            r, g, b, a = self.line_rgba
        self.line_btn.setStyleSheet(f"background-color: rgba({r},{g},{b},{a}); width:40px; height:24px;")
        self.line_btn.setText(f"RGBA: {r},{g},{b},{a}")

    def open_color_dialog(self):
        from PyQt6.QtWidgets import QColorDialog
        dlg = QColorDialog(self)
        dlg.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        dlg.setWindowTitle("色を選択（カラーホイール付き）")
        from PyQt6.QtGui import QColor
        r, g, b, a = self.color_rgba
        dlg.setCurrentColor(QColor(r, g, b, a))
        if dlg.exec():
            qcolor = dlg.currentColor()
            self.color_rgba = (qcolor.red(), qcolor.green(), qcolor.blue(), qcolor.alpha())
            self.update_color_btn()

    def open_line_color_dialog(self):
        from PyQt6.QtWidgets import QColorDialog
        dlg = QColorDialog(self)
        dlg.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        dlg.setWindowTitle("線の色を選択（カラーホイール付き）")
        from PyQt6.QtGui import QColor
        # アクティブレイヤーの線色
        r, g, b, a = self.canvas.layers[self.canvas.active_layer].line_rgba if self.canvas else self.line_rgba
        dlg.setCurrentColor(QColor(r, g, b, a))
        if dlg.exec():
            qcolor = dlg.currentColor()
            if self.canvas:
                self.canvas.layers[self.canvas.active_layer].line_rgba = (qcolor.red(), qcolor.green(), qcolor.blue(), qcolor.alpha())
                self.update_line_btn()
                self.canvas.update()
            else:
                self.line_rgba = (qcolor.red(), qcolor.green(), qcolor.blue(), qcolor.alpha())
                self.update_line_btn()

    def add_layer(self):
        if self.canvas:
            name = f"Layer {len(self.canvas.layers)+1}"
            layer = Layer(name)
            layer.lines = self.canvas.generate_lines(self.canvas.width(), self.canvas.height(), count=self.line_count_spin.value())
            layer.regions = self.canvas.create_regions(layer.lines)
            layer.colored_regions = []
            # 新規レイヤーの線色は現在のUIの色
            layer.line_rgba = self.line_rgba
            layer.line_width = self.line_width_spin.value()
            self.canvas.layers.append(layer)
            item = QListWidgetItem()
            widget = LayerListItemWidget(layer.name, len(self.canvas.layers)-1, self, checked=True)
            self.layer_list.addItem(item)
            self.layer_list.setItemWidget(item, widget)
            self.canvas.active_layer = len(self.canvas.layers)-1
            self.layer_list.setCurrentRow(self.canvas.active_layer)
            self.update_line_btn()
            self.canvas.update()

    def delete_layer(self):
        if self.canvas and len(self.canvas.layers) > 1:
            idx = self.layer_list.currentRow()
            self.layer_list.takeItem(idx)
            self.canvas.layers.pop(idx)

            self.canvas.active_layer = self.layer_list.currentRow()
            self.canvas.update()

    def open_canvas_dialog(self):
        dialog = CanvasDialog(self)
        if dialog.exec():
            w, h, n = dialog.get_canvas_params()
            self.init_canvas(w, h, n)

    def change_active_layer(self, idx):
        if self.canvas:
            self.canvas.active_layer = idx
            # 選択したレイヤーは必ず表示状態にする
            item = self.layer_list.item(idx)
            if not item:
                return

            print(f"Active layer changed to {idx}: {self.canvas.layers[idx].name}")
            self.canvas.layers[idx].visible = True
            # チェックボックスもONにし、アンチェック不可
            widget = self.layer_list.itemWidget(item)
            if widget and hasattr(widget, 'checkbox'):
                widget.checkbox.setChecked(True)
                widget.checkbox.setEnabled(False)
            self.line_width_spin.setValue(self.canvas.layers[idx].line_width)
            self.update_line_btn()
            self.canvas.update()
            # 他のレイヤーのチェックボックスは有効化
            for i in range(self.layer_list.count()):
                if i != idx:
                    other_item = self.layer_list.item(i)
                    other_widget = self.layer_list.itemWidget(other_item)
                    if other_widget and hasattr(other_widget, 'checkbox'):
                        other_widget.checkbox.setEnabled(True)

    def save_canvas_dialog(self):
        if not self.canvas:
            return
        # プレビュー付きダイアログ
        dlg = SaveCanvasDialog(self, create_preview_image=lambda antialiasing: self.canvas.to_qimage(antialiasing))
        if not dlg.exec():
            return
        path = dlg.get_params()
        if not path:
            return
        if path.lower().endswith('.svg'):
            self.canvas.to_svg(path)
        else:
            self.canvas.to_qimage(dlg.is_antialiasing_enabled()).save(path)

    def regenerate_active_layer(self):
        if self.canvas and 0 <= self.canvas.active_layer < len(self.canvas.layers):
            layer = self.canvas.layers[self.canvas.active_layer]
            w, h = self.canvas.width(), self.canvas.height()
            n = self.line_count_spin.value()
            layer.lines = self.canvas.generate_lines(w, h, count=n)
            layer.regions = self.canvas.create_regions(layer.lines)
            layer.colored_regions = []
            self.canvas.update()

    def open_layer_properties_dialog(self):
        idx = self.layer_list.currentRow()
        if idx < 0 or not self.canvas or idx >= len(self.canvas.layers):
            return
        layer = self.canvas.layers[idx]
        dlg = LayerPropertiesDialog(self, layer_name=layer.name)
        if dlg.exec():
            new_name = dlg.get_name()
            layer.name = new_name
            item = self.layer_list.item(idx)
            if item:
                item.setText(new_name)

class LayerListItemWidget(QWidget):
    def __init__(self, layer_name, idx, parent, checked=True):
        super().__init__()
        self.idx = idx
        self.parent = parent
        layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)
        layout.addWidget(self.checkbox)
        self.label = QLabel(layer_name)
        layout.addWidget(self.label)
        self.prop_btn = QPushButton("...")
        self.prop_btn.setFixedWidth(30)
        self.prop_btn.setToolTip("レイヤー情報編集")
        layout.addWidget(self.prop_btn)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.prop_btn.clicked.connect(self.open_properties_dialog)
        self.checkbox.stateChanged.connect(self.toggle_layer_visible)
        self.label.mouseDoubleClickEvent = self.start_edit_name
        self.edit = None

    def open_properties_dialog(self):
        idx = self.idx
        if idx < 0 or not self.parent.canvas or idx >= len(self.parent.canvas.layers):
            return
        layer = self.parent.canvas.layers[idx]
        dlg = LayerPropertiesDialog(self.parent, layer_name=layer.name)
        # 初期値として現在のsave_modeを反映
        dlg.save_mode_radios[getattr(layer, 'save_mode', 0)].setChecked(True)
        if dlg.exec():
            new_name = dlg.get_name()
            layer.name = new_name
            self.label.setText(new_name)
            # 保存モードも反映
            mode_idx = dlg.get_save_mode()
            layer.save_mode = mode_idx

    def toggle_layer_visible(self, state):
        if not self.parent.canvas or self.idx >= len(self.parent.canvas.layers):
            return
        layer = self.parent.canvas.layers[self.idx]
        layer.visible = bool(state)
        self.parent.canvas.update()

    def start_edit_name(self, event):
        if self.edit:
            return
        self.edit = QLineEdit(self.label.text())
        self.layout().replaceWidget(self.label, self.edit)
        self.label.hide()
        self.edit.setFocus()
        self.edit.returnPressed.connect(self.commit_edit_name)
        self.edit.focusOutEvent = self.commit_edit_name_on_focus_out

    def commit_edit_name(self):
        new_name = self.edit.text()
        self.label.setText(new_name)
        self.label.show()
        self.layout().replaceWidget(self.edit, self.label)
        self.edit.deleteLater()
        self.edit = None
        # モデルにも反映
        if self.parent.canvas and self.idx < len(self.parent.canvas.layers):
            self.parent.canvas.layers[self.idx].name = new_name

    def commit_edit_name_on_focus_out(self, event):
        QLineEdit.focusOutEvent(self.edit, event)
        self.commit_edit_name()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
