import numpy as np

K = 10
c = 3
iteration = 10
n = 3
p = 0.2
alpha = 1


h0 = np.zeros(n + 1)
lambdax = 0
for it in range(iteration):
    h = h0.copy()
    for i in range(n):
        h0[i] = (
            min(
                K + alpha * (1 - p) * h[0] + alpha * p * h[1],
                c * i + alpha * (1 - p) * h[i] + alpha * p * h[i + 1],
            )
            - lambdax
        )
    h0[-1] = K + alpha * (1 - p) * h[0] + alpha * p * h[1] - lambdax

    tmp = [c * i + alpha * (1 - p) * h0[i] + alpha * p * h0[i + 1] for i in range(n)]
    tmp.append(K + alpha * (1 - p) * h0[0] + alpha * p * h0[1])
    lambdax = min(tmp)
