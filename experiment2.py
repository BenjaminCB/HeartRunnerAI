import numpy as np
from heartrunner.settings import *
from heartrunner.core.types import *
from heartrunner.core.database import HeartrunnerDB


SAMPLE = 1000
ITER = 10
SELECTION = 20
RESULT_PATH = f"data/experiments/experiment2_2.csv"


def aed_choice(candidates: list[Candidate], num: int):
    sorted_by_a = sorted(candidates, key=lambda c: min(c.aed_costs()[0:num]))
    a_cost = 0
    for i in range(SELECTION):
        a_cost += min(sorted_by_a[i].aed_costs()[0:num])
    return a_cost/SELECTION


if __name__ == "__main__":
    with HeartrunnerDB.default() as db:
        db.delete_nodes(Runner)
        db.generate_entity(Runner, RUNNERS)
        
        a_costs = np.empty(shape=(ITER, SAMPLE))

        for i in range(SAMPLE):
            db.delete_nodes(Patient)
            patient = db.generate_entity(Patient)[0]
            radius = 1
            while True:
                candidates = db.get_pathfinder(patient, kilometers=radius).compute_candidates()
                if candidates: break
                radius += 0.5
                if radius > 2:
                    radius = 1
                    db.delete_nodes(Patient)
                    patient = db.generate_entity(Patient)[0]
            
            for j in range(ITER):
                a_costs[j][i] = aed_choice(candidates, j+1)
            
            np.savetxt(RESULT_PATH, a_costs.transpose(), delimiter=",")
            
        
