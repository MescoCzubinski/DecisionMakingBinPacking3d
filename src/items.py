import csv
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Item:
    id: int
    name: str
    width: float
    height: float
    depth: float
    weight: float
    depends_on: list[int] = field(default_factory=list)

    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth

    def orientations(self) -> list[tuple[float, float, float]]:
        w, h, d = self.width, self.height, self.depth
        return list({(w, h, d), (w, d, h), (h, w, d), (h, d, w), (d, w, h), (d, h, w)})


def load_items():
    path = Path(__file__).with_name("items.csv")
    items = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            deps = [int(x) for x in row["depends_on"].split(";") if x.strip()]
            items.append(Item(
                id=int(row["id"]),
                name=row["name"],
                width=float(row["width"]),
                height=float(row["height"]),
                depth=float(row["depth"]),
                weight=float(row["weight"]),
                depends_on=deps,
            ))
    return items


SAMPLE_ITEMS: list[Item] = load_items()
