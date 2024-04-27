#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt
import pandas

from athlete import Athlete


def time_convert_to_str(time: int | float) -> str:
    """Convert time (in seconds) to a string of format hh:mm:ss
    The hh: is ommitted if equal to 0"""
    out = ""
    h = time // 3600
    if h != 0:
        out = f"{h}:"
        time -= h * 3600
    # We want to keep the decisecond
    return f"{out}{int(time // 60):02}:{int(time - (time//60)*60):02}"


def time_convert_to_float(time: str) -> float:
    """Split time at : and return the time in seconds"""
    m, s = time.split(":")
    return float(m) * 60 + float(s)


class Simulation:
    """Base class for simulation"""

    frame: int = 0
    t: float = 0.0
    dt: float = 0.0
    distance: float = 0.0
    num_athlete: int = 0
    ended = False
    render = False
    waiting: dict[float, list[Athlete]] = {}
    skiing: list[Athlete] = []
    done: list[Athlete] = []
    color = plt.cm.get_cmap("hsv", 0)

    def load_csv(self, path_file: str) -> None:
        """Load the csv, create the list of athletes waiting"""
        self.file = path_file
        self.data = pandas.read_csv(path_file)

        if self.file.find("_") == -1:
            raise AttributeError("Cannot find the distance in the file name")
        self.distance = int(self.file.split("_")[-1].split(".")[0]) * 1000

        for i in range(len(self.data["name"])):
            self.num_athlete += 1
            A = Athlete(self.data["name"][i], self.num_athlete, dict(self.data.iloc[i]))
            t = time_convert_to_float(A.get("jump_time_diff"))
            if t in self.waiting:
                self.waiting[t].append(A)
            else:
                self.waiting[t] = [A]

        self.color = plt.cm.get_cmap("hsv", self.num_athlete)
        self.time: dict[str, list[float]] = {name: [] for name in self.data["name"]}
        self.dist: dict[str, list[float]] = {name: [] for name in self.data["name"]}

    def guess_avg_speed(self, a: Athlete) -> float:
        """Return the average speed for an athlete"""
        raise NotImplementedError(
            "Cannot use this class to simulate, please use a derived class"
        )


class SimpleSim(Simulation):
    """A simple simulation without collision, air resistance, or anything really"""

    def __init__(self, dt: float) -> None:
        self.dt = dt
        self.fig, self.axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))

    def guess_avg_speed(self, a: Athlete) -> float:
        """Return the average speed"""
        return self.distance / time_convert_to_float(a.get("cross_time"))

    def start(self) -> None:
        """Initialize the simulation"""
        for i in self.waiting:
            for j in range(len(self.waiting[i])):
                self.waiting[i][j].avg_speed = self.guess_avg_speed(self.waiting[i][j])
        self.t = .0
        self.frame = 0
        self.ended = False
        for a in self.waiting[self.t]:
            self.skiing.append(a)
        self.waiting.pop(self.t)

        # plt.ylim([0, self.num_athlete])
        self.axes.set_ylim([0, self.num_athlete])

    def update(self) -> None:
        """Update the state of the simulation.
        If some athlete can now start the cross crountry, make them start.
        Remove the athlete from the race if they finished."""
        print(time_convert_to_str(self.t), end="\r")
        self.frame += 1
        self.t += self.dt
        if self.t in self.waiting:
            for a in self.waiting[self.t]:
                self.skiing.append(a)
            self.waiting.pop(self.t)

        i = 0
        while i < len(self.skiing):
            self.skiing[i].update(self.dt)
            if self.skiing[i].distance >= self.distance:
                self.done.append(self.skiing[i])
                self.skiing.pop(i)
            else:
                i += 1

        if len(self.skiing) == len(self.waiting) == 0:
            self.ended = True

        # for a in self.skiing:
        #     self.time[a.name].append(self.t / 60)
        #     self.dist[a.name].append(a.distance / 1000)

        if self.render:
            # for name in self.time:
            #     self.axes.plot(self.time[name], self.dist[name])
            for a in self.skiing:
                self.axes.plot([0, a.time], [a.starting_place, a.starting_place], color=self.color(a.starting_place))
            self.fig.savefig(os.path.join("imgs", f"{self.frame:05}.png"))
