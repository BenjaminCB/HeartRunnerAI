import pygad.gann
import pygad.nn
import numpy
import json
import heartrunner.core.types as hct
from random import uniform

ALL_TASKS: list[hct.Task] = []
CURRENT_TASKS: list[hct.Task] = []
STATE = numpy.zeros(2500)
PREV_TIME = 0
SAMPLE_CHANCE = 0.03


def sample_tasks(pick_chance: float):
    sampled = []

    for task in ALL_TASKS:
        if uniform(0,1) < pick_chance:
            sampled.append(task)

    return sampled


def predict_with_cost(runners: list[int], cost: list[int], sol_idx: int):
    global GANN_instance, STATE

    # make prediction for patient runner and update state
    truncated_state = numpy.take(STATE, runners)
    concated = numpy.concatenate((truncated_state, numpy.array(cost)), axis=None)
    input = numpy.array([concated / numpy.amax(concated)])
    predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                   data_inputs=input)
    p_idx = predictions[0]
    STATE[runners[p_idx]] += cost[p_idx]


def process(task: hct.Task, sol_idx: int):
    global PREV_TIME, STATE

    STATE -= (task.time - PREV_TIME)
    STATE = STATE.clip(min=0)
    PREV_TIME = task.time

    predict_with_cost(task.runners, task.p_costs, sol_idx)
    predict_with_cost(task.runners, task.a_costs, sol_idx)

    return numpy.amax(STATE)


def fitness_func(solution, sol_idx):
    latency_sum = sum([process(task, sol_idx) for task in CURRENT_TASKS])
    return 10000000 / latency_sum


def callback_generation(ga_instance):
    global GANN_instance, CURRENT_TASKS, STATE, PREV_TIME

    population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks,
                                                            population_vectors=ga_instance.population)
    GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)

    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))

    CURRENT_TASKS = sample_tasks(SAMPLE_CHANCE)
    STATE = numpy.zeros(2500)
    PREV_TIME = 0


def converter(json_line):
    task = hct.Task.from_json(json_line)
    task.runners = list(map(lambda r: r % 100, task.runners))
    return task


if __name__ == "__main__":
    with open("../../data/training/T3600-R2000-C10-A1.json", "r") as task_file:
        ALL_TASKS = list(map(hct.Task.from_json, json.load(task_file)))

    # roughly 100 tasks
    CURRENT_TASKS = sample_tasks(SAMPLE_CHANCE)

    num_solutions = 6
    GANN_instance = pygad.gann.GANN(num_solutions=num_solutions,
                                    num_neurons_input=20,
                                    num_neurons_hidden_layers=[40],
                                    num_neurons_output=10,
                                    hidden_activations="relu",
                                    output_activation="softmax")

    population_vectors = pygad.gann.population_as_vectors(GANN_instance.population_networks)

    ga_instance = pygad.GA(num_generations=500,
                           num_parents_mating=4,
                           initial_population=population_vectors.copy(),
                           fitness_func=fitness_func,
                           mutation_percent_genes=5,
                           init_range_low=-2,
                           init_range_high=2,
                           parent_selection_type="tournament",
                           K_tournament=3,
                           crossover_type="single_point",
                           mutation_type="random",
                           random_mutation_max_val=0.2,
                           random_mutation_min_val=-0.2,
                           keep_parents=0,
                           keep_elitism=0,
                           on_generation=callback_generation)

    ga_instance.run()

    ga_instance.plot_fitness(save_dir="../../plots/fitness.png")

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))
