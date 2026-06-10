from collections import defaultdict, deque


class Bin:
    def __init__(self, truck):
        self.truck = truck
        self.placed = []
        self.points = [(0.0, 0.0, 0.0)]
        self.weight = 0.0
        self.contents = {}

    def _in_bounds(self, pos, dims):
        return (pos[0] + dims[0] <= self.truck.width and
                pos[1] + dims[1] <= self.truck.height and
                pos[2] + dims[2] <= self.truck.depth)

    @staticmethod
    def _overlaps(a_pos, a_dims, b_pos, b_dims):
        for i in range(3):
            if a_pos[i] + a_dims[i] <= b_pos[i] or b_pos[i] + b_dims[i] <= a_pos[i]:
                return False
        return True

    def _try_one(self, item):
        if self.weight + item.weight > self.truck.max_weight:
            return False

        chosen = None
        for p in sorted(self.points, key=lambda q: (q[2], q[1], q[0])):
            for dims in item.orientations():
                if not self._in_bounds(p, dims):
                    continue
                if any(self._overlaps(p, dims, pp, pd) for pp, pd in self.placed):
                    continue
                chosen = (p, dims)
                break
            if chosen is not None:
                break

        if chosen is None:
            return False

        pos, dims = chosen
        self.placed.append((pos, dims))
        self.contents[item.id] = (pos, dims)
        self.weight += item.weight

        x, y, z = pos
        w, h, d = dims
        if pos in self.points:
            self.points.remove(pos)
        for new_p in ((x + w, y, z), (x, y + h, z), (x, y, z + d)):
            if new_p not in self.points:
                self.points.append(new_p)
        return True

    def add_group(self, items):
        snapshot = (list(self.placed), list(self.points),
                    self.weight, dict(self.contents))
        for item in sorted(items, key=lambda it: it.volume, reverse=True):
            if not self._try_one(item):
                self.placed, self.points, self.weight, self.contents = snapshot
                return False
        return True

    @property
    def used_volume(self) -> float:
        return sum(d[0] * d[1] * d[2] for _, d in self.contents.values())


def build_adjacency(items):
    present = {it.id for it in items}
    adj = defaultdict(set)
    for it in items:
        for dep in it.depends_on:
            if dep in present:
                adj[it.id].add(dep)
                adj[dep].add(it.id)
    return adj


def component(start, adj):
    seen = {start}
    queue = deque([start])
    while queue:
        for nb in adj.get(queue.popleft(), ()):
            if nb not in seen:
                seen.add(nb)
                queue.append(nb)
    return seen


def pack(order, gene_ids, by_id, adj, truck):
    assigned = set()
    bins = []
    for g in order:
        iid = gene_ids[int(g)]
        if iid in assigned:
            continue
        comp = component(iid, adj)
        group = [by_id[c] for c in comp]
        if not any(b.add_group(group) for b in bins):
            new_bin = Bin(truck)
            new_bin.add_group(group)
            bins.append(new_bin)
        assigned |= comp
    return bins
