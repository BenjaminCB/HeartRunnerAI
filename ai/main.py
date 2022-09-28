from dotenv import load_dotenv
import os
import heart_runner_db

if __name__ == "__main__":
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    load_dotenv('../.env')
    # uri = "neo4j+s://10ef08ec.databases.neo4j.io"
    # user = "neo4j"
    # password = "lymMxxE2BKuotSVbZPzpBTzg_IMDqrWkHcNcoAU8R3M"
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    db = heart_runner_db.HeartRunnerDB(uri, user, password)
    runners = db.gen_runners(5)
    print(runners)
    patients = db.gen_patients(5)
    print(patients)
    db.close()
