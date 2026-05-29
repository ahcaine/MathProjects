from __future__ import annotations

from manim import *
import numpy as np


class RandomWalkDot(Scene):
    """Animate a 2D random walk with fixed step length and random orientation.

    Edit the class constants below to change the walk:

    - DX: spatial step length
    - DT: run time for each update on screen
    - N_STEPS: number of random steps
    - SEED: random seed for reproducibility
    """

    DX = 0.16
    DT = 0.08
    N_STEPS = 60
    SEED = 522

    DOT_RADIUS = 0.08
    VECTOR_COLOR = YELLOW
    PATH_COLOR = BLUE_D
    DOT_COLOR = ORANGE

    def sample_walk(self) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(self.SEED)
        angles = rng.uniform(0.0, 2, size=self.N_STEPS)
        steps = self.DX * \
            np.column_stack((np.cos(angles*PI), np.sin(angles*PI)))

        positions = np.zeros((self.N_STEPS + 1, 2), dtype=float)
        positions[1:] = np.cumsum(steps, axis=0)
        return positions, angles

    @staticmethod
    def padded_range(values: np.ndarray, padding: float = 1.0) -> tuple[float, float]:
        lower = float(np.min(values))
        upper = float(np.max(values))
        if np.isclose(lower, upper):
            lower -= 0.25
            upper += 0.25
        return lower - padding, upper + padding

    def build_plane(self, positions: np.ndarray) -> NumberPlane:
        x_min, x_max = self.padded_range(positions[:, 0], padding=1.25)
        y_min, y_max = self.padded_range(positions[:, 1], padding=1.25)

        plane = NumberPlane(
            x_range=[np.floor(x_min), np.ceil(x_max), 1],
            y_range=[np.floor(y_min), np.ceil(y_max), 1],
            background_line_style={
                "stroke_color": GREY_B,
                "stroke_width": 1,
                "stroke_opacity": 0.45,
            },
            axis_config={
                "stroke_color": GREY_A,
                "stroke_width": 2,
                "include_ticks": False,
            },
            faded_line_ratio=2,
        )
        plane.set_width(min(config.frame_width - 1.0, 12.0))
        plane.shift(ORIGIN - plane.c2p(0, 0))
        return plane

    def construct(self) -> None:
        positions, angles = self.sample_walk()
        plane = self.build_plane(positions)

        title = Tex(r"2D Random Walk", font_size=40).to_edge(UP)
        rule = MathTex(
            r"p_k = p_{k-1} + x_k, \quad x_k = dx(\cos\theta_k,\sin\theta_k)",
            font_size=34,
        ).next_to(title, DOWN, buff=0.2)

        step_counter = DecimalNumber(0, num_decimal_places=0, font_size=30)
        time_counter = DecimalNumber(0, num_decimal_places=2, font_size=30)
        counter_label = VGroup(
            Tex("step", font_size=28),
            step_counter,
            Tex(r",\quad time $=$", font_size=28),
            time_counter,
        ).arrange(RIGHT, buff=0.18).to_corner(UR)

        parameter_label = MathTex(
            rf"dx={self.DX:.2f}, \quad \Delta t={self.DT:.2f}, \quad N={self.N_STEPS}",
            font_size=30,
        ).to_corner(UL)

        origin_point = plane.c2p(*positions[0])
        dot = Dot(origin_point, radius=self.DOT_RADIUS, color=self.DOT_COLOR)
        trail = TracedPath(
            dot.get_center, stroke_color=self.PATH_COLOR, stroke_width=5)

        start_label = MathTex(r"p_0=(0,0)", font_size=30).next_to(
            dot, DOWN + RIGHT, buff=0.18)

        # self.add(plane, title, rule, counter_label,
        #          parameter_label, trail, dot, start_label)
        self.add(plane, title, counter_label,
                 trail, dot, start_label)
        self.wait(0.4)

        current_vector = None

        for k in range(self.N_STEPS):
            start = plane.c2p(*positions[k])
            end = plane.c2p(*positions[k + 1])

            new_vector = Arrow(
                start=start,
                end=end,
                buff=0,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.22,
                color=self.VECTOR_COLOR,
            )

            theta_label = MathTex(
                rf"\theta_{{{k + 1}}}={angles[k]:.2f}\pi",
                font_size=28,
            ).next_to(parameter_label, DOWN, aligned_edge=LEFT, buff=0.18)

            animations = [
                step_counter.animate.set_value(k + 1),
                time_counter.animate.set_value((k + 1) * self.DT),
                FadeIn(theta_label, shift=0.08 * DOWN),
            ]

            if current_vector is None:
                animations.append(Create(new_vector))
            else:
                animations.append(ReplacementTransform(
                    current_vector, new_vector))

            self.play(*animations, run_time=self.DT, rate_func=linear)
            self.play(dot.animate.move_to(end),
                      run_time=self.DT, rate_func=linear)

            current_vector = new_vector

            if k == 0:
                self.play(FadeOut(start_label), run_time=0.2)

            self.play(FadeOut(theta_label), run_time=0.12)

        final_label = MathTex(
            rf"p_{{{self.N_STEPS}}}=({positions[-1, 0]:.2f},{positions[-1, 1]:.2f})",
            font_size=30,
        ).next_to(dot, UP + RIGHT, buff=0.2)

        self.play(FadeIn(final_label), run_time=0.4)
        self.wait(1.2)
