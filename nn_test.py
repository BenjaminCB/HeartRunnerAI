from heartrunner.database import HeartrunnerDB
from heartrunner.evolution import Evolution
from heartrunner.types import NodeType

if __name__=="__main__":
    n_runner = 1000
    with HeartrunnerDB.default() as db:
        db.delete_nodes(NodeType.Runner)
        db.generate_runners(n_runner)
    evo = Evolution(n_pop=10, n_iter=5, input_size=60, m_rate=0.01, c_rate=0.01, n_runner=n_runner)
    evo.evolve()
    