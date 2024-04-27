#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pandas
from athlete import Athlete

def time_convert_to_str(time: int|float) -> str:
    out = ""
    h = time // 3600
    if h != 0:
        out = f"{h}:"
        time -= h * 3600
    # We want to keep the decisecond
    return f"{out}{int(time // 60):02}:{int(time - (time//60)*60):02}"

def time_convert_to_float(time: str) -> float:
    m, s = time.split(":")
    return float(m) * 60 + float(s)

class Simulation:
    def load_csv(self, path_file: str) -> None:
        self.file = path_file
        self.data = pandas.read_csv(path_file)
        self.waiting: dict[float, list[Athlete]] = {}
        self.skiing: list[Athlete] = []
        self.done: list[Athlete] = []

        if self.file.find("_") == -1:
            raise AttributeError("Cannot find the distance in the file name")
        self.distance = int(self.file.split("_")[-1].split(".")[0]) * 1000

        for i in range(len(self.data)):
            A = Athlete(self.data["name"][i], 0, dict(self.data.iloc[i]))
            t = time_convert_to_float(A.get("jump_time_diff"))
            if t in self.waiting:
                self.waiting[t].append(A)
            else:
                self.waiting[t] = [A]

    def guess_avg_speed(self, a: Athlete) -> float:
        raise NotImplementedError("Cannot use this class to simulate, please use a derived class")

class SimpleSim(Simulation):
    def __init__(self, dt: float) -> None:
        self.dt = dt
        self.ended = False

    def guess_avg_speed(self, a: Athlete) -> float:
        return self.distance / time_convert_to_float(a.get("cross_time"))

    def start(self) -> None:
        for i in self.waiting:
            for j in range(len(self.waiting[i])):
                self.waiting[i][j].avg_speed = self.guess_avg_speed(self.waiting[i][j])
        self.t = .0
        for a in self.waiting[self.t]:
            self.skiing.append(a)
        self.waiting.pop(self.t)

        # for t in self.waiting:
        #     print(f"{t}: {self.waiting[t]}")

    def update(self) -> None:
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
