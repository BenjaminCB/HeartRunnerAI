import os
from dotenv import load_dotenv
from timeit import default_timer
from heartrunner.types import NodeType
from heartrunner.database import HeartrunnerDB

if __name__ == "__main__":
    load_dotenv('.env')
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    with HeartrunnerDB(uri, user, password) as db:
        acc = 0
        for i in range(10):
            db.delete_nodes(NodeType.Runner)
            db.generate_runners(1000)
            db.delete_nodes(NodeType.Patient)
            db.generate_patients(1)
            patients = db.get_nodes(NodeType.Patient)
            for patient in patients:
                time1 = default_timer()
                pf = db.get_pathfinder(patient)
                time2 = default_timer()
                pf.calculate_tasks(n_runners=20, n_aeds=3)
                elapsed = time2-time1
                acc += elapsed
                print(f"{i+1:4} Elapsed: {elapsed:.6f} - Average: {acc/(i+1):.6f}")
                