from __future__ import annotations

import csv
import itertools
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
    value: float
    depends_on: list[int] = field(default_factory=list)

    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth

    def orientations(self) -> list[tuple[float, float, float]]:
        return list(set(itertools.permutations((self.width, self.height, self.depth))))


def load_items(path=None):
    path = Path(path) if path else Path(__file__).with_name("items.csv")
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
                value=float(row["value"]),
                depends_on=deps,
            ))
    return items


SAMPLE_ITEMS: list[Item] = load_items()
