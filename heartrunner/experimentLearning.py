import itertools
from multiprocessing import reduction
from operator import truediv
from pickle import TRUE
from random import randrange
import this
from typing import List
from typing_extensions import Self
from .types import *

class RunnerToChoose:
  
    DistanceToPatients: List[int] 
    DistanceToAEDToPatient: List[int]
  
    def __init__(self):
        self.DistanceToPatients = []
        self.DistanceToPatients= []
  
    def addDistanceToPatient(self,distance):
        self.DistanceToPatients.append(distance)

    def addDistanceToAED(self,distance):
        self.DistanceToAEDToPatient.append(distance)



class PatientGenerator:
    def GeneratePatient():
        return TRUE


class NeuralNetwork:

    def ChooseRunners(listofrunners):
        return listofrunners[0]


class Dispatcher:
    Runners: List[RunnerToChoose]
    Decisionmaker: NeuralNetwork
    def __init__(self):
        self.Runners = []

    def PickRunners(self,amountOfPatients):
        return TRUE
        
