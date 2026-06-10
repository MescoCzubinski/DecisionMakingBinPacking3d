import numpy as np

MUTATION_PROB = 0.05
TOURNAMENT_SIZE = 5
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
            parent = self._tournament()
            new_pop.append(self._mutate(parent.copy()))

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
