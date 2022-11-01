import pytest
import numpy as np
from heartrunner.neuralnetwork import NeuralNetwork


@pytest.fixture
def nn():
    return NeuralNetwork()


def test_mutate_rate(nn: NeuralNetwork):
    full_mutation = nn.mutate(rate=1, amount=1)
    zero_mutation = nn.mutate(rate=0, amount=1)

    nnw, nfw, nzw = nn.model.get_weights(), full_mutation.model.get_weights(), zero_mutation.model.get_weights()
    for i in range(len(nnw)):
        zero_diff: np.ndarray = nnw[i]-nzw[i]
        assert not zero_diff.any()

        full_diff: np.ndarray = nnw[i]-nfw[i]
        assert full_diff.all()


def test_mutate_amount(nn: NeuralNetwork):
    pass


def test_crossover():
    pass

