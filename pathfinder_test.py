import os
import timeit
from dotenv import load_dotenv
from heartrunner.database import HeartRunnerDB
from heartrunner.types import *

if __name__ == "__main__":
    load_dotenv('.env')
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    with HeartRunnerDB(uri, user, password) as db:
        db.delete_nodes(NodeType.Patient)
        db.delete_nodes(NodeType.Runner)
        db.generate_patients(100)
        db.generate_runners(1000)
        for i in range(1,10):
            location = db.get_location(NodeType.Patient, i)
            start = timeit.default_timer()
            graph = db.get_subgraph(location.coords())
            elapsed = timeit.default_timer() - start
            print(elapsed)
            print(len(graph.runners.values()))
            print(len(graph.aeds.values()))
