import itertools
from random import randrange

class Runner:
    id_iter = itertools.count(1)

    def __init__(self):
        self.id = next(self.id_iter)
        self.speed = randrange(3,6)     # random number from 3-5

    def create_node(self):
        return f"CREATE (p:Runner {{id: {self.id}, speed: {self.speed}}})"
