from timeit import default_timer
from heartrunner.settings import *
from heartrunner.core.types import Runner, Patient
from heartrunner.core.database import HeartrunnerDB
import numpy as np

if __name__ == "__main__":
    with HeartrunnerDB.default() as db:
        db.delete_nodes(Runner)
        db.generate_entity(Runner, RUNNERS)
        db.delete_nodes(Patient)
        acc = 0
        acc_size = 0
        i = 0
        count = 0
        for patient in db.generate_entity(Patient, 100):
            time1 = default_timer()
            pf = db.get_pathfinder(patient)
            paths = pf.compute_paths()
            a = np.array([path.costs for path in paths])
            print(a.transpose())
            if len(paths) < CANDIDATE_RUNNERS:
                count += 1
            time2 = default_timer()
            elapsed = time2-time1
            size = len(pf.get_edges())+len(pf.get_nodes())
            acc += elapsed
            acc_size += size
            i += 1
            print(f"{i:4} Elapsed: {elapsed:.6f} - Avg.: {acc/i:.6f} - Size: {size:6.0f} - Avg.: {acc_size/i:6.0f} - Missed: {count}/{i}")
