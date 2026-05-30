from __future__ import annotations

import numpy as np

from src import config
from src.ga import GeneticAlgorithm
from src.items import SAMPLE_ITEMS
from src.truck import Truck


def make_fitness(items, truck):
    id_to_item = {it.id: it for it in items}
    gene_ids = [it.id for it in items]

    def fitness(chromosome):
        selected = {gene_ids[i] for i, bit in enumerate(chromosome) if bit}

        stack = list(selected)
        while stack:
            for dep in id_to_item[stack.pop()].depends_on:
                if dep in id_to_item and dep not in selected:
                    selected.add(dep)
                    stack.append(dep)

        subset = sorted((id_to_item[i] for i in selected),
                        key=lambda it: it.value / it.volume, reverse=True)
        placement, _weight = truck.pack(subset)
        packed = set(placement)

        changed = True
        while changed:
            changed = False
            for i in list(packed):
                if any(dep not in packed for dep in id_to_item[i].depends_on):
                    packed.discard(i)
                    changed = True

        return sum(id_to_item[i].value for i in packed)

    return fitness


def report_solution(chromosome, items, truck):
    fitness = make_fitness(items, truck)
    value = fitness(chromosome)

    id_to_item = {it.id: it for it in items}
    gene_ids = [it.id for it in items]
    selected = {gene_ids[i] for i, bit in enumerate(chromosome) if bit}
    stack = list(selected)
    while stack:
        for dep in id_to_item[stack.pop()].depends_on:
            if dep in id_to_item and dep not in selected:
                selected.add(dep)
                stack.append(dep)
    subset = sorted((id_to_item[i] for i in selected),
                    key=lambda it: it.value / it.volume, reverse=True)
    placement, weight = truck.pack(subset)

    truck_vol = truck.width * truck.height * truck.depth
    used_vol = sum(id_to_item[i].volume for i in placement)

    print("\n" + "=" * 60)
    print("FINAL LOADING PLAN")
    print("=" * 60)
    print(f"Boxes loaded : {len(placement)} / {len(items)} in catalogue")
    print(f"Total value  : {value:.0f}")
    print(f"Total weight : {weight:.0f} / {truck.max_weight} kg "
          f"({100 * weight / truck.max_weight:.1f}%)")
    print(f"Volume used  : {100 * used_vol / truck_vol:.1f}% of trailer")
    print("-" * 60)
    for item_id, (pos, dims) in sorted(placement.items()):
        it = id_to_item[item_id]
        x, y, z = (round(v) for v in pos)
        w, h, d = (round(v) for v in dims)
        print(f"  [{item_id:>3}] {it.name:<22} pos=({x:>4},{y:>4},{z:>5}) "
              f"size=({w}x{h}x{d}) val={it.value:.0f}")
    print("=" * 60)


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
        cx_prob=config.CROSSOVER_PROB,
        mut_prob=config.MUTATION_PROB,
        tournament_size=config.TOURNAMENT_SIZE,
        elitism=config.ELITISM,
        rng=rng,
    )

    print(f"Truck: {truck.width}x{truck.height}x{truck.depth} cm, "
          f"max {truck.max_weight} kg")
    print(f"Starting catalogue: {len(items)} items\n")

    for gen in range(1, config.GENERATIONS + 1):
        ga.step()
        best_val, _ = ga.best()
        avg = ga.fitnesses.mean()
        print(f"Gen {gen:>3}/{config.GENERATIONS} | "
              f"items={ga.n_genes:>2} | best={best_val:>6.0f} | avg={avg:>6.0f}")

        if (gen % config.ARRIVAL_INTERVAL == 0 and gen < config.GENERATIONS
                and arrival_queue):
            new_items = arrival_queue[:config.ARRIVAL_COUNT]
            del arrival_queue[:config.ARRIVAL_COUNT]
            items.extend(new_items)
            ga.grow(len(new_items), make_fitness(items, truck))
            names = ", ".join(it.name for it in new_items)
            print(f"    >> ARRIVAL: {len(new_items)} new boxes -> {names}")

    _, best_chrom = ga.best()
    report_solution(best_chrom, items, truck)


if __name__ == "__main__":
    main()
