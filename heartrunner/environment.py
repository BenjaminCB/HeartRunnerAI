import numpy as np
from .types import Task


class Environment:

    def __init__(self, nn, n_runner):
        self.tasks = []
        self.nn = nn
        self.n_runner = n_runner
        self.state = np.zeros(self.n_runner, dtype=np.int32)
        self.score = 0

    def enqueue_tasks(self, rss: list[Task]):
        self.tasks = rss

    def _new_latency(self, ts: list[(int, int)]):
        # TODO infinity may not be the best value to give as it gives
        # as it gives some problems when scaling with np.interp
        additional_latency = np.full(self.n_runner, np.Infinity)
        for (runner_id, runner_time) in ts:
            additional_latency[runner_id] = runner_time

        return np.add(self.state, additional_latency)

    def process_tasks(self):
        prev_time = None
        for task in self.tasks:
            if prev_time:
                self.state -= (task.time-prev_time)
                self.state = self.state.clip(min=0)
            prev_time = task.time
            
            truncated_state = np.empty(task.count, dtype=np.int32)
            np.take(a=self.state, indices=task.runner_ids, out=truncated_state)
            state_through_patient = truncated_state + task.patient_times
            state_through_aed = truncated_state + task.aed_times

            # save relative position so we can retrieve the id later
            # runner_ids = []
            # truncated_state = np.empty(len(runner_ids))
            # state_through_patient = np.empty(len(runner_ids))
            # state_through_aed = np.empty(len(runner_ids))
            # i = 0
            # for runner, ptime, atime in runner_times:
            #     runner_ids.append(runner.id)
            #     truncated_state[i] = self.state[runner_ids[i]]
            #     state_through_patient[i] = truncated_state[i] + ptime
            #     state_through_aed[i] = truncated_state[i] + atime
            #     i += 1

            # concat and normalize data
            patient_input = np.concatenate((truncated_state, state_through_patient), axis=None)
            patient_input = (patient_input - np.min(patient_input)) / (np.max(patient_input) - np.min(patient_input))
            patient_prediction = self.nn.predict(patient_input)
            self.state[task.runner_ids[patient_prediction[0][0]]] += task.patient_times[patient_prediction[0][0]]

            aed_input = np.concatenate((truncated_state, state_through_aed), axis=None)
            aed_input = (aed_input - np.min(aed_input)) / (np.max(aed_input) - np.min(aed_input))
            aed_prediction = self.nn.predict(aed_input)
            self.state[task.runner_ids[aed_prediction[0][0]]] += task.aed_times[aed_prediction[0][0]]

            # update score from new state
            self.score += self.state.max()

        self.tasks = []