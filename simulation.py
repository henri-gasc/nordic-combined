#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import os
import random
import shutil

import matplotlib.pyplot as plt
import pandas
from labellines import labelLines

from athlete import Athlete, time_convert_to_float


def time_convert_to_str(time: int | float) -> str:
    """Convert time (in seconds) to a string of format hh:mm:ss
    The hh: is ommitted if equal to 0"""
    out = ""
    h = time // 3600
    if h != 0:
        out = f"{int(h)}:"
        time -= h * 3600
    # We want to keep the decisecond
    return f"{out}{int(time // 60):02}:{int(time - (time//60)*60):02}"


class Simulation:
    """Base class for simulation"""

    # Athlete status
    waiting: dict[float, list[Athlete]] = {}
    skiing: list[Athlete] = []
    done: list[Athlete] = []
    all_athletes: list[Athlete] = []

    # Time, distance
    t: float = 0.0
    dt: float = 0.0
    distance: float = 0.0

    # Simulation status
    num_athlete: int = 0
    max_place: int = -1
    ended = False
    use_random = False

    # Rendering
    frame: int = 0
    render = False
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    def read_csv(self, path_file: str) -> tuple[pandas.DataFrame, int]:
        data = pandas.read_csv(path_file)
        if path_file.find("_") == -1:
            raise AttributeError("Cannot find the distance in the file name")
        distance = int(path_file.split("_")[-1].split(".")[0]) * 1000
        return data, distance

    def load_csv(self, path_file: str) -> None:
        """Load the csv, create the list of athletes waiting"""
        self.file = path_file
        self.data, self.distance = self.read_csv(path_file)

        # For each record of athlete, create an Athlete object
        for i in range(len(self.data["name"])):
            self.num_athlete += 1
            A = Athlete(
                self.data["name"][i], self.dt, dict(self.data.iloc[i]), self.use_random
            )
            self.all_athletes.append(A)
            self.max_place = max(self.max_place, A.starting_place + 1)

        # Rendering records
        self.time: dict[str, list[float]] = {name: [] for name in self.data["name"]}
        self.dist: dict[str, list[float]] = {name: [] for name in self.data["name"]}
        self.frames: dict[int, dict[int, tuple[int, float, float]]] = {}

    def update(self) -> None:
        """Update the state of the simulation."""
        raise NotImplementedError(
            "Cannot use this class to simulate, please use a derived class"
        )

    def guess_avg_speed(self, a: Athlete) -> float:
        """Return the average speed for an athlete"""
        raise NotImplementedError(
            "Cannot use this class to simulate, please use a derived class"
        )

    def prepare_race(self, path: str) -> None:
        """Load the csv to compute the average speed"""
        raise NotImplementedError(
            "Cannot use this class to simulate, please use a derived class"
        )

    def start(self) -> None:
        """Initialize the simulation"""

        for a in self.all_athletes:
            # Set the average speed for all athletes
            a.avg_speed = self.guess_avg_speed(a)
            # Put all athletes in waiting zone
            t = a.start_time()
            if t in self.waiting:
                self.waiting[t].append(a)
            else:
                self.waiting[t] = [a]

        # Reset some variables
        self.t = 0.0
        self.frame = 0
        self.ended = False

        # Change the status of the first athletes
        for a in self.waiting[self.t]:
            self.skiing.append(a)
        self.waiting.pop(self.t)

    def render_save_frame(self, frame: int) -> None:
        """Save the frame on disk. Written to be used via multiprocessing"""
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
        ax.set_xlabel(f"Distance (in m)")
        ax.set_ylabel("Starting position")
        ax.set_ylim([0, self.max_place + 1])
        xvals = []
        for p in self.frames[frame]:
            c = self.colors[(p - 1) % len(self.colors)]
            data = self.frames[frame][p]
            ax.plot(data[1:], [p, p], color=c, label=f"{data[0]}")
            d = abs(data[2] - data[1])
            x = data[1] + d / 2 * (1 + 0.2 * ((p % 3) - 1))
            if (x < data[1]) or (x > data[2]):
                print(data[1], data[2], p)
            xvals.append(x)
        labelLines(ax.get_lines(), xvals=xvals)
        fig.savefig(os.path.join("imgs", f"{frame:05}.png"))
        plt.close(fig)
        print(
            f"{len(os.listdir('imgs'))/len(self.frames)*100:4.4}% is done  ", end="\r"
        )

    def render_write(self) -> None:
        """Create a multiprocessing pool to write all frames to disk"""
        if not self.render:
            return
        pool = multiprocessing.Pool()
        shutil.rmtree("imgs")
        os.makedirs("imgs", exist_ok=True)
        pool.map(self.render_save_frame, range(1, len(self.frames) + 1))

    def render_update_data(self) -> None:
        """Update the data used in rendering"""
        # Get all athletes
        all_athlete = []
        for l in self.waiting:
            all_athlete += self.waiting[l]
        all_athlete += self.skiing.copy() + self.done.copy()

        # Keep the plotted window around the the min and max without a big zoom out
        m = min([a.distance for a in all_athlete])
        if m > 500:
            m -= 500
        else:
            m = 0

        if self.ended:
            # Fix the render for some time at the end
            for i in range(250):
                self.render_add_data(m)
                self.frame += 1
        else:
            self.render_add_data(m)

    def render_add_data(self, m: float) -> None:
        # There can not be* more than one athlete with a starting place, and they cannot be in self.skiing an self.done at the same time
        self.frames[self.frame] = {}
        for a in self.skiing.copy() + self.done.copy():
            self.frames[self.frame][self.max_place - a.starting_place] = (
                a.rank,
                m,
                a.distance,
            )
        # self.time[a.name][self.frame] = [0, a.time]
        # self.dist[a.name][self.frame] = [a.starting_place, a.starting_place]

    def compare_positions(self) -> None:
        """Plot the expected and real ending position and the name for each athlete"""
        x_start = 0
        x_end = 5
        x_mid = 0.5 * (x_end - x_start)
        plt.axis("off")
        plt.xlim(x_start, x_end + x_mid)
        for a in self.done:
            y_start = self.num_athlete - a.expected_rank
            y_end = self.num_athlete - a.rank
            plt.plot([x_start, x_end], [y_start, y_end])
            plt.text(
                x_end + x_mid / 50,
                y_end - 0.30,
                f"{a.name} {a.starting_place:02}: {a.expected_rank:02} -> {a.rank:02}",
            )
            if (a.expected_rank % 5) == 0:
                plt.text(x_start - x_mid / 20, y_start - 0.30, f"{a.expected_rank:02}")
        plt.show()
        plt.close()

    def update_rank(self) -> None:
        places = {}
        for i in range(len(self.skiing)):
            places[self.skiing[i].name] = self.skiing[i].distance
        # Sort the dict
        places = {
            k: v
            for k, v in sorted(places.items(), key=lambda item: item[1], reverse=True)
        }

        # Give the rank to the correct athlete
        for i in range(len(self.skiing)):
            self.skiing[i].rank = (
                1 + len(self.done) + list(places.keys()).index(self.skiing[i].name)
            )

    def finish_update(self) -> None:
        self.update_rank()

        # If no more athletes are running or waiting, the simulation ended
        if len(self.skiing) == len(self.waiting) == 0:
            self.ended = True

        if round(self.t, 0) == self.t:
            self.frame += 1
            self.render_update_data()

    def correctness(self) -> None:
        if not self.ended:
            raise ValueError("Cannot use this function if the simulation did not end")
        n = self.num_athlete
        assert len(self.done) == n, "Why are those values not equal ?"

        exact_position = 0
        real_rank = ["" for _ in range(n)]
        simu_rank = ["" for _ in range(n)]
        for i in range(n):
            er = self.done[i].expected_rank
            sr = self.done[i].rank
            # Count the number of exact position
            if er == sr:
                exact_position += 1
            real_rank[er - 1] = self.done[i].name
            simu_rank[sr - 1] = self.done[i].name

        # List athletes before and after each athlete, both in the real race and in the simulation
        afters_real: dict[str, list[str]] = {}
        afters_simu: dict[str, list[str]] = {}
        before_real: dict[str, list[str]] = {}
        before_simu: dict[str, list[str]] = {}
        for i in range(n):
            afters_real[real_rank[i]] = real_rank[i + 1 :]
            afters_simu[simu_rank[i]] = simu_rank[i + 1 :]
            before_real[real_rank[i]] = real_rank[:i]
            before_simu[simu_rank[i]] = simu_rank[:i]

        # Count the number of athlete that are in the correct part (before and after an athlete)
        adapted_position = 0
        total = int((n - 1) * n)
        for a in afters_real:
            for after in afters_real[a]:
                if after in afters_simu[a]:
                    adapted_position += 1
        for a in before_real:
            for before in before_real[a]:
                if before in before_simu[a]:
                    adapted_position += 1

        print(
            f"\nExact position: {exact_position} / {n} ({(exact_position/n*100):6.3}%)"
        )
        print(
            f"Adapted metric: {adapted_position} / {total} = ({(adapted_position/total*100):6.3}%)"
        )

    def show_energy_evol(self, num: int = 0) -> None:
        """Should only be used after the simulatio is done"""
        if num == -1:
            r = range(self.num_athlete)
        else:
            r = range(num, num + 1, 1)

        plt.ylim(-5, 105)
        for i in r:
            athlete = self.done[i]
            energy = athlete.energies
            plt.plot(range(len(energy)), energy)

        plt.show()
        plt.close()

    def start_update(self) -> None:
        self.t = round(self.t + self.dt, 3)

        if self.t in self.waiting:
            for a in self.waiting[self.t]:
                self.skiing.append(a)
            self.waiting.pop(self.t)

        text = f"{time_convert_to_str(self.t)}, {len(self.done)} / {self.num_athlete}"
        m: Athlete | None = None
        for a in self.skiing:
            if (a.rank != -1) and ((m is None) or (a.rank < m.rank)):
                m = a
        if m is not None:
            text = f"{text}, {int(self.distance - m.distance):05}m to go"

        print(text, end="\r")


