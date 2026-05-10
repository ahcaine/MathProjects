"""Rebuild an old MATLAB project in Python.

This script recreates two parts of the portfolio write-up:

1. An overdamped Langevin simulation in an exponentially decaying potential
   with constant diffusivity, together with the long-time scaling solution
   for a non-normalizable Boltzmann distribution.
2. A position-dependent diffusivity model near a wall, simulated with an
   Euler-Maruyama discretization of the Itô SDE

       dX = [D'(X) - D(X) V'(X) / (k_B T)] dt + sqrt(2 D(X)) dW.

The script saves a small set of PNG figures into ``projects/non-normalizable-boltzmann/images/`` so the
results can be embedded in the static site.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


K_B = 1.380649e-23
TEMPERATURE = 298.15


@dataclass(frozen=True)
class PhysicalParams:
    temperature: float = TEMPERATURE
    viscosity: float = 1.0e-3
    particle_radius: float = 2.5e-6
    debye_length: float = 0.08e-6
    wall_potential_scale: float = 16.0

    @property
    def kbt(self) -> float:
        return K_B * self.temperature

    @property
    def gamma(self) -> float:
        return 6.0 * np.pi * self.viscosity * self.particle_radius

    @property
    def D0(self) -> float:
        return self.kbt / self.gamma

    @property
    def V0(self) -> float:
        return self.wall_potential_scale * self.kbt


def potential(x: np.ndarray, params: PhysicalParams) -> np.ndarray:
    return params.V0 * np.exp(-x / params.debye_length)


def potential_gradient(x: np.ndarray, params: PhysicalParams) -> np.ndarray:
    return -(params.V0 / params.debye_length) * np.exp(-x / params.debye_length)


def force(x: np.ndarray, params: PhysicalParams) -> np.ndarray:
    return -potential_gradient(x, params)


def reflect_lower(values: np.ndarray, lower: float) -> np.ndarray:
    reflected = values.copy()
    mask = reflected < lower
    reflected[mask] = lower + np.abs(reflected[mask] - lower)
    return reflected


def simulate_constant_diffusivity(
    *,
    params: PhysicalParams,
    n_particles: int,
    n_steps: int,
    dt: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    positions = np.zeros(n_particles, dtype=float)
    history = np.empty((n_steps + 1, n_particles), dtype=float)
    history[0] = positions
    sigma = np.sqrt(2.0 * params.D0 * dt)

    for step in range(1, n_steps + 1):
        drift = force(positions, params) / params.gamma
        positions = positions + drift * dt + sigma * rng.standard_normal(n_particles)
        positions = reflect_lower(positions, 0.0)
        history[step] = positions

    times = np.arange(n_steps + 1) * dt
    return times, history


def scaling_solution(x: np.ndarray, t: float, params: PhysicalParams) -> np.ndarray:
    if t <= 0.0:
        raise ValueError("t must be positive for the scaling solution")
    return (
        1.0
        / np.sqrt(np.pi * params.D0 * t)
        * np.exp(-potential(x, params) / params.kbt - x**2 / (4.0 * params.D0 * t))
    )


def binned_velocity(
    positions: np.ndarray,
    dt: float,
    bins: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_prev = positions[:-1].ravel()
    x_next = positions[1:].ravel()
    velocity = (x_next - x_prev) / dt

    counts, edges = np.histogram(x_prev, bins=bins)
    weighted, _ = np.histogram(x_prev, bins=bins, weights=velocity)
    centers = 0.5 * (edges[:-1] + edges[1:])

    means = np.full_like(centers, np.nan, dtype=float)
    valid = counts > 75
    means[valid] = weighted[valid] / counts[valid]
    return centers, means, counts


def diffusivity_brenner(z: np.ndarray, params: PhysicalParams) -> tuple[np.ndarray, np.ndarray]:
    r = params.particle_radius
    D = params.D0 * (1.0 - 9.0 * r / (8.0 * z))
    dD = params.D0 * (9.0 * r) / (8.0 * z**2)
    return D, dD


def diffusivity_rational(z: np.ndarray, params: PhysicalParams) -> tuple[np.ndarray, np.ndarray]:
    r = params.particle_radius
    numerator = 6.0 * z**2 + 2.0 * r * z
    denominator = 6.0 * z**2 + 9.0 * r * z + 2.0 * r**2
    numerator_prime = 12.0 * z + 2.0 * r
    denominator_prime = 12.0 * z + 9.0 * r

    D = params.D0 * numerator / denominator
    dD = params.D0 * (
        numerator_prime * denominator - numerator * denominator_prime
    ) / denominator**2
    return D, dD


def simulate_variable_diffusivity(
    *,
    params: PhysicalParams,
    n_particles: int,
    n_steps: int,
    dt: float,
    x0: float,
    diffusivity_model,
    lower_wall: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    positions = np.full(n_particles, x0, dtype=float)
    history = np.empty((n_steps + 1, n_particles), dtype=float)
    history[0] = positions

    for step in range(1, n_steps + 1):
        D, dD = diffusivity_model(positions, params)
        D = np.maximum(D, params.D0 * 1.0e-6)
        drift = dD - D * potential_gradient(positions, params) / params.kbt
        noise = np.sqrt(2.0 * D * dt) * rng.standard_normal(n_particles)
        positions = positions + drift * dt + noise
        positions = reflect_lower(positions, lower_wall)
        history[step] = positions

    times = np.arange(n_steps + 1) * dt
    return times, history


def summarize_variable_diffusivity(
    *,
    params: PhysicalParams,
    n_particles: int,
    n_steps: int,
    dt: float,
    x0: float,
    diffusivity_model,
    lower_wall: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    positions = np.full(n_particles, x0, dtype=float)
    times = np.arange(n_steps + 1) * dt
    variance = np.zeros(n_steps + 1, dtype=float)
    fourth = np.zeros(n_steps + 1, dtype=float)

    for step in range(1, n_steps + 1):
        D, dD = diffusivity_model(positions, params)
        D = np.maximum(D, params.D0 * 1.0e-6)
        drift = dD - D * potential_gradient(positions, params) / params.kbt
        noise = np.sqrt(2.0 * D * dt) * rng.standard_normal(n_particles)
        positions = positions + drift * dt + noise
        positions = reflect_lower(positions, lower_wall)

        displacement = positions - x0
        centered = displacement - displacement.mean()
        variance[step] = np.mean(centered**2)
        fourth[step] = np.mean(centered**4)

    return times, variance, fourth


def central_moments(displacements: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centered = displacements - displacements.mean(axis=1, keepdims=True)
    var = np.mean(centered**2, axis=1)
    fourth = np.mean(centered**4, axis=1)
    return var, fourth


def make_scaling_figure(
    *,
    params: PhysicalParams,
    times: np.ndarray,
    history: np.ndarray,
    output_dir: Path,
) -> None:
    final_time = times[-1]
    final_positions = history[-1]
    max_x = np.quantile(final_positions, 0.997)
    bins = np.linspace(0.0, max_x, 70)
    hist_density, edges = np.histogram(final_positions, bins=bins, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    profile = scaling_solution(centers, final_time, params)
    amplitude = np.dot(hist_density, profile) / np.dot(profile, profile)

    grid = np.linspace(0.0, max_x, 500)
    theory = amplitude * scaling_solution(grid, final_time, params)

    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    ax.hist(
        final_positions * 1.0e6,
        bins=edges * 1.0e6,
        range=(0.0, max_x * 1.0e6),
        density=True,
        alpha=0.65,
        color="#b55233",
        label="Simulated ensemble at final time",
    )
    ax.plot(
        grid * 1.0e6,
        theory / 1.0e6,
        color="#1d2733",
        lw=2.3,
        label="Best-fit scaling profile",
    )
    ax.set_xlabel("Distance from wall (micrometers)")
    ax.set_ylabel("Probability density (1 / micrometer)")
    ax.set_title("Non-normalizable Boltzmann scaling solution")
    ax.legend()
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(output_dir / "nnbd_scaling_solution.png", dpi=180)
    plt.close(fig)


def make_velocity_figure(
    *,
    params: PhysicalParams,
    history: np.ndarray,
    dt: float,
    output_dir: Path,
) -> None:
    bins = np.linspace(0.0, 0.7e-6, 60)
    centers, measured, counts = binned_velocity(history, dt, bins)
    theory = force(centers, params) / params.gamma
    valid = counts > 250

    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    ax.plot(
        centers[valid] * 1.0e6,
        theory[valid] * 1.0e6,
        color="#1d2733",
        lw=2.3,
        label="F(x) / gamma",
    )
    ax.plot(
        centers[valid] * 1.0e6,
        measured[valid] * 1.0e6,
        color="#b55233",
        lw=1.9,
        label="Mean simulated velocity",
    )
    ax.set_xlabel("Distance from wall (micrometers)")
    ax.set_ylabel("Velocity (micrometers / second)")
    ax.set_title("Ensemble drift matches the overdamped Langevin drift")
    ax.set_ylim(bottom=0.0)
    ax.legend()
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(output_dir / "nnbd_velocity_validation.png", dpi=180)
    plt.close(fig)


def make_trajectory_figure(
    *,
    params: PhysicalParams,
    output_dir: Path,
    seed: int,
) -> None:
    times, history = simulate_constant_diffusivity(
        params=params,
        n_particles=6,
        n_steps=1800,
        dt=5.0e-5,
        seed=seed + 100,
    )

    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    colors = ["#1d2733", "#b55233", "#2b6f89", "#8d6a9f", "#5b8a5a", "#cc7a00"]
    for idx in range(history.shape[1]):
        ax.plot(
            times,
            history[:, idx] * 1.0e6,
            lw=1.8,
            alpha=0.95,
            color=colors[idx % len(colors)],
            label=f"Particle {idx + 1}",
        )

    ax.axhline(0.0, color="k", ls="--", lw=1.2, alpha=0.7, label="Wall")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Distance from wall (micrometers)")
    ax.set_title("Sample particle trajectories near the charged wall")
    ax.grid(alpha=0.18)
    ax.legend(ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir / "nnbd_particle_trajectories.png", dpi=180)
    plt.close(fig)


def make_variable_diffusivity_figures(
    *,
    params: PhysicalParams,
    output_dir: Path,
    seed: int,
) -> None:
    start_positions = [2.0 * params.particle_radius, 10.0 * params.particle_radius]
    lower_wall = 1.15 * params.particle_radius
    model_specs = [
        ("Brenner approximation", diffusivity_brenner, "#b55233"),
        ("Rational near-wall model", diffusivity_rational, "#2b6f89"),
    ]

    msd_fig, msd_axes = plt.subplots(1, 2, figsize=(12.5, 5.2), sharey=True)
    kurt_fig, kurt_ax = plt.subplots(figsize=(8.5, 5.4))

    for axis, (title, model, color) in zip(msd_axes, model_specs):
        for idx, x0 in enumerate(start_positions):
            times, var, fourth = summarize_variable_diffusivity(
                params=params,
                n_particles=3500,
                n_steps=1500,
                dt=2.0e-3,
                x0=x0,
                diffusivity_model=model,
                lower_wall=lower_wall,
                seed=seed + idx + (0 if model is diffusivity_brenner else 10),
            )
            label = f"x0 = {x0 / params.particle_radius:.0f} r"

            axis.plot(times, var * 1.0e12, lw=2.0, label=label)
            if idx == 0:
                kurtosis = np.divide(
                    fourth,
                    var**2,
                    out=np.full_like(var, np.nan),
                    where=var > 0.0,
                )
                kurt_ax.plot(times, kurtosis - 3.0, lw=2.0, color=color, label=title)

        axis.plot(times, 2.0 * params.D0 * times * 1.0e12, "k--", lw=1.6, label="2 D0 t")
        axis.set_title(title)
        axis.set_xlabel("Time (seconds)")
        axis.grid(alpha=0.18)
        axis.legend()

    msd_axes[0].set_ylabel("Variance of displacement (micrometers squared)")
    msd_fig.suptitle("Position-dependent diffusivity still gives near-linear MSD growth", y=1.02)
    msd_fig.tight_layout()
    msd_fig.savefig(output_dir / "diffusing_diffusivity_msd.png", dpi=180, bbox_inches="tight")
    plt.close(msd_fig)

    kurt_ax.axhline(0.0, color="k", ls="--", lw=1.4, label="Gaussian baseline")
    kurt_ax.set_xlabel("Time (seconds)")
    kurt_ax.set_ylabel("Excess kurtosis")
    kurt_ax.set_title("Displacement kurtosis remains non-Gaussian near the wall")
    kurt_ax.grid(alpha=0.18)
    kurt_ax.legend()
    kurt_fig.tight_layout()
    kurt_fig.savefig(output_dir / "diffusing_diffusivity_kurtosis.png", dpi=180)
    plt.close(kurt_fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "images",
        help="Directory where PNG figures will be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=522,
        help="Seed for NumPy's random number generator.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = PhysicalParams()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    times, history = simulate_constant_diffusivity(
        params=params,
        n_particles=5000,
        n_steps=900,
        dt=1.0e-4,
        seed=args.seed,
    )
    make_scaling_figure(params=params, times=times, history=history, output_dir=args.output_dir)
    make_velocity_figure(params=params, history=history, dt=times[1] - times[0], output_dir=args.output_dir)
    make_trajectory_figure(params=params, output_dir=args.output_dir, seed=args.seed)
    make_variable_diffusivity_figures(params=params, output_dir=args.output_dir, seed=args.seed)

    print(f"Saved figures to {args.output_dir}")
    print(f"D0 = {params.D0 * 1.0e12:.4f} micrometers^2/s")
    print(f"gamma = {params.gamma:.4e} N s / m")


if __name__ == "__main__":
    main()
