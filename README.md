# 3D Bin Packing with Dependencies

A student project for the Decision Making course comparing two solutions to a 3D bin packing problem: loading furniture boxes into trucks, with box dependencies. A genetic algorithm is compared with an exact CPLEX model, then run on a continuous stream of new boxes.

## Requirements

- Python 3.12
- Dependencies listed in `requirements.txt` (numpy)

```sh
pip install -r requirements.txt
```

A Nix flake (`flake.nix`) is also provided for a reproducible environment. It also includes MiKTeX for building the LaTeX report:

```sh
nix develop
```

The exact model needs IBM ILOG CPLEX Optimization Studio (not included).

## Problem

The factory keeps producing furniture, packed as rectangular boxes. One piece of furniture can take more than one box (e.g. a table top and its legs). Trucks are loaded gradually, and when a truck is full enough it leaves and can no longer be changed. A loading plan is feasible when:

- every box fits inside the truck and does not overlap other boxes (all 6 axis-aligned rotations are allowed),
- the truck's weight limit is not exceeded,
- a box travels in the same truck as every box it depends on.

The goal is to use as few trucks as possible.

## File structure

- `main.py` – entry point: runs the continuous-stream simulation, or the small comparison instance with `compare`.
- `src/config.py` – parameters: population size, number of generations, truck size, arrival and departure intervals, random seed.
- `src/items.py` – the `Item` dataclass (dimensions, weight, dependencies, rotations) and loading of `items.csv`.
- `src/items.csv` – 484 furniture boxes (`id,name,width,height,depth,weight,depends_on`, dependencies separated by `;`).
- `src/truck.py` – the `Truck` class (dimensions and weight limit).
- `src/packer.py` – the decoder that turns a box order into loaded trucks.
- `src/ga.py` – the genetic algorithm.
- `CPLEX/binpacking3d.mod` – the exact model in OPL.
- `CPLEX/binpacking3d.dat` – data for the exact model: the first 15 boxes from `items.csv`.
- `docs/raport.tex` / `docs/raport.pdf` – the report (in Polish), built with `build-raport`.

## Genetic algorithm

The algorithm does not assign boxes to trucks directly. It only optimises the order in which boxes are loaded, and a decoder (`packer.py`) builds the trucks from that order:

1. Boxes linked by dependencies are merged into groups that are always loaded together.
2. Each group goes into the first truck where it fits. If it fits in none, a new truck is opened.
3. Inside a truck, a box is placed at the first free corner point (back, then bottom, then left) and in the first rotation that fits without overlapping. Placing a box adds three new corner points.

Each individual is a permutation of box indices. Each generation keeps the 2 best individuals (elitism), and fills the rest of the population with parents picked by tournament selection (size 5) and mutated by swapping genes (probability 0.05 per gene).

### Continuous production

- Every `ARRIVAL_INTERVAL` generations, `ARRIVAL_COUNT` new boxes arrive. Their indices are appended to every individual, so the population keeps what it has already learnt.
- Every `DEPART_INTERVAL` generations, the fullest truck departs. Its boxes are marked as departed and the decoder skips them from then on.

The final result is the number of trucks that departed plus the trucks still being loaded.

## Exact model (CPLEX)

`binpacking3d.mod` is a mixed-integer model of the same problem. It minimises the number of used trucks, with binary variables for truck use, box-to-truck assignment and box rotation, continuous box positions, and big-M constraints that stop boxes in the same truck from overlapping. It also includes symmetry breaking (trucks are used in order).

The number of overlap variables grows with the square of the number of boxes, so CPLEX proves optimality only for a dozen or so boxes. That is why it is used only as a benchmark on a small instance.

## Usage

### Continuous-stream simulation

```sh
python main.py
```

With the default parameters, it starts with 10 boxes and receives 5 new ones every 10 generations (105 boxes over 200 generations). The fullest truck departs every 40 generations. The truck is a light delivery van: 180 × 200 × 300 cm (W × H × D), 1500 kg. It prints progress for each generation, then the contents of each truck with the position and size of every box.

The parameters can be changed in `src/config.py`.

### Comparison with CPLEX

```sh
python main.py compare
```

Runs the genetic algorithm on the first 15 boxes with no arrivals or departures, the same instance as `CPLEX/binpacking3d.dat`. The exact model can be run from CPLEX Optimization Studio or from the command line:

```sh
oplrun CPLEX/binpacking3d.mod CPLEX/binpacking3d.dat
```

### Report

```sh
build-raport
```

Available inside `nix develop`. Builds `docs/raport.pdf` from `docs/raport.tex`.
