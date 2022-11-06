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


def sample_tasks(pick_chance: float):
    sampled = []

    for task in ALL_TASKS:
        if uniform(0,1) < pick_chance:
            sampled.append(task)

    return sampled


def process(task: hct.Task, sol_idx: int):
    global GANN_instance, PREV_TIME, STATE

    truncated_state = numpy.take(STATE, task.runners)

    STATE -= (task.time - PREV_TIME)
    STATE = STATE.clip(min=0)

    # make prediction for patient runner and update state
    input = numpy.array([numpy.concatenate((truncated_state, numpy.array(task.p_costs)), axis=None)])
    predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                   data_inputs=input)
    p_idx = predictions[0]
    STATE[task.runners[p_idx]] += task.p_costs[p_idx]

    # make prediction for aed runner and update state
    input = numpy.array([numpy.concatenate((truncated_state, numpy.array(task.a_costs)), axis=None)])
    predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                   data_inputs=input)
    r_idx = predictions[0]
    STATE[task.runners[r_idx]] += task.p_costs[r_idx]

    return numpy.amax(STATE)


def fitness_func(solution, sol_idx):
    latency_sum = sum([process(task, sol_idx) for task in CURRENT_TASKS])
    return (1 / latency_sum) * 100000


def callback_generation(ga_instance):
    global GANN_instance, CURRENT_TASKS, STATE, PREV_TIME

    population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks,
                                                            population_vectors=ga_instance.population)
    GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)

    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))

    CURRENT_TASKS = sample_tasks(0.03)
    STATE = numpy.zeros(2500)
    PREV_TIME = 0


if __name__ == "__main__":
    with open("../../data/training/T3600-R2000-C10-A1.json", "r") as task_file:
        ALL_TASKS = list(map(hct.Task.from_json, json.load(task_file)))

    # roughly 100 tasks
    CURRENT_TASKS = sample_tasks(0.03)

    num_solutions = 6
    GANN_instance = pygad.gann.GANN(num_solutions=num_solutions,
                                    num_neurons_input=20,
                                    num_neurons_hidden_layers=[40],
                                    num_neurons_output=10,
                                    hidden_activations=["relu"],
                                    output_activation="softmax")

    population_vectors = pygad.gann.population_as_vectors(GANN_instance.population_networks)

    ga_instance = pygad.GA(num_generations=100,
                           num_parents_mating=4,
                           initial_population=population_vectors.copy(),
                           fitness_func=fitness_func,
                           mutation_percent_genes=5,
                           init_range_low=-2,
                           init_range_high=5,
                           parent_selection_type="sss",
                           crossover_type="single_point",
                           mutation_type="random",
                           keep_parents=1,
                           on_generation=callback_generation)

    ga_instance.run()

    ga_instance.plot_fitness()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))
