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
            # db.delete_nodes(NodeType.Runner)
            # db.generate_runners(1000)
            time1 = default_timer()
            db.delete_nodes(NodeType.Patient)
            patients = db.generate_patients(10)
            for patient in patients:
                tasks = db.get_pathfinder(patient).compute_paths(n_runners=20, n_aeds=3)
                
            time2 = default_timer()
            elapsed = time2-time1
            acc += elapsed
            print(f"{i+1:4} Elapsed: {elapsed:.6f} - Average: {acc/(i+1):.6f}")
