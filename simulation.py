#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

import matplotlib.pyplot as plt
import pandas

import athlete
import render
import utils


class Simulation(render.SimuRender):
    """Base class for simulation"""

    all_athletes: list[athlete.Athlete] = []

    # Time, distance
    t: float = 0.0
    dt: float = 0.0
    distance: float = 0.0

    # Simulation status
    num_athlete: int = 0
    max_place: int = -1
    use_random = False

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
        self.all_athletes = []

        # For each record of athlete, create an Athlete object
        for i in range(len(self.data["name"])):
            self.num_athlete += 1
            A = athlete.Athlete(
                self.data["name"][i], self.dt, dict(self.data.iloc[i]), self.use_random
            )
            self.all_athletes.append(A)
            self.max_place = max(self.max_place, A.starting_place + 1)

        # Rendering records
        self.time = {name: [] for name in self.data["name"]}
        self.dist = {name: [] for name in self.data["name"]}
        self.frames = {}

    def update(self) -> None:
        """Update the state of the simulation."""
        raise NotImplementedError(
            "Cannot use this class to simulate, please use a derived class"
        )

    def guess_avg_speed(self, a: athlete.Athlete) -> float:
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

        self.done = []
        self.skiing = []

        # Change the status of the first athletes
        if self.t not in self.waiting:
            return
        for a in self.waiting[self.t]:
            self.skiing.append(a)
        self.waiting.pop(self.t)

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

    def excat_rate(self) -> (float, float, float):
        if not self.ended:
            raise ValueError("Cannot use this function if the simulation did not end")
        n = self.num_athlete
        assert len(self.done) == n, "Why are those values not equal ?"
        exact_position = 0
        for i in range(n):
            er = self.done[i].expected_rank
            sr = self.done[i].rank
            # Count the number of exact position
            if er == sr:
                exact_position += 1
        return (exact_position, n, exact_position / n * 100)

    def adapt_rate(self) -> (float, float, float):
        if not self.ended:
            raise ValueError("Cannot use this function if the simulation did not end")
        n = self.num_athlete
        assert len(self.done) == n, "Why are those values not equal ?"

        real_rank = ["" for _ in range(max([a.expected_rank for a in self.done]))]
        simu_rank = ["" for _ in range(max([a.rank for a in self.done]))]
        for i in range(n):
            er = self.done[i].expected_rank
            sr = self.done[i].rank
            real_rank[er - 1] = self.done[i].name
            simu_rank[sr - 1] = self.done[i].name

        # List athletes before and after each athlete, both in the real race and in the simulation
        afters_real: dict[str, list[str]] = {}
        afters_simu: dict[str, list[str]] = {}
        before_real: dict[str, list[str]] = {}
        before_simu: dict[str, list[str]] = {}
        i = 0
        for k in range(min(len(simu_rank), len(real_rank))):
            if (real_rank[k] == "") or (simu_rank[k] == ""):
                continue
            afters_real[real_rank[i]] = real_rank[i + 1 :]
            afters_simu[simu_rank[i]] = simu_rank[i + 1 :]
            before_real[real_rank[i]] = real_rank[:i]
            before_simu[simu_rank[i]] = simu_rank[:i]
            i += 1

        # Count the number of athlete that are in the correct part (before and after an athlete)
        adapted_position = 0
        total = int((n - 1) * n)
        for a in afters_real:
            if a not in afters_simu:
                continue
            for after in afters_real[a]:
                if after in afters_simu[a]:
                    adapted_position += 1
        for a in before_real:
            if a not in before_simu:
                continue
            for before in before_real[a]:
                if before in before_simu[a]:
                    adapted_position += 1

        return (adapted_position, total, adapted_position / total * 100)

    def correctness(self) -> None:
        exact_position, n, per_e = self.excat_rate()
        adapted_position, total, per_a = self.adapt_rate()
        n = self.num_athlete

        print(
            f"\nExact position: {exact_position} / {n} ({per_e:6.3}%)"
        )
        print(
            f"Adapted metric: {adapted_position} / {total} = ({per_a:6.3}%)"
        )

    def show_energy_evol(self, num: int = 0) -> None:
        """Should only be used after the simulatio is done"""
        if num == -1:
            r = range(self.num_athlete)
        else:
            r = range(num, num + 1, 1)

        # print(self.done[1].energies[-1])
        # self.done[0].energies.append(325)
        # print(self.done[1].energies[-1])

        # print(self.done[1].energy)
        # self.done[0].energy = 325
        # print(self.done[1].energy)

        # if self.done[0].energies == self.done[1].energies:
        #     print("problem")
        done = 0
        print("")
        # plt.ylim(-5, 105)
        for i in r:
            athlete = self.done[i]
            print(athlete.name)
            speed = athlete.speeds[athlete.name]
            # plt.plot(
            #     [(i + athlete.start_time()) / 60 for i in range(len(energy))],
            #     [i * 3.6 for i in energy],
            # )

            sample_per_min = 60 / self.dt
            avg = []
            for i in range(len(speed)):
                if i < sample_per_min:
                    min = 0.0
                    max = sample_per_min
                elif len(speed) - i < sample_per_min:
                    min = len(speed) - sample_per_min
                    max = len(speed)
                else:
                    min = i - sample_per_min // 2
                    max = i + sample_per_min // 2 + 1
                avg.append(sum(speed[int(min):int(max)]) / len(speed[int(min):int(max)]))

            plt.plot(
                [(i * self.dt + athlete.start_time()) / 60 for i in range(len(speed))],
                [i * 3.6 * 3.22 for i in avg],
            )
            print(f"{done} / {len(r)}", end="\r")
            done += 1

        for i in r:
            athlete = self.done[i]
            energy = athlete.energies[athlete.name]
            plt.plot(
                [(i * self.dt + athlete.start_time()) / 60 for i in range(len(energy))],
                energy,
            )

        plt.xlabel("Time (in min)")
        # plt.ylabel("Energy level (in %)")
        plt.show()
        plt.close()

    def start_update(self) -> None:
        self.t = round(self.t + self.dt, 3)

        if self.t in self.waiting:
            for a in self.waiting[self.t]:
                self.skiing.append(a)
            self.waiting.pop(self.t)

        text = f"{utils.time_convert_to_str(self.t)}, {len(self.done)} / {self.num_athlete}"
        m: athlete.Athlete | None = None
        for a in self.skiing:
            if (a.rank != -1) and ((m is None) or (a.rank < m.rank)):
                m = a
        if m is not None:
            text = f"{text}, {int(self.distance - m.distance):05}m to go"

        print(text, end="\r")


    def write(self) -> None:
        with open("data", "a") as f:
            for a in self.done:
                f.write(f"{a.name}, {a.rank}, {a.expected_rank}, {a.time}\n")

    def give_points(self) -> dict[str, int]:
        assert self.ended
        print("")
        points = {}
        values = [100, 90, 80, 70, 60, 55, 52, 49, 46, 43, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        for a in self.done:
            sr = a.rank - 1
            if sr >= len(values):
                sp = 0
            else:
                sp = values[sr]
            rr = a.expected_rank - 1
            if rr >= len(values):
                rp = 0
            else:
                rp = values[rr]
            with open("data.csv", "a") as f:
                f.write(f"{a.name}, {sp}, {rp}\n")
            # print(f"{a.name} ({a.rank}) -> {values[a.rank]}")
        return points


class SimpleSim(Simulation):
    """A simple simulation without collision, air resistance, or anything really"""

    def __init__(self, dt: float) -> None:
        self.dt = dt

    def guess_avg_speed(self, a: athlete.Athlete) -> float:
        """Return the average speed"""
        return self.distance / utils.time_convert_to_float(a.get("cross_time"))

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

    def guess_avg_speed(self, a: athlete.Athlete) -> float:
        """Return the average speed"""
        t = a.total_time
        d = a.total_distance
        if (t == 0) or (d == 0):
            t = utils.time_convert_to_float(a.get("cross_time"))
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
                    self.all_athletes[k].total_time += utils.time_convert_to_float(
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
            d = 0.0

            for j in range(0, len(self.skiing)):
                if i == j:
                    continue
                other = self.skiing[j]
                d = other.distance - a.distance
                # The athlete has to be < 2m behind the guy in front
                if d < 2.0 and d > 0.5:
                    can_activate_boost = True
                    break

            # If slipstream, you get a boost
            if not self.skiing[i].boost.is_active(self.t):
                if can_activate_boost:
                    # Activate the boost only if the athlete can (but prob that it fails)
                    if a.can_boost() and (random.random() < self.prob_activation_boost):
                        self.skiing[i].boost.change(self.t)
                else:
                    self.skiing[i].boost.reset()

            # Update the position of the athletes
            self.skiing[i].update(self.dt)

            # Remove the athlete if went over the distance (finished)
            if self.skiing[i].distance >= self.distance:
                self.done.append(self.skiing[i])
                self.skiing.pop(i)
            else:
                i += 1

        self.finish_update()
