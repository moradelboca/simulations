import matplotlib.pyplot as plt
import numpy as np


def plot_distribution(nums, intervals=10):
    intervals = np.linspace(min(nums), max(nums), intervals)
    plt.hist(nums, bins=intervals, edgecolor='black')
    plt.title("Distribucion de numeros pseudoaleatorios")
    plt.xlabel("Numeros pseudoaleatorios")
    plt.ylabel("Frecuencia")
    plt.show()
