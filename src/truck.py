from __future__ import annotations


class Truck:
    def __init__(self, width, height, depth, max_weight):
        self.width = width
        self.height = height
        self.depth = depth
        self.max_weight = max_weight

    def _in_bounds(self, pos, dims):
        x, y, z = pos
        w, h, d = dims
        return (x + w <= self.width and
                y + h <= self.height and
                z + d <= self.depth)

    @staticmethod
    def _overlaps(a_pos, a_dims, b_pos, b_dims):
        for i in range(3):
            if a_pos[i] + a_dims[i] <= b_pos[i] or b_pos[i] + b_dims[i] <= a_pos[i]:
                return False
        return True

    def pack(self, items):
        placed = []
        placement = {}
        weight = 0.0
        points = [(0.0, 0.0, 0.0)]

        for item in items:
            if weight + item.weight > self.max_weight:
                continue

            chosen = None
            for p in sorted(points, key=lambda q: (q[2], q[1], q[0])):
                for dims in item.orientations():
                    if not self._in_bounds(p, dims):
                        continue
                    if any(self._overlaps(p, dims, pp, pd) for pp, pd in placed):
                        continue
                    chosen = (p, dims)
                    break
                if chosen is not None:
                    break

            if chosen is None:
                continue

            pos, dims = chosen
            placed.append((pos, dims))
            placement[item.id] = (pos, dims)
            weight += item.weight

            x, y, z = pos
            w, h, d = dims
            if pos in points:
                points.remove(pos)
            for new_p in ((x + w, y, z), (x, y + h, z), (x, y, z + d)):
                if new_p not in points:
                    points.append(new_p)

        return placement, weight
