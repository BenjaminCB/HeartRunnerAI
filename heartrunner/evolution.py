import nn as nn
import environment as env
import random as rand


class Evolution:
    def __init__(self, n_pop, n_iter, input_size, m_rate, c_rate, n_runner):
        self.n_pop = n_pop
        self.n_iter = n_iter
        self.m_rate = m_rate
        self.c_rate = c_rate
        self.n_runner = n_runner
        self.tasks = []

        neural_net = nn.NeuralNetwork(input_size)
        self.pop = [nn.NeuralNetwork.mutate(neural_net, m_rate) for _ in range(n_pop)]

    # run evolution algorithm
    def evolve(self):
        for gen in range(self.n_iter):
            # TODO generate a new batch of tasks
            self.tasks = []
            scores = [self._objective(c) for c in self.pop]
            selected = [self._selection(scores) for _ in range(self.n_pop)]
            self.pop = self._next_generation(selected)

    # get the best nn from the current population
    def best(self):
        res = self.pop[0]
        best_score = self._objective(res)
        for i in range(self.n_pop):
            score = self._objective(i)
            if score < best_score:
                res = i
                best_score = score
        return res

    # generate the next generation
    def _next_generation(self, parents):
        children = []
        for i in range(0, self.n_pop, 2):
            p1, p2 = parents[i], parents[i + 1]
            for child in nn.NeuralNetwork.crossover(p1, p2, self.c_rate):
                children.append(child.mutate(self.m_rate))
        return children

    # calculate the reward
    # TODO perform the tasks in an environment
    # return a score based on the final state probably just the max latency
    def _objective(self, child):
        environment = env.Environment(child, self.n_runner)
        environment.enqueue_tasks(self.tasks)
        environment.process_tasks()
        return environment.score

    # Tournament style selection pick k random scores return the nn with the lowest score
    def _selection(self, scores, k=3):
        selection_index = rand.randint(0, self.n_pop)
        for i in [rand.randint(0, self.n_pop) for _ in range(k - 1)]:
            if scores[i] < scores[selection_index]:
                selection_index = i
        return self.pop[selection_index]
