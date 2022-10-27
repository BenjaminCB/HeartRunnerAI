from timeit import default_timer
from heartrunner.types import AED, Intersection, Runner, Patient
from heartrunner.database import HeartrunnerDB

if __name__ == "__main__":
    with HeartrunnerDB.default() as db:
        db.delete_nodes(Runner)
        db.generate_entity(Runner, 1000)
        db.delete_nodes(Patient)
        acc = 0
        acc_size = 0
        i = 0
        for patient in db.generate_entity(Patient, 1000):
            time1 = default_timer()
            pf = db.get_pathfinder(patient)
            pf.compute_paths(n_runners=20, n_aeds=3)
            time2 = default_timer()
            elapsed = time2-time1
            size = len(pf.get_edges())+len(pf.get_nodes())
            acc += elapsed
            acc_size += size
            i += 1
            print(f"{i:4} Elapsed: {elapsed:.6f} - Avg.: {acc/i:.6f} - Size: {size:6.0f} - Avg.: {acc_size/i:6.0f}")
