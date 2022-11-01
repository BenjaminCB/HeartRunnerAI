from __future__ import annotations
import numpy as np
from random import uniform
from keras import layers, models
from heartrunner.settings import NN_INPUT, NN_OUTPUT


class NeuralNetwork:
    def __init__(self):
        self.model = models.Sequential([
            layers.Dense(NN_INPUT, activation='relu', input_shape=(NN_INPUT,)),
            layers.Dense(NN_OUTPUT, activation='softmax')
        ])

    def predict(self):
        pass

    def mutate(self, rate: float, amount: float):
        weights = self.model.get_weights()
        mutator = np.vectorize(lambda w: w if uniform(0, 1) > rate else w + uniform(-amount, amount))
        mutated = NeuralNetwork()
        mutated.model.set_weights(list(map(mutator, weights)))
        return mutated

    @staticmethod
    def crossover(n1: NeuralNetwork, n2: NeuralNetwork, rate: float):
        n1w, n2w = n1.model.get_weights(), n2.model.get_weights()
        for i in range(len(n1w)):
            if uniform(0, 1) < rate:
                n1w[i], n2w[i] = n2w[i], n1w[i]
        n1.model.set_weights(n1w)
        n2.model.set_weights(n2w)
        return [n1, n2]

