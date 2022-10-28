from heartrunner.database import HeartrunnerDB
from heartrunner.evolution import Evolution
from heartrunner.types import NodeType

if __name__=="__main__":
    n_runner = 1000
    with HeartrunnerDB.default() as db:
        db.delete_nodes(NodeType.Runner)
        db.generate_runners(n_runner)
    evo = Evolution(n_pop=10, n_iter=10, layers=[60, 40, 20], m_rate=0.1, m_amount=0.05, c_rate=0.1, n_runner=n_runner)
    all_scores = evo.evolve()
    min_scores = list(map(min, all_scores))
    print('lowest score in each generation')
    print(min_scores)
    print('highest score in each generation')
    max_scores = list(map(max, all_scores))
    print(max_scores)
