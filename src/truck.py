
class Truck:
    def __init__(self, width, height, depth, max_weight):
        self.width = width
        self.height = height
        self.depth = depth
        self.max_weight = max_weight

    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth
