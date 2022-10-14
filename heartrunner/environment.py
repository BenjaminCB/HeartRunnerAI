import numpy as np
import types as t


class Environment:

    def __init__(self, db):
        self.queue = []
        self.db = db
        self.runner_count = self.db.count_nodes(t.NodeType.Runner)
        self.state = np.zeros(self.runner_count)

    def enqueue(self, rs: list[(t.Runner, int, int)]):
        self.queue.insert(0, rs)

    def _new_latency(self, ts: list[(int, int)]):
        additional_latency = np.full(self.runner_count, np.Infinity)
        for (runner_id, runner_time) in ts:
            additional_latency[runner_id] = runner_time

        return np.add(self.state, additional_latency)

    def process_task(self):
        task = self.queue.pop()
        patient_times = np.add(self.state, map(lambda time: (time[0].id, time[1]), task))
        aed_times = np.add(self.state, map(lambda time: (time[0].id, time[2]), task))

        nn_input = np.concatenate((self.state, patient_times, aed_times), axis=None)
