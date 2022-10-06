import os
from dotenv import load_dotenv
from random import sample
from heartrunner.database import HeartRunnerDB
from heartrunner.types import *

if __name__ == "__main__":
    load_dotenv('.env')
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    with HeartRunnerDB(uri, user, password) as db:
        pass
