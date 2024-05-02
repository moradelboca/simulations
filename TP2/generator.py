import numpy as np
import random as rd



def uniform(a, b, n):
    for i in range(n):
        rnd = rd.uniform(0, 1)
        num = a + rnd * (b - a)
        yield round(num, 4)


def exponential(lambd, n):
    for i in range(n):
        rnd = rd.uniform(0, 1)
        num = (-1 / lambd) * np.log(1 - rnd)
        yield round(num, 4)


def normal(mean, std, n):
    for i in range(n):
        rnd1 = rd.uniform(0, 1)
        rnd2 = rd.uniform(0, 1)
        num1 = (np.sqrt(-2 * np.log(rnd1)) * np.cos(2 * np.pi * rnd2)) * std + mean
        num2 = (np.sqrt(-2 * np.log(rnd1)) * np.sin(2 * np.pi * rnd2)) * std + mean
        yield round(num1, 4)
        yield round(num2, 4)