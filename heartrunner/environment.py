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

            # save relative position so we can retrieve the id later
            runner_ids = []
            truncated_state = np.empty(len(runner_ids))
            state_through_patient = np.empty(len(runner_ids))
            state_through_aed = np.empty(len(runner_ids))
            i = 0
            for runner, ptime, atime in runner_times:
                runner_ids.append(runner.id)
                truncated_state[i] = self.state[runner_ids[i]]
                state_through_patient[i] = truncated_state[i] + ptime
                state_through_aed[i] = truncated_state[i] + atime
                i += 1

            # concat and normalize data
            nn_input = np.concatenate((truncated_state, state_through_patient, state_through_aed), axis=None)
            nn_input = (nn_input - np.min(nn_input)) / (np.max(nn_input) - np.min(nn_input))

            prediction = self.nn.predict(nn_input)

            # update state
            self.state[runner_ids[prediction[0]]] += runner_times[prediction[0]][1]
            self.state[runner_ids[prediction[1]]] += runner_times[prediction[1]][2]

            # update score from new state
            self.score += self.state.max

        self.tasks = []
