import itertools

class Patient:
    id_iter = itertools.count(1)

    def __init__(self):
        self.id = next(self.id_iter)
