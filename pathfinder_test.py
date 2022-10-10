import os
import timeit
from dotenv import load_dotenv
from heartrunner.types import *
from heartrunner.database import HeartrunnerDB
from heartrunner.pathfinder import Pathfinder

if __name__ == "__main__":
    load_dotenv('.env')
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    with HeartrunnerDB(uri, user, password) as db:
        db.delete_nodes(NodeType.Patient)
        db.delete_nodes(NodeType.Runner)
        db.generate_patients(10)
        db.generate_runners(1000)
        patients = db.get_nodes(NodeType.Patient)
        for patient in patients:
            graph = db.get_subgraph(patient)
            pf = Pathfinder(patient, graph)
