import imp
import threading
from msilib.schema import Class
from pickle import TRUE
from typing import Dict, List, Tuple
from .types import *
from random import random, randrange
from .database import *

class GeneratePatient:
    timestep: int
    probality: float
    acommulatedTime: int
    ourDatabase : HeartRunnerDB

    def __init__(self, timestep, probability):
        self.acommulatedTime = 0
        self.timestep = timestep
        self.probality = probability

    def GeneratePatientBasedOnTime(self):
        self.acommulatedTime += self.timestep
        
        if (random.uniform(0,1) < self.probality):
            shit = self.ourDatabase.gen_patients()

        t = Timer(self.timestep, self.GeneratePatientBasedOnTime)
        t.start()



        


        
        


