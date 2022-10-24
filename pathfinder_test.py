from heartrunner.types import NodeType
from heartrunner.database import HeartrunnerDB

if __name__ == "__main__":
    with HeartrunnerDB.default() as db:
        runners = db.count_nodes(NodeType.Runner)
        print(runners)
