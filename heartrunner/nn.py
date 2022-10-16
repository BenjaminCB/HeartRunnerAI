from tensorflow import keras


class NeuralNetwork:
    def __init__(self, layer_sizes: list[int]):
        self.model = keras.Sequential([
            keras.layers.Dense(layer_sizes[1], input_shape=layer_sizes[0], activation='relu'),
            keras.layers.Dense(layer_sizes[2], activation='sigmoid')
        ])

        self.model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

    # TODO should probably do some post processing to make the prediction more human readable
    def predict(self, x):
        return self.model.predict(x)

    # TODO implement noise
    # the method should not mutate the current nn but instead return a new one
    @staticmethod
    def mutate(nn, m_rate):
        pass

    # TODO implement crossover
    # method should perform a crossover of the nns and the inverse of that crossover and return them
    @staticmethod
    def crossover(p1, p2, c_rate):
        return [p1, p2]