class SimpleSim(Simulation):
    """A simple simulation without collision, air resistance, or anything really"""

    def __init__(self, dt: float) -> None:
        self.dt = dt

    def guess_avg_speed(self, a: Athlete) -> float:
        """Return the average speed"""
        return self.distance / time_convert_to_float(a.get("cross_time"))

    def update(self) -> None:
        """Update the state of the simulation.
        If some athlete can now start the cross crountry, make them start.
        Remove the athlete from the race if they finished."""

        self.start_update()

        # Update all athletes that are not finished
        i = 0
        while i < len(self.skiing):
            self.skiing[i].update(self.dt)
            if self.skiing[i].distance >= self.distance:
                self.done.append(self.skiing[i])
                self.skiing.pop(i)
            else:
                i += 1

        self.finish_update()


class SlipstreamSim(Simulation):
    """A more advanced simulation, notably with a attempt to recreate the slipstream effect"""

    prob_activation_boost = 0.90

    def __init__(self, dt: float) -> None:
        self.dt = dt
        self.use_random = True

    def guess_avg_speed(self, a: Athlete) -> float:
        """Return the average speed"""
        t = a.total_time
        d = a.total_distance
        if (t == 0) or (d == 0):
            t = time_convert_to_float(a.get("cross_time"))
            d = self.distance
        # s = self.distance / t
        # print(f"{a.name:30}: {(s * 3.6):.05} ({self.distance}m in {t}s)")
        return d / t

    def prepare_race(self, path: str) -> None:
        """Should only be used after self.load_csv"""
        data, distance = self.read_csv(path)
        for k in range(len(self.all_athletes)):
            a = self.all_athletes[k]
            for i in range(len(data.name)):
                if data.name[i] == self.all_athletes[k].name:
                    self.all_athletes[k].total_distance += distance
                    self.all_athletes[k].total_time += time_convert_to_float(
                        data.cross_time[i]
                    )

    def update(self) -> None:
        """Update the state of the simulation.
        If some athlete can now start the cross crountry, make them start.
        Remove the athlete from the race if they finished."""

        # Update state and add skiing athletes
        self.start_update()

        i = 0
        while i < len(self.skiing):
            a = self.skiing[i]

            # Test wether an athlete benifits from slipstream effect
            can_activate_boost = False
            force_change = False
            d = 0.0

            for j in range(0, len(self.skiing)):
                if i == j:
                    continue
                other = self.skiing[j]
                d = other.distance - a.distance
                if d < 2.0 and d > 0.5:
                    # If the athlete in front is slower by more than 1km/h, he is overtaken
                    if other.avg_speed < (
                        a.avg_speed - 0.278
                    ):  # The speed is stored in m/s
                        force_change = True
                    can_activate_boost = True
                    break

            # If slipstream, you get a boost
            if not (force_change or self.skiing[i].boost.is_active(self.t)):
                if can_activate_boost:
                    # Activate the boost only if the athlete can (but prob that it fails)
                    if a.can_boost() and (random.random() < self.prob_activation_boost):
                        self.skiing[i].boost.change(self.t)
                else:
                    self.skiing[i].boost.reset()

            # Update the position of the athletes
            if force_change:
                # Go a little further than just the position
                self.skiing[i].update(self.dt, d / self.dt * 2)
            else:
                self.skiing[i].update(self.dt)

            # Remove the athlete if went over the distance (finished)
            if self.skiing[i].distance >= self.distance:
                self.done.append(self.skiing[i])
                self.skiing.pop(i)
            else:
                i += 1

        self.finish_update()
