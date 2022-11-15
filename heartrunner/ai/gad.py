import pygad.gann
import pygad.nn
import numpy
import json
import heartrunner.core.types as hct
from random import uniform, sample
from time import time
from ortools.linear_solver import pywraplp

RUNNER_COUNT = 1000
GREEDY_COUNT = 1000
TASK_COUNT = 100
ALL_TASKS: list[hct.Task] = []
CURRENT_TASKS: list[hct.Task] = []
STATE = numpy.zeros(RUNNER_COUNT)
PREV_TIME = 0
SAMPLE_CHANCE = 0.03


# return a sorted sample from the list of tasks
def sample_n_tasks(n: int):
    sampled = sample(ALL_TASKS, n)
    return sorted(sampled, key=lambda t: t.time)


# return a sorted sample from the list of tasks
def sample_tasks(pick_chance: float):
    sampled = []

    for task in ALL_TASKS:
        if uniform(0, 1) < pick_chance:
            sampled.append(task)

    return sampled


# adjust state latencies as time passes
def update_state_time(t: hct.Task):
    global PREV_TIME, STATE

    STATE -= (t.time - PREV_TIME)
    STATE = STATE.clip(min=0)
    PREV_TIME = t.time


# fill the STATE by performing n amount of tasks using the greedy algorithm
def greedy(task_count: int):
    global STATE, PREV_TIME

    tasks = sample_n_tasks(task_count)
    for task in tasks:
        update_state_time(task)
        min_cost = task.p_costs[0] + STATE[task.runners[0]] + task.a_costs[1] + STATE[task.runners[1]]
        p_idx = 0
        a_idx = 1
        i = 0
        j = 0
        while i < len(task.runners):
            while j < len(task.runners):
                if i == j:
                    j += 1
                    continue

                cost = task.p_costs[i] + STATE[task.runners[i]] + task.a_costs[j] + STATE[task.runners[j]]
                if cost < min_cost:
                    min_cost = cost
                    p_idx = i
                    a_idx = j

                j += 1

            i += 1

        STATE[task.runners[p_idx]] += task.p_costs[p_idx]
        STATE[task.runners[a_idx]] += task.a_costs[a_idx]
    PREV_TIME = 0



# make a prediction for a single choice such a which runner for the patient
def predict_with_cost(runners: list[int], cost: list[int], sol_idx: int):
    global GANN_instance, STATE

    # make prediction for patient runner and update state
    truncated_state = numpy.take(STATE, runners)
    concat = numpy.concatenate((truncated_state, numpy.array(cost)), axis=None)
    nn_input = numpy.array([concat / numpy.amax(concat)])
    # input = numpy.array([concatenated])
    predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                   data_inputs=nn_input)
    c_idx = predictions[0]
    STATE[runners[c_idx]] += cost[c_idx]

    return c_idx


# make the nn perform a task return the cost of the choice
def nn_choice(task: hct.Task, sol_idx: int):
    global PREV_TIME, STATE

    p_idx = predict_with_cost(task.runners, task.p_costs, sol_idx)
    a_idx = predict_with_cost(task.runners, task.a_costs, sol_idx)
    prediction_cost = STATE[task.runners[p_idx]] + STATE[task.runners[a_idx]]

    return prediction_cost


# calculate the cost of the greedy choice
def greedy_cost(task: hct.Task):
    min_cost = task.p_costs[0] + STATE[task.runners[0]] + task.a_costs[0] + STATE[task.runners[0]]
    for i in range(len(task.runners)):
        for j in range(len(task.runners)):
            cost = task.p_costs[i] + STATE[task.runners[i]] + task.a_costs[j] + STATE[task.runners[j]]
            if cost < min_cost:
                min_cost = cost

    return min_cost


# percent difference from the greed choice
def fitness_func(_, sol_idx):
    c_greedy = 0
    c_prediction = 0
    for task in CURRENT_TASKS:
        update_state_time(task)
        c_greedy += greedy_cost(task)
        c_prediction += nn_choice(task, sol_idx)

    return (c_greedy / (c_prediction + 1)) * 100


# At the end of each generation weights and tasks need to be updated
def callback_generation(ga):
    global GANN_instance, CURRENT_TASKS, STATE, PREV_TIME

    # update the weighs
    population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks,
                                                            population_vectors=ga.population)
    GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)

    print("Generation = {generation}".format(generation=ga.generations_completed))
    print("Fitness    = {fitness}".format(fitness=ga.best_solution()[1]))

    # update globals for the next generation
    STATE = numpy.zeros(RUNNER_COUNT)
    greedy(GREEDY_COUNT)
    print("state maximum: {n}".format(n=numpy.amax(STATE)))
    CURRENT_TASKS = sample_n_tasks(TASK_COUNT)
    PREV_TIME = 0


# how to we convert a task in json format to a Task object
def converter(json_line):
    global RUNNER_COUNT
    task = hct.Task.from_json(json_line)
    task.runners = list(map(lambda r: r % RUNNER_COUNT, task.runners))
    return task


if __name__ == "__main__":
    with open("../../data/training/T3600-R2000-C10-A1.json", "r") as task_file:
        ALL_TASKS = list(map(converter, json.load(task_file)))

    greedy(GREEDY_COUNT)
    CURRENT_TASKS = sample_n_tasks(TASK_COUNT)

    GANN_instance = pygad.gann.GANN(num_solutions=10,
                                    num_neurons_input=20,
                                    num_neurons_hidden_layers=[40, 20],
                                    num_neurons_output=10,
                                    hidden_activations="relu",
                                    output_activation="softmax")

    population_vectors = pygad.gann.population_as_vectors(GANN_instance.population_networks)

    ga_instance = pygad.GA(num_generations=100,
                           num_parents_mating=4,
                           initial_population=population_vectors.copy(),
                           fitness_func=fitness_func,
                           mutation_percent_genes=10,
                           init_range_low=-1,
                           init_range_high=1,
                           parent_selection_type="tournament",
                           K_tournament=3,
                           crossover_type="single_point",
                           mutation_type="random",
                           random_mutation_max_val=0.05,
                           random_mutation_min_val=-0.05,
                           keep_parents=0,
                           keep_elitism=0,
                           on_generation=callback_generation)

    ga_instance.run()

    ga_instance.plot_fitness(title=
                             (
                                 "Task count: {task_count}, "
                                 "greedy count: {greedy_count}, "
                                 "runner count: {runner_count}"
                             ).format(task_count=TASK_COUNT, greedy_count=GREEDY_COUNT, runner_count=RUNNER_COUNT),
                             ylabel="Fitness [percentage of greedy cost]",
                             save_dir=f"../../plots/{int(time())}.png")

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))