from __future__ import annotations
import numpy as np
from random import uniform
from keras import layers, models
from heartrunner.settings import *


class NeuralNetwork:
    def __init__(
        self, 
        input_size=NN_INPUT, 
        hidden_size=NN_HIDDEN, 
        output_size=NN_OUTPUT
    ):
        self.model = models.Sequential([
            layers.Dense(hidden_size, activation='relu', input_shape=(input_size,)),
            layers.Dense(output_size, activation='softmax')
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
        cross_weights = np.vectorize(lambda w1, w2: w1 if uniform(0, 1) > rate else w2)
        n1.model.set_weights(list(map(cross_weights, n1w, n2w)))
        n2.model.set_weights(list(map(cross_weights, n2w, n1w)))
        return [n1, n2]

