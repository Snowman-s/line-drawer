import sys
import random, math
from typing import List
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPaintEvent, QPolygonF

from shapely.geometry import LineString, MultiLineString, Point, Polygon
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
        self.lines: List[LineString] = None
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

    def generate_lines(self, width, height, count=20) -> List[LineString]:
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
            lines.append(LineString([(x1, y1), (x2, y2)]))

        return lines

    def create_regions(self, lines):
        # キャンバスの四辺を追加
        w, h = self.width(), self.height()
        all_lines = lines + [
            LineString([(0, 0), (w, 0)]),
            LineString([(w, 0), (w, h)]),
            LineString([(w, h), (0, h)]),
            LineString([(0, h), (0, 0)])
        ]
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
            for line in layer.lines:
                painter.drawLine(int(line.coords[0][0]), int(line.coords[0][1]), 
                                 int(line.coords[1][0]), int(line.coords[1][1]))

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

    def _coords_equal(self, c1, c2, tol=1e-6):
        import math
        return math.isclose(c1[0], c2[0], abs_tol=tol) and math.isclose(c1[1], c2[1], abs_tol=tol)

    def _merge_connected_lines(self, lines):
        """
        Merge connected LineStrings into polylines (list of points).
        Returns a list of polylines, each as a list of (x, y) tuples.
        Uses math.isclose for coordinate equality.
        """
        from shapely.geometry import LineString
        unused = [list(line.coords) for line in lines if isinstance(line, LineString)]
        polylines = []
        while unused:
            poly = unused.pop(0)
            changed = True
            while changed:
                changed = False
                for i, other in enumerate(unused):
                    if self._coords_equal(poly[-1], other[0]):
                        poly += other[1:]
                        unused.pop(i)
                        changed = True
                        break
                    elif self._coords_equal(poly[0], other[-1]):
                        poly = other[:-1] + poly
                        unused.pop(i)
                        changed = True
                        break
                    elif self._coords_equal(poly[0], other[0]):
                        poly = other[::-1] + poly
                        unused.pop(i)
                        changed = True
                        break
                    elif self._coords_equal(poly[-1], other[-1]):
                        poly += other[-2::-1]
                        unused.pop(i)
                        changed = True
                        break
            polylines.append(poly)
        return polylines

    def to_svg(self, path):
        w, h = self.width(), self.height()
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
        for idx, layer in enumerate(self.layers):
            if not layer.visible:
                continue
            mode = getattr(layer, 'save_mode', 0)
            # 塗り領域
            if mode == 0 or mode == 1:
                for region, rgba in layer.colored_regions:
                    coords = list(region.exterior.coords)
                    r, g, b, a = rgba
                    fill = f'rgba({r},{g},{b},{a/255:.2f})' if a < 255 else f'rgb({r},{g},{b})'
                    points = ' '.join(f'{int(x)},{int(y)}' for x, y in coords)
                    svg.append(f'<polygon points="{points}" style="fill:{fill};stroke:{fill};stroke-width:1" />')
            # 線
            r, g, b, a = layer.line_rgba
            stroke = f'rgba({r},{g},{b},{a/255:.2f})' if a < 255 else f'rgb({r},{g},{b})'
            sw = layer.line_width
            if mode == 0:
                merged_lines = unary_union(layer.lines)
                # --- 修正: 連続する線をpolyline化 ---
                if hasattr(merged_lines, 'geoms'):
                    polylines = self._merge_connected_lines(merged_lines.geoms)
                    for poly in polylines:
                        if len(poly) >= 2:
                            svg.append(f'<polyline points="{" ".join(f"{int(x)},{int(y)}" for x, y in poly)}" style="stroke:{stroke};stroke-width:{sw};fill:none" />')
                elif isinstance(merged_lines, LineString):
                    coords = list(merged_lines.coords)
                    if len(coords) >= 2:
                        svg.append(f'<polyline points="{" ".join(f"{int(x)},{int(y)}" for x, y in coords)}" style="stroke:{stroke};stroke-width:{sw};fill:none" />')
            else:
                colored_polys = [region for region, _ in layer.colored_regions]
                shared_edges = self.get_shared_edges(colored_polys, idx)
                merged_lines = unary_union(shared_edges)
                if hasattr(merged_lines, 'geoms'):
                    polylines = self._merge_connected_lines(merged_lines.geoms)
                    for poly in polylines:
                        if len(poly) >= 2:
                            svg.append(f'<polyline points="{" ".join(f"{int(x)},{int(y)}" for x, y in poly)}" style="stroke:{stroke};stroke-width:{sw};fill:none" />')
                elif isinstance(merged_lines, LineString):
                    coords = list(merged_lines.coords)
                    if len(coords) >= 2:
                        svg.append(f'<polyline points="{" ".join(f"{int(x)},{int(y)}" for x, y in coords)}" style="stroke:{stroke};stroke-width:{sw};fill:none" />')
        svg.append('</svg>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg))

    def to_qimage(self):
        from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QPolygonF
        from PyQt6.QtCore import QPointF
        w, h = self.width(), self.height()
        image = QImage(w, h, QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        for idx, layer in enumerate(self.layers):
            if not layer.visible:
                continue
            mode = getattr(layer, 'save_mode', 0)
            # 塗り領域
            if mode == 0 or mode == 1:
                for region, rgba in layer.colored_regions:
                    coords = region.exterior.coords
                    rr, gg, bb, aa = rgba
                    qcolor = QColor(rr, gg, bb, aa)
                    painter.setBrush(qcolor)
                    painter.setPen(qcolor)
                    poly = QPolygonF([QPointF(x, y) for x, y in coords])
                    painter.drawPolygon(poly)
            # 線
            r, g, b, a = layer.line_rgba
            line_color = QColor(r, g, b, a)
            pen = QPen(line_color)
            pen.setWidth(layer.line_width)
            painter.setPen(pen)
            painter.setBrush(QColor(0,0,0,0))
            if mode == 0:
                for lines in layer.lines:
                    coords = list(lines.coords)
                    if len(coords) == 2:
                      x1, y1 = coords[0]
                      x2, y2 = coords[1]
                      painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            else:
                colored_polys = [region for region, _ in layer.colored_regions]
                shared_edges = self.get_shared_edges(colored_polys, idx)
                from shapely.geometry import LineString
                for edge in shared_edges:
                    if isinstance(edge, LineString):
                        coords = list(edge.coords)
                        if len(coords) == 2:
                            x1, y1 = coords[0]
                            x2, y2 = coords[1]
                            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                    elif hasattr(edge, 'geoms'):
                        for geom in edge.geoms:
                            coords = list(geom.coords)
                            if len(coords) == 2:
                                x1, y1 = coords[0]
                                x2, y2 = coords[1]
                                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.end()
        return image

