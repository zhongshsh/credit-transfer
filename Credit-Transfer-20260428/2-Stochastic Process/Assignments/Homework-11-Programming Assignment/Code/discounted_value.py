import numpy as np

K = 10
c = 3
iteration = 10
n = 10
p = 0.2
alpha = 0.8

J = np.random.rand(n + 1)
for it in range(iteration):
    for i in range(n):
        J[i] = min(
            K + alpha * (1 - p) * J[0] + alpha * p * J[1],
            c * i + alpha * (1 - p) * J[i] + alpha * p * J[i + 1],
        )
    J[-1] = K + alpha * (1 - p) * J[0] + alpha * p * J[1]
