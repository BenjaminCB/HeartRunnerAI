from cmath import pi
import numpy as np

arr = np.linspace(5, 25, 10)

def calc_reward(array):
    reward = array.sum()
    # print("sum of function is: " + str(arrSum))
    return reward

def mean_reward(array):
    meanArray = np.linspace(5, 5, array.size)
    # print("Size of array: " + str(meanArray.size))
    # print(meanArray)
    return meanArray

def gain(array):
    reward = array.sum()
    print(reward)
    meanArray = np.linspace(5, 5, array.size)
    meanReward = meanArray.sum()
    print(meanReward)
    gain = reward - meanReward
    print(gain)
    return gain



calc_reward(arr)
mean_reward(arr)
gain(arr)