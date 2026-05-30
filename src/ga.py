from __future__ import annotations

import numpy as np


class GeneticAlgorithm:
    def __init__(self, n_genes, fitness_fn, *, pop_size, cx_prob, mut_prob,
                 tournament_size, elitism, rng):
        self.n_genes = n_genes
        self.fitness_fn = fitness_fn
        self.pop_size = pop_size
        self.cx_prob = cx_prob
        self.mut_prob = mut_prob
        self.tournament_size = tournament_size
        self.elitism = elitism
        self.rng = rng

        self.population = [
            self.rng.integers(0, 2, size=n_genes, dtype=np.int8)
            for _ in range(pop_size)
        ]
        self.fitnesses = self._evaluate(self.population)

    def _evaluate(self, population):
        return np.array([self.fitness_fn(ind) for ind in population], dtype=float)

    def _tournament(self):
        idx = self.rng.integers(0, self.pop_size, size=self.tournament_size)
        best = idx[np.argmax(self.fitnesses[idx])]
        return self.population[best]

    def _crossover(self, a, b):
        if self.rng.random() >= self.cx_prob or self.n_genes < 2:
            return a.copy(), b.copy()
        point = int(self.rng.integers(1, self.n_genes))
        c1 = np.concatenate([a[:point], b[point:]])
        c2 = np.concatenate([b[:point], a[point:]])
        return c1, c2

    def _mutate(self, ind):
        flips = self.rng.random(self.n_genes) < self.mut_prob
        ind[flips] ^= 1
        return ind

    def step(self):
        elite_idx = np.argsort(self.fitnesses)[::-1][:self.elitism]
        new_pop = [self.population[i].copy() for i in elite_idx]

        while len(new_pop) < self.pop_size:
            p1 = self._tournament()
            p2 = self._tournament()
            c1, c2 = self._crossover(p1, p2)
            new_pop.append(self._mutate(c1))
            if len(new_pop) < self.pop_size:
                new_pop.append(self._mutate(c2))

        self.population = new_pop
        self.fitnesses = self._evaluate(self.population)

    def grow(self, n_new, fitness_fn):
        self.n_genes += n_new
        self.fitness_fn = fitness_fn
        self.population = [
            np.concatenate([ind, np.zeros(n_new, dtype=np.int8)])
            for ind in self.population
        ]
        self.fitnesses = self._evaluate(self.population)

    def best(self):
        i = int(np.argmax(self.fitnesses))
        return self.fitnesses[i], self.population[i]
