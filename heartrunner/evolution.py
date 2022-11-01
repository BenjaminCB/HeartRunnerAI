import numpy as np
from heartrunner.settings import *
from heartrunner.neuralnetwork import NeuralNetwork

class Evolution:
    def __init__(
        self,
        generations: int = GENERATIONS,
        population_size: int = POPULATION_SIZE,
        mutation_rate: float = MUTATION_RATE,
        mutation_amount: float = MUTATION_AMOUNT,
        crossover_rate: float = CROSSOVER_RATE
    ):
        self._m_rate = mutation_rate
        self._m_amount = mutation_amount
        self._c_rate = crossover_rate
        self._iterations = generations
        self._pop_size = population_size
        self._nn = NeuralNetwork()

    def run(self):
        for iteration in range(self._iterations):
            children = [self._nn.mutate(self._m_rate, self._m_amount)]
            rewards = np.zeros(self._pop_size)

            for child in children:
                # Evaluate child
                pass

            gain = rewards-rewards.mean()

