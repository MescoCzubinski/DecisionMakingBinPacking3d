import numpy as np

CROSSOVER_PROB = 0.8
MUTATION_PROB = 0.05
TOURNAMENT_SIZE = 4
ELITISM = 2


class GeneticAlgorithm:
    def __init__(self, n_genes, fitness_fn, pop_size, rng):
        self.n_genes = n_genes
        self.fitness_fn = fitness_fn
        self.pop_size = pop_size
        self.rng = rng

        self.population = [rng.permutation(n_genes) for _ in range(pop_size)]
        self.fitnesses = self._evaluate(self.population)

    def _evaluate(self, population):
        return np.array([self.fitness_fn(ind) for ind in population], dtype=float)

    def _tournament(self):
        contenders = self.rng.integers(0, self.pop_size, size=TOURNAMENT_SIZE)
        winner = contenders[np.argmax(self.fitnesses[contenders])]
        return self.population[winner]

    def _ox(self, a, b):
        n = self.n_genes
        i, j = sorted(int(v) for v in self.rng.integers(0, n + 1, size=2))
        child = np.full(n, -1, dtype=a.dtype)
        child[i:j] = a[i:j]
        taken = set(a[i:j].tolist())
        fill = (x for x in b.tolist() if x not in taken)
        for pos in range(n):
            if child[pos] == -1:
                child[pos] = next(fill)
        return child

    def _crossover(self, a, b):
        if self.rng.random() >= CROSSOVER_PROB or self.n_genes < 2:
            return a.copy(), b.copy()
        return self._ox(a, b), self._ox(b, a)

    def _mutate(self, ind):
        for pos in range(self.n_genes):
            if self.rng.random() < MUTATION_PROB:
                swap = int(self.rng.integers(0, self.n_genes))
                ind[pos], ind[swap] = ind[swap], ind[pos]
        return ind

    def step(self):
        ranked_best_first = np.argsort(self.fitnesses)[::-1]
        elite_idx = ranked_best_first[:ELITISM]
        new_pop = [self.population[i].copy() for i in elite_idx]

        while len(new_pop) < self.pop_size:
            parent1 = self._tournament()
            parent2 = self._tournament()
            child1, child2 = self._crossover(parent1, parent2)
            new_pop.append(self._mutate(child1))
            if len(new_pop) < self.pop_size:
                new_pop.append(self._mutate(child2))

        self.population = new_pop
        self.fitnesses = self._evaluate(self.population)

    def grow(self, n_new, fitness_fn):
        new_genes = np.arange(self.n_genes, self.n_genes + n_new)
        self.n_genes += n_new
        self.fitness_fn = fitness_fn
        self.population = [np.concatenate([ind, new_genes]) for ind in self.population]
        self.fitnesses = self._evaluate(self.population)

    def best(self):
        i = int(np.argmax(self.fitnesses))
        return self.fitnesses[i], self.population[i]
