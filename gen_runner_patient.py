import os
from dotenv import load_dotenv
from heartrunner.database import HeartRunnerDB

if __name__ == "__main__":
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    load_dotenv('.env')
    # uri = "neo4j+s://10ef08ec.databases.neo4j.io"
    # user = "neo4j"
    # password = "lymMxxE2BKuotSVbZPzpBTzg_IMDqrWkHcNcoAU8R3M"
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    db = HeartRunnerDB(uri, user, password)
    runners = db.gen_runners(2000)
    print(runners)
    # patients = db.gen_patients(5)
    # print(patients)
    # connecting = db.connecting_intersections(2000)
    # print(connecting)
    db.close()
