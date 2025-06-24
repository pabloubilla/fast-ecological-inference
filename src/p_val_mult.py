import numpy as np
import scipy.stats as stats



def p_val_threshold_n(n, mu, alpha):
    """
    Compute the smallest z such that P(X <= z - 1) >= 1 - alpha
    """

    # n : number of trials
    # mu : interested in p-values less than or equal to mu
    # alpha : significance level
    # Returns the smallest z such that P(X <= z - 1) >= 1 - alpha
    cum_prob = 0
    for z in range(n + 1):
        cum_prob += stats.binom.pmf(z - 1, n, mu)
        if cum_prob >= 1 - alpha:
            return z
    return n  # In case the loop finishes without reaching threshold


"""
Obtener el threshold para la cantidad óptima de iteraciones
"""


def compute_thresholds(S_min, S_max, mu_power, alpha_power):
    thresholds = {}
    mu = 10 ** (-mu_power)
    alpha = 10 ** (-alpha_power)
    for s in range(S_min, S_max + 1):
        n = int(10**s)
        thresholds[s] = p_val_threshold_n(n, mu, alpha)
    return thresholds


"""
Cálculo principal
"""


def compute_p_value_m_mult_threshold(
    x, r, S_min, S_max, thresholds, lgac_n=None, log_p=None, seed=None
):
    if seed is not None:
        np.random.seed(seed)
    J = sum(x)
    # log_p = np.log(r)
    # lgac_n = np.array([sum([np.log(max(k, 1)) for k in range(j + 1)]) for j in range(J + 1)])
    beta_n = np.sum(x * log_p) - np.sum(lgac_n[x])
    for s in range(S_min, S_max + 1):
        n = int(10**s)
        threshold = thresholds[s]
        x_samples = np.random.multinomial(J, r, size=n)
        beta_S = np.sum(x_samples * log_p, axis=1) - np.sum(lgac_n[x_samples], axis=1)
        less_p = np.sum(beta_S <= beta_n)
        if less_p >= threshold:
            break
    return less_p / n, s
