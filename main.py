import numpy as np

from src import config, packer
from src.ga import GeneticAlgorithm
from src.items import SAMPLE_ITEMS
from src.truck import Truck


def decode(order, items, truck):
    adj = packer.build_adjacency(items)
    gene_ids = [it.id for it in items]
    by_id = {it.id: it for it in items}
    return packer.pack(order, gene_ids, by_id, adj, truck)


def make_fitness(items, truck):
    adj = packer.build_adjacency(items)
    gene_ids = [it.id for it in items]
    by_id = {it.id: it for it in items}
    capacity = truck.volume

    def fitness(order):
        bins = packer.pack(order, gene_ids, by_id, adj, truck)
        return sum((b.used_volume / capacity) ** 2 for b in bins) / len(bins)

    return fitness


def report_solution(order, items, truck):
    bins = decode(order, items, truck)
    total_vol = truck.volume

    print(f"\n\nBoxes: {len(items)}")
    print(f"Trucks used: {len(bins)}")
    print("-" * 60)
    by_id = {it.id: it for it in items}
    for k, b in enumerate(bins, 1):
        fill = 100 * b.used_volume / total_vol
        load = 100 * b.weight / truck.max_weight
        print(f"\nTruck {k}: {len(b.contents)} boxes, weight: {load:.1f}%, volume: {fill:.1f}%")
        for item_id, (pos, dims) in sorted(b.contents.items()):
            x, y, z = (round(v) for v in pos)
            w, h, d = (round(v) for v in dims)
            print(f"  [{item_id}] {by_id[item_id].name:<24} pos=({x},{y},{z}) size=({w}x{h}x{d})")


def main():
    rng = np.random.default_rng(config.SEED)
    truck = Truck(config.TRUCK_WIDTH, config.TRUCK_HEIGHT,
                  config.TRUCK_DEPTH, config.TRUCK_MAX_WEIGHT)

    items = list(SAMPLE_ITEMS[:config.INITIAL_ITEMS])
    arrival_queue = list(SAMPLE_ITEMS[config.INITIAL_ITEMS:])

    ga = GeneticAlgorithm(
        n_genes=len(items),
        fitness_fn=make_fitness(items, truck),
        pop_size=config.POPULATION_SIZE,
        rng=rng,
    )

    for gen in range(1, config.GENERATIONS + 1):
        ga.step()
        score, best_order = ga.best()
        trucks = len(decode(best_order, items, truck))
        print(f"  [{gen}/{config.GENERATIONS}] boxes={ga.n_genes:>2} | trucks={trucks:>2} | fitness={score:.3f}")

        if (gen % config.ARRIVAL_INTERVAL == 0 and gen < config.GENERATIONS
                and arrival_queue):
            new_items = arrival_queue[:config.ARRIVAL_COUNT]
            del arrival_queue[:config.ARRIVAL_COUNT]
            items.extend(new_items)
            ga.grow(len(new_items), make_fitness(items, truck))
            print("\nNew items added")

    _, best_order = ga.best()
    report_solution(best_order, items, truck)


if __name__ == "__main__":
    main()
