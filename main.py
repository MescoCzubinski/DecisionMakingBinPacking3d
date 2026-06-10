import numpy as np

from src import config, packer
from src.ga import GeneticAlgorithm
from src.items import SAMPLE_ITEMS
from src.truck import Truck


def fitness(order, items, truck, departed):
    groups = packer.build_groups(items, departed)
    gene_ids = [it.id for it in items]
    by_id = {it.id: it for it in items}
    bins = packer.pack(order, gene_ids, by_id, groups, truck, departed)
    capacity = truck.volume
    return sum((b.used_volume / capacity) ** 2 for b in bins) / len(bins)


def report_solution(order, items, truck, departed, shipped):
    groups = packer.build_groups(items, departed)
    gene_ids = [it.id for it in items]
    by_id = {it.id: it for it in items}
    bins = packer.pack(order, gene_ids, by_id, groups, truck, departed)
    total_vol = truck.volume
    all_bins = shipped + bins

    print(f"\n\nBoxes: {len(items)}")
    print(f"Trucks used: {len(all_bins)}  ({len(shipped)} shipped, {len(bins)} loading)")
    print("-" * 60)
    for k, b in enumerate(all_bins, 1):
        fill = 100 * b.used_volume / total_vol
        load = 100 * b.weight / truck.max_weight
        print(f"\nTruck {k}: {len(b.contents)} boxes, weight: {load:.1f}%, volume: {fill:.1f}%")

        for item_id, (pos, dims) in sorted(b.contents.items()):
            x, y, z = (round(v) for v in pos)
            w, h, d = (round(v) for v in dims)
            print(f"  [{item_id}] {by_id[item_id].name:<24} pos=({x},{y},{z}) size=({w}x{h}x{d})")


def main():
    rng = np.random.default_rng(config.SEED)
    truck = Truck(config.TRUCK_WIDTH, config.TRUCK_HEIGHT, config.TRUCK_DEPTH, config.TRUCK_MAX_WEIGHT)

    items = list(SAMPLE_ITEMS[:config.INITIAL_ITEMS])
    arrival_queue = list(SAMPLE_ITEMS[config.INITIAL_ITEMS:])
    departed_ids = set()
    shipped = []

    ga = GeneticAlgorithm(
        n_genes=len(items),
        fitness_fn=lambda order: fitness(order, items, truck, departed_ids),
        pop_size=config.POPULATION_SIZE,
        rng=rng,
    )

    for gen in range(1, config.GENERATIONS + 1):
        ga.step()
        score, best_order = ga.best()
        bins = packer.pack(best_order, [it.id for it in items], {it.id: it for it in items}, packer.build_groups(items, departed_ids), truck, departed_ids)
        print(f"  [{gen}/{config.GENERATIONS}] boxes={ga.n_genes:>2} | trucks={len(bins):>2} | fitness={score:.3f}")

        if (gen % config.ARRIVAL_INTERVAL == 0 and gen < config.GENERATIONS and arrival_queue):
            new_items = arrival_queue[:config.ARRIVAL_COUNT]
            arrival_queue = arrival_queue[config.ARRIVAL_COUNT:]
            items.extend(new_items)
            ga.grow(len(new_items), lambda order: fitness(order, items, truck, departed_ids))
            print("\nNew items added")

        if gen % config.DEPART_INTERVAL == 0 and bins:
            fullest = max(bins, key=lambda b: b.used_volume)
            shipped.append(fullest)
            departed_ids.update(fullest.contents)
            print(f"Truck departed: {len(fullest.contents)} boxes, {100 * fullest.used_volume / truck.volume:.1f}% full")

    _, best_order = ga.best()
    report_solution(best_order, items, truck, departed_ids, shipped)


if __name__ == "__main__":
    main()
