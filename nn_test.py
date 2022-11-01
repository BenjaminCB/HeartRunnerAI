from heartrunner.database import HeartrunnerDB
from heartrunner.evolution import Evolution, generate_tasks
from heartrunner.types import NodeType

if __name__=="__main__":
    n_runner = 500
    with HeartrunnerDB.default() as db:
        db.delete_nodes(NodeType.Runner)
        db.generate_runners(n_runner)
    evo = Evolution(n_pop=26, n_iter=10, layers=[10, 10, 5], m_rate=0.2, m_amount=0.03, c_rate=0.2, n_runner=n_runner)
    worst_nns, best_nns = evo.evolve()
    tasks = generate_tasks()
    print('WORST NNS')
    print([Evolution.objective(nn, n_runner, tasks) for nn in worst_nns])

    print('BEST NNS')
    print([Evolution.objective(nn, n_runner, tasks) for nn in best_nns])