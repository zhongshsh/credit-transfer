import numpy as np

K = 10
c = 3
iteration = 5
n = 3
p = 0.2
alpha = 0.8


def g(s, action):
    if action == 1:
        return K
    if action == 0:
        return c * s


mu = np.ones(n + 1)
M = np.zeros((n + 1, n + 1))

for it in range(iteration):
    M = np.zeros((n + 1, n + 1))
    M[n][n], M[n][0], M[n][1] = 1, -alpha * (1 - p), -alpha * p
    for i in range(n):
        if mu[i] == 0:
            M[i][i] = 1 - alpha * (1 - p)
            M[i][i + 1] = -alpha * p
        else:
            if i == 0:
                M[0][0] = 1 - alpha * (1 - p)
                M[i][1] = -alpha * p
            else:
                M[i][i], M[i][0], M[i][1] = 1, -alpha * (1 - p), -alpha * p

    G = np.array([g(i, mu[i]) for i in range(n)] + [K])
    J = np.dot(np.linalg.inv(M), G)

    for i in range(n):
        cost1 = K + alpha * (1 - p) * J[0] + alpha * p * J[1]
        cost0 = c * i + alpha * (1 - p) * J[i] + alpha * p * J[i + 1]
        if cost1 > cost0:
            mu[i] = 0
        else:
            mu[i] = 1
