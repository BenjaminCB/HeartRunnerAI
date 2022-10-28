from __future__ import annotations
import tensorflow as tf
import numpy as np
from random import uniform


class NeuralNetwork:
    def __init__(self, layers):
        # l1 = tf.keras.layers.Dense(layers, input_shape=(layers,), activation='relu'),
        # l2 = tf.keras.layers.Dense(layers, activation='sigmoid')
        self.model = tf.keras.Sequential([
            # tf.keras.layers.InputLayer(input_shape=(layers,)),
            tf.keras.layers.Dense(layers[1], input_shape=(layers[0],), activation='relu'),
            tf.keras.layers.Dense(layers[2])
        ])
        self.layers = layers
        self.model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

    # Given the model is trained, outputs prediction(s) [( , ), ( , ) ...].
    def predict(self, x: np.ndarray):
        x = x.reshape((1, self.layers[0]))
        prediction_each_neuron = self.model.predict(x)
        pre_sorted = []
        
        # index each prediction
        for i in range(0, len(prediction_each_neuron[0]), 1):
            pre_sorted.append((i, prediction_each_neuron[0][i]))

        # sort by [( 2. , 1. )]
        pre_sorted = sorted(pre_sorted, key=lambda x: x[1], reverse=True)
        return pre_sorted

    # the method should not mutate the current nn but instead return a new one
    def mutate(self, m_rate: float, m_amount: float):
        weights = self.model.get_weights()
        mutator = np.vectorize(lambda w: w if uniform(0, 1) < m_rate else w + uniform(-1 * m_amount, m_amount))
        # mutated = NeuralNetwork(self.layers).model.set_weights(list(map(mutator, weights)))
        mutated = NeuralNetwork(self.layers)
        mutated.model.set_weights(list(map(mutator, weights)))
        return mutated

    # method should perform a crossover of the nns and the inverse of that crossover and return them
    @staticmethod
    def crossover(p1: NeuralNetwork, p2: NeuralNetwork, c_rate):
        p1w, p2w = p1.model.get_weights(), p2.model.get_weights()

        for i in range(len(p1w)):
            if uniform(0, 1) > c_rate:
                p1w[i], p2w[i] = p2w[i], p1w[i]

        p1.model.set_weights(p1w)
        p2.model.set_weights(p2w)

        return [p1, p2]
