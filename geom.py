import math
import random
from typing import List
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union

def generate_lines(width, height, count=20) -> List[LineString]:
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

def create_regions(w: float, h:float, lines: List[LineString]) -> List[Polygon]:
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

def regions_in(regions: List[Polygon], partial_regions: List[Polygon], tolerance: float = 1e-8) -> bool:
    for pr in partial_regions:
        if not any(pr.equals_exact(r, tolerance) for r in regions):
            return False
    return True
