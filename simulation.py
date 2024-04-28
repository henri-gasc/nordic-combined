#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt
from labellines import labelLines
import multiprocessing
import shutil
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
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    def load_csv(self, path_file: str) -> None:
        """Load the csv, create the list of athletes waiting"""
        self.file = path_file
        self.data = pandas.read_csv(path_file)

        if self.file.find("_") == -1:
            raise AttributeError("Cannot find the distance in the file name")
        self.distance = int(self.file.split("_")[-1].split(".")[0]) * 1000

        ranks = []
        for i in range(len(self.data["name"])):
            self.num_athlete += 1
            r = self.data["jump_rank"][i]
            while r in ranks:
                r += 1
            ranks.append(r)
            A = Athlete(self.data["name"][i], r, dict(self.data.iloc[i]))
            t = time_convert_to_float(A.get("jump_time_diff"))
            if t in self.waiting:
                self.waiting[t].append(A)
            else:
                self.waiting[t] = [A]

        self.time: dict[str, list[float]] = {name: [] for name in self.data["name"]}
        self.dist: dict[str, list[float]] = {name: [] for name in self.data["name"]}
        self.frames: dict[int, dict[int, tuple[int, float, float]]] = {}

    def guess_avg_speed(self, a: Athlete) -> float:
        """Return the average speed for an athlete"""
        raise NotImplementedError(
            "Cannot use this class to simulate, please use a derived class"
        )

    def save_frame(self, frame: int) -> None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
        ax.set_xlabel(f"Distance (in m)")
        ax.set_ylabel("Starting position")
        ax.set_ylim([0, self.num_athlete+2])
        xvals = []
        for p in self.frames[frame]:
            c = self.colors[(p-1)%len(self.colors)]
            data = self.frames[frame][p]
            ax.plot(data[1:], [p, p], color=c, label=f"{data[0]}")
            d = abs(data[2] - data[1])
            x = data[1] + d/2 * (1 + 0.2*((p%3)-1))
            if (x < data[1]) or (x > data[2]):
                print(data[1], data[2], p)
            xvals.append(x)
        labelLines(ax.get_lines(), xvals=xvals)
        fig.savefig(os.path.join("imgs", f"{frame:05}.png"))
        plt.close(fig)
        print(f"{len(os.listdir('imgs'))/len(self.frames)*100:4.4}% is done  ", end="\r")

    def write(self) -> None:
        pool = multiprocessing.Pool()
        shutil.rmtree("imgs")
        os.makedirs("imgs", exist_ok=True)
        pool.map(self.save_frame, range(1, len(self.frames)+1))


class SimpleSim(Simulation):
    """A simple simulation without collision, air resistance, or anything really"""

    def __init__(self, dt: float) -> None:
        self.dt = dt

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
        
        for i in range(len(self.skiing)):
            for j in range(len(self.skiing)):
                if (self.skiing[i].distance > self.skiing[j].distance) and (self.skiing[i].rank > self.skiing[j].rank):
                    self.skiing[i].overtake(self.skiing[j])

        if len(self.skiing) == len(self.waiting) == 0:
            self.ended = True

        # for a in self.skiing:
        #     self.time[a.name].append(self.t / 60)
        #     self.dist[a.name].append(a.distance / 1000)

        all_athlete = []
        for l in self.waiting:
            all_athlete += self.waiting[l]
        all_athlete += self.skiing.copy() + self.done.copy()
        m = min([a.distance for a in all_athlete])
        if m > 500:
            m -= 500
        else:
            m = 0

        if self.ended:
            for i in range(250):
                self.add_data(m)
                self.frame += 1
        else:
            self.add_data(m)

    def add_data(self, m: float) -> None:
        # There can not be* more than one athlete with a starting place, and they cannot be in self.skiing an self.done at the same time
        self.frames[self.frame] = {}
        for a in self.skiing.copy() + self.done.copy():
            self.frames[self.frame][a.starting_place] = (a.rank, m, a.distance)
        # self.time[a.name][self.frame] = [0, a.time]
        # self.dist[a.name][self.frame] = [a.starting_place, a.starting_place]
