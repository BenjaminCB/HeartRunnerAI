import numpy as np
from heartrunner.settings import *
from heartrunner.core.types import *
from heartrunner.core.database import HeartrunnerDB


SAMPLE = 1000
RUNNERS = 2000
CANDIDATE_RUNNERS = 20
CANDIDATE_AEDS = 1
SELECTION = 5
RESULT_PATH = "data/experiments/experiment1.csv"


def proximity_choice(candidates: list[Candidate]):
    p_cost, a_cost = 0, 0
    for i in range(SELECTION):
        p_cost += candidates[i].patient_cost()
        a_cost += min(candidates[i].aed_costs())
    return p_cost/SELECTION, a_cost/SELECTION


def path_choice(candidates: list[Candidate]):
    sorted_by_r = sorted(candidates, key=lambda c: c.patient_cost())
    sorted_by_a = sorted(candidates, key=lambda c: min(c.aed_costs()))
    p_cost, a_cost = 0, 0
    for i in range(SELECTION):
        p_cost += sorted_by_r[i].patient_cost()
        a_cost += min(sorted_by_a[i].aed_costs())
    return p_cost/SELECTION, a_cost/SELECTION


if __name__ == "__main__":
    with HeartrunnerDB.default() as db:
        db.delete_nodes(Runner)
        db.generate_entity(Runner, RUNNERS)

        p_cost_proximity = np.empty(SAMPLE)
        a_cost_proximity = np.empty(SAMPLE)
        p_cost_path = np.empty(SAMPLE)
        a_cost_path = np.empty(SAMPLE)

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
                
            p_cost_proximity[i], a_cost_proximity[i] = proximity_choice(candidates)
            p_cost_path[i], a_cost_path[i] = path_choice(candidates)

            print(
                f"{i+1:-4}: "
                f"p_costs: {p_cost_proximity[i]:.2f}    {p_cost_path[i]:.2f} "
                f"a_costs: {a_cost_proximity[i]:.2f}    {a_cost_path[i]:.2f} "
            )

        results = np.array([p_cost_proximity, p_cost_path, a_cost_proximity, a_cost_path]).transpose()
        np.savetxt(RESULT_PATH, results, delimiter=',')
            
        
