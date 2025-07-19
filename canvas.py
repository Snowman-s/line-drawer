import sys
import random, math
from typing import List
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPaintEvent, QPolygonF

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union, polygonize

class Layer:
    save_mode_enum = [
        "通常",
        "塗られている領域に接する線のみを保存",
        "塗られている領域に接する線のみを保存し、塗りつぶしは描画しない"
    ]

    def __init__(self, name, visible=True):
        self.save_mode = 0  # デフォルトの保存モード（通常）
        self.name = name
        self.visible = visible
        self.lines = []
        self.colored_regions = []
        self.regions: List[Polygon] = []  # 領域もレイヤーごとに保持
        self.line_rgba = (0, 0, 0, 255)  # 線の色もレイヤーごとに保持
        self.line_width = 2  # 線の太さ（デフォルト2）

class Canvas(QWidget):
    def __init__(self, width=800, height=600, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet("background-color: white;")
        self.layers = [Layer("Layer 1")]
        self.active_layer = 0
        initial_lines = self.generate_lines(width, height, count=20)
        self.layers[0].lines = initial_lines
        self.layers[0].regions = self.create_regions(initial_lines)
        self.selected_region = None
        self.colored_regions = []    # 塗りつぶした領域のリスト
        # 親(MainWindow)からRGBA値を参照
        self.selected_rgba = (255, 0, 0, 255)
        if parent and hasattr(parent, "parent") and hasattr(parent.parent(), "color_rgba"):
            self.get_rgba = lambda: parent.parent().color_rgba
            self.get_line_rgba = lambda: parent.parent().line_rgba
        elif parent and hasattr(parent, "color_rgba"):
            self.get_rgba = lambda: parent.color_rgba
            self.get_line_rgba = lambda: parent.line_rgba
        else:
            self.get_rgba = lambda: (255,0,0,255)
            self.get_line_rgba = lambda: (0,0,0,255)

    def mousePressEvent(self, event):
        # クリック開始時にドラッグフラグをセット
        self._dragging = True
        self._prev_pos = (event.position().x() if hasattr(event, 'position') else event.x(),
                          event.position().y() if hasattr(event, 'position') else event.y())
        self._color_region_at_event(event)

    def mouseMoveEvent(self, event):
        # ドラッグ中のみ領域を塗る
        if getattr(self, '_dragging', False):
            x = event.position().x() if hasattr(event, 'position') else event.x()
            y = event.position().y() if hasattr(event, 'position') else event.y()
            prev_x, prev_y = getattr(self, '_prev_pos', (x, y))
            drag_line = LineString([(prev_x, prev_y), (x, y)])
            layer = self.layers[self.active_layer]
            colored = False
            for region in layer.regions:
                if region.intersects(drag_line):
                    # 塗りつぶし
                    for i, (rgn, _) in enumerate(layer.colored_regions):
                        if region.equals(rgn):
                            layer.colored_regions[i] = (region, self.get_rgba())
                            break
                    else:
                        layer.colored_regions.append((region, self.get_rgba()))
                    colored = True
            if colored:
                self.update()
            self._prev_pos = (x, y)

    def mouseReleaseEvent(self, event):
        # ドラッグ終了
        self._dragging = False
        self._prev_pos = None

    def _color_region_at_event(self, event):
        x = event.position().x() if hasattr(event, 'position') else event.x()
        y = event.position().y() if hasattr(event, 'position') else event.y()
        pt = Point(x, y)
        layer = self.layers[self.active_layer]
        if hasattr(layer, 'regions'):
            for region in layer.regions:
                if region.contains(pt):
                    self.selected_region = region
                    for i, (rgn, _) in enumerate(layer.colored_regions):
                        if region.equals(rgn):
                            layer.colored_regions[i] = (region, self.get_rgba())
                            break
                    else:
                        layer.colored_regions.append((region, self.get_rgba()))
                    self.update()
                    break
            else:
                self.selected_region = None
                self.update()

    def generate_lines(self, width, height, count=20):
        lines = []
        diag = math.hypot(width, height)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            cx = random.uniform(0, width)
            cy = random.uniform(0, height)
            length = diag + random.uniform(20, 100)
            dx = math.cos(angle) * length
            dy = math.sin(angle) * length
            x1 = cx - dx
            y1 = cy - dy
            x2 = cx + dx
            y2 = cy + dy
            lines.append((x1, y1, x2, y2))
        return lines

    def create_regions(self, lines):
        line_strings = [LineString([(x1, y1), (x2, y2)]) for x1, y1, x2, y2 in lines]
        # キャンバスの四辺を追加
        w, h = self.width(), self.height()
        border_lines = [
            LineString([(0, 0), (w, 0)]),
            LineString([(w, 0), (w, h)]),
            LineString([(w, h), (0, h)]),
            LineString([(0, h), (0, 0)])
        ]
        all_lines = line_strings + border_lines
        merged_lines = unary_union(all_lines)
        polygons = polygonize(merged_lines)
        regions = []
        for poly in polygons:
            if isinstance(poly, Polygon):
                regions.append(poly)
        return regions

    def paintEvent(self, event: QPaintEvent):
        from PyQt6 import QtCore
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QColor, QPen
        painter = QPainter(self)
        # --- 下層: αチェッカー（市松模様） ---
        checker_size = 20
        color1 = Qt.GlobalColor.lightGray
        color2 = Qt.GlobalColor.white
        w, h = self.width(), self.height()
        for y in range(0, h, checker_size):
            for x in range(0, w, checker_size):
                if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                    painter.setBrush(color1)
                else:
                    painter.setBrush(color2)
                painter.setPen(Qt.GlobalColor.transparent)
                painter.drawRect(x, y, checker_size, checker_size)
        # --- 上層: 塗り領域・線 ---
        # 各レイヤーを描画
        for idx, layer in enumerate(self.layers):
            if not layer.visible:
                continue
            for region, rgba in layer.colored_regions:
                coords = region.exterior.coords
                r, g, b, a = rgba
                qcolor = QColor(r, g, b, a)
                painter.setBrush(qcolor)
                painter.setPen(qcolor)
                poly = QPolygonF([QtCore.QPointF(int(x), int(y)) for x, y in coords])
                painter.drawPolygon(poly)
            # 線描画（レイヤーごとの色と太さ）
            r, g, b, a = layer.line_rgba
            line_color = QColor(r, g, b, a)
            pen = QPen(line_color)
            pen.setWidth(layer.line_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for x1, y1, x2, y2 in layer.lines:
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def get_shared_edges(self, target_polygons: List[Polygon], layer_idx: int) -> List[LineString]:
        shared_edges = []

        for target in target_polygons:
            for other in self.layers[layer_idx].regions:
                if target.equals(other):
                    continue  # 同じポリゴンはスキップ

                # 共通部分を取得
                inter = target.boundary.intersection(other.boundary)

                # 共通部分が線分なら追加
                if isinstance(inter, LineString):
                    if not inter.is_empty:
                        shared_edges.append(inter)

        return shared_edges
