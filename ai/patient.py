import itertools

class Patient:
    id_iter = itertools.count(1)

    def __init__(self):
        self.id = next(self.id_iter)

    def create_node(self):
        return f"CREATE (p:Patient {{id: {self.id}}})"

    def row2patient(row):
        return {"id": row["p"]["id"]}
