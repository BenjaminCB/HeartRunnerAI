import random as rand
from .database import HeartrunnerDB
from .environment import Environment
from .types import Task, NodeType
from .nn import NeuralNetwork
from datetime import datetime, timedelta
from joblib import Parallel, delayed


def generate_tasks():
    initial_time = datetime.now()
    task_chance = 0.0001
    task_times = []
    for i in range(86400):
        if rand.random() < task_chance:
            task_times.append(i)
    task_count = len(task_times)

    tasks = []
    with HeartrunnerDB.default() as db:
        db.delete_nodes(NodeType.Patient)
        patients = db.generate_patients(task_count)
        for i in range(task_count):
            paths = db.get_pathfinder(patients[i], kilometers=2).compute_paths(n_runners=20, n_aeds=1)
            time = initial_time + timedelta(seconds=task_times[i])
            tasks.append(Task(paths, time))

    return tasks


class Evolution:
    def __init__(self, n_pop, n_iter, layers, m_rate, m_amount, c_rate, n_runner):
        self.n_pop = n_pop
        self.n_iter = n_iter
        self.m_rate = m_rate
        self.m_amount = m_amount
        self.c_rate = c_rate
        self.n_runner = n_runner
        self.tasks = []

        neural_net = NeuralNetwork(layers=layers)
        self.pop = [neural_net.mutate(m_rate, m_amount) for _ in range(n_pop)]

    # run evolution algorithm
    def evolve(self):
        all_scores = []
        for gen in range(self.n_iter):
            print(gen+1)
            # TODO generate a new batch of tasks
            self.tasks = generate_tasks()
            # scores = Parallel(n_jobs=4)(delayed(self._objective)(c) for c in self.pop)
            scores = [self._objective(c) for c in self.pop]
            all_scores.append(scores)
            selected = [self._selection(scores) for _ in range(self.n_pop)]
            self.pop = self._next_generation(selected)
            self.m_amount *= 0.75
        return all_scores

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
            for child in NeuralNetwork.crossover(p1, p2, self.c_rate):
                children.append(child.mutate(self.m_rate, self.m_amount))
        return children

    # calculate the reward
    # TODO perform the tasks in an environment
    # return a score based on the final state probably just the max latency
    def _objective(self, child):
        environment = Environment(child, self.n_runner)
        environment.enqueue_tasks(self.tasks)
        environment.process_tasks()
        return environment.score

    # Tournament style selection pick k random scores return the nn with the lowest score
    def _selection(self, scores, k=3):
        selection_index = rand.randint(0, self.n_pop-1)
        for i in [rand.randint(0, self.n_pop-1) for _ in range(k - 1)]:
            if scores[i] < scores[selection_index]:
                selection_index = i
        return self.pop[selection_index]
