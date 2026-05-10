import numpy as np
import matplotlib.pyplot as plt


def lorenz(state, sigma=10.0, beta=8.0 / 3.0, rho=28.0):
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return np.array([dx, dy, dz])


def integrate(initial_state, step_size=0.01, steps=10_000):
    trajectory = np.zeros((steps, 3), dtype=float)
    trajectory[0] = initial_state

    for index in range(1, steps):
        previous = trajectory[index - 1]
        trajectory[index] = previous + step_size * lorenz(previous)

    return trajectory


trajectory = integrate(np.array([0.0, 1.0, 1.05]))

figure = plt.figure(figsize=(7, 5))
axes = figure.add_subplot(projection="3d")
axes.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], lw=0.6)
axes.set_title("Lorenz Attractor")
axes.set_xlabel("x")
axes.set_ylabel("y")
axes.set_zlabel("z")

plt.tight_layout()
plt.show()
