from tensorflow import keras
from random import uniform
import numpy as np


class NeuralNetwork:
    def __init__(self, layers):
        # keras.layers.Dense(layer_sizes[1], input_shape=layer_sizes[0], activation='relu'),
        # keras.layers.Dense(layer_sizes[2], activation='sigmoid')
        self.model = keras.Sequential(layers)

        self.model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

    # Given the model is trained, outputs prediction(s) [( , ), ( , ) ...].
    def predict(self, x):
        prediction_each_neuron = self.model.predict(x)
        prediction_each_neuron = numpy.array(prediction_each_neuron)
        pre_sorted = []
        
        # index each prediction
        for i in range(0, len(prediction_each_neuron), 1):
            for j in range(0, len(prediction_each_neuron[0]), 1):
                pre_sorted.append((i, prediction_each_neuron[i][j]))

        # sort by [( 2. , 1. )]
        pre_sorted = sorted(sorted(pre_sorted, key=lambda x: x[1], reverse=True), key=lambda x: float(x[0]))
        return pre_sorted

    # the method should not mutate the current nn but instead return a new one
    def mutate(self, m_rate: float):
        weights = np.array(self.model.get_weights())
        mutator = np.vectorize(lambda w: w if uniform(0, 1) < m_rate else w * uniform(-0.1, 0.1))
        self.model.set_weights(mutator(weights))

    # TODO implement crossover (look at the keras model saving and serialization API)
    # method should perform a crossover of the nns and the inverse of that crossover and return them
    @staticmethod
    def crossover(p1, p2, c_rate):
        p1w, p2w = p1.get_weights(), p2.get_weights()
        c1w = np.empty(np.shape(p1w))
        c2w = np.empty(np.shape(p1w))

        for i in range(p1w.size):
            if uniform(0, 1) < c_rate:
                c1w[i] = p1w[i]
                c2w[i] = p2w[i]
            else:
                c1w[i] = p2w[i]
                c2w[i] = p1w[i]

        return p1.set_weights(c1w), p2.set_weights(c2w)
