import numpy as np
import types as types


class Environment:

    def __init__(self, nn, n_runner):
        self.tasks = []
        self.nn = nn
        self.n_runner = n_runner
        self.state = np.zeros(self.n_runner)
        self.score = 0

    def enqueue_tasks(self, rss: list[(list[(types.Runner, int, int)], int)]):
        for rs in rss:
            self.tasks.insert(0, rs)

    def _new_latency(self, ts: list[(int, int)]):
        # TODO infinity may not be the best value to give as it gives
        # as it gives some problems when scaling with np.interp
        additional_latency = np.full(self.n_runner, np.Infinity)
        for (runner_id, runner_time) in ts:
            additional_latency[runner_id] = runner_time

        return np.add(self.state, additional_latency)

    def process_tasks(self):
        for task in self.tasks:
            runner_times = task[0]
            timestep = task[1]
            self.state -= timestep

            # calculate patient_times, figure out which value to give unreachable runners
            # calculate aed_times
            # concat all into big vector
            # scale values from 0 to 1 look at np.interp
            # get prediction from nn
            # update state
            # update score from new state

        self.tasks = []
