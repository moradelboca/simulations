import numpy as np
import pandas as pd


def fit(distribution, nums, intervals, params):
    n = len(nums)
    seen_freq, interval_from = np.histogram(nums, bins=intervals)
    interval_to = np.roll(interval_from, -1)[:-1]
    interval_from = interval_from[:-1]
    class_mark = [(interval_from[i] + interval_to[i]) / 2 for i in range(len(interval_from))]
    seen_prob = [freq / n for freq in seen_freq]

    if distribution == "uniform":
        expected_freq = [n / intervals] * intervals
        expected_prob = [freq / n for freq in expected_freq] 
    elif distribution == "exponential":
        lambd = params["lambd"]
        expected_prob = [(1-np.e**(-lambd*interval_to[i]))-(1-np.e**(-lambd*interval_from[i])) for i in range(intervals)]
        expected_freq = [prob * n for prob in expected_prob]
    else:
        mean = params["mean"]
        std = params["std"]
        expected_prob = [(np.e**(-0.5 * ((class_mark[i] - mean) / std)**2)) / (std * np.sqrt(2 * np.pi)) * (interval_to[i] - interval_from[i]) for i in range(len(class_mark))]
        expected_freq = [prob * n for prob in expected_prob]

    chisq = [(seen_freq[i] - expected_freq[i])**2 / expected_freq[i] for i in range(intervals)]
    chisq_value = sum(chisq)
    chisq_data = pd.DataFrame({
        "Desde": interval_from,
        "Hasta": interval_to,
        "Marca de Clase": class_mark,
        "Frecuencia Observada": seen_freq,
        "Frecuencia Esperada": expected_freq,
        "Chi": chisq
    })

    seen_prob_acum = np.cumsum(seen_prob)
    expected_prob_acum = np.cumsum(expected_prob)
    ks = [abs(seen_prob_acum[i] - expected_prob_acum[i]) for i in range(intervals)]
    ks_value = max(ks)
    ks_data = pd.DataFrame({
        "Desde": interval_from,
        "Hasta": interval_to,
        "Marca de Clase": class_mark,
        "Probabilidad Acumulada Observada": seen_prob_acum,
        "Probabilidad Acumulada Esperada": expected_prob_acum,
        "KS": ks
    })

    return chisq_data, chisq_value, ks_data, ks_value