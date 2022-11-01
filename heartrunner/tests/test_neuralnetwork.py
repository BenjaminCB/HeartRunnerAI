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
    amount = 1
    mutated = nn.mutate(rate=1, amount=amount)
    nnw, mnw = nn.model.get_weights(), mutated.model.get_weights()
    for i in range(len(nnw)):
        diff: np.ndarray = abs(nnw[i]-mnw[i])
        assert diff.max() <= amount


def test_crossover(nn: NeuralNetwork):
    nn1 = nn
    nn2 = nn.mutate(rate=1, amount=1)
    w1, w2 = nn1.model.get_weights(), nn2.model.get_weights()
    
    # Full crossover
    NeuralNetwork.crossover(nn1, nn2, rate=1)
    nw1, nw2 = nn1.model.get_weights(), nn2.model.get_weights()
    
    # No crossover
    NeuralNetwork.crossover(nn1, nn2, rate=0)
    nnw1, nnw2 = nn1.model.get_weights(), nn2.model.get_weights()

    for i in range(len(w1)):
        assert np.all(w1[i]==nw2[i]) and np.all(w2[i]==nw1[i])
        assert np.all(nw1[i]==nnw1[i]) and np.all(nw2[i]==nnw2[i])
