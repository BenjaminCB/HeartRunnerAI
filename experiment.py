import numpy as np
from heartrunner.settings import *
from heartrunner.core.types import *
from heartrunner.core.database import HeartrunnerDB


SAMPLE = 100


def proximity_choice(candidates: list[Candidate]):
    p_cost = candidates[0].patient_cost()
    a_cost = min(candidates[1].aed_costs())
    return p_cost + a_cost


def greedy_choice(candidates: list[Candidate]):
    p = []
    a = []
    for c in candidates:
        p.append((c.patient_cost(), c.runner.id))
        a.append((min(c.aed_costs()), c.runner.id))

    p = sorted(p, key=lambda e: e[0])
    a = sorted(a, key=lambda e: e[0])

    p_cost = p[0][0]
    a_cost = a[0][0] if a[0][1] != p[0][1] else a[1][0]
    
    return p_cost + a_cost


if __name__ == "__main__":
    with HeartrunnerDB.default() as db:
        db.delete_nodes(Runner)
        db.delete_nodes(Patient)
        db.generate_entity(Runner, RUNNERS)
        patients = db.generate_entity(Patient, SAMPLE)   

        cost_proximity = np.empty(SAMPLE)
        cost_greedy = np.empty(SAMPLE)

        i = 0
        for patient in patients:
            # Get candidates to assign to patient
            radius = 1
            while True:
                candidates = db.get_pathfinder(patient, kilometers=radius).compute_candidates()
                if candidates: break
                radius += 0.5
            
            cost_proximity[i] = proximity_choice(candidates)

            cost_greedy[i] = greedy_choice(candidates)

            print(f"Iteration {i+1}: Proximity = {cost_proximity[i]:.1f} Greedy = {cost_greedy[i]:.1f}")
            i += 1
        
        print(f"Mean costs: Proximity = {cost_proximity.mean():.2f}, Greedy = {cost_greedy.mean():.2f}")
            
            

            
            
