#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import os
import shutil

import matplotlib.pyplot as plt
from labellines import labelLines

import athlete


class SimuRender:
    # Used in functions here, but changed in athlete.Athlete
    ended = False
    waiting: dict[float, list[athlete.Athlete]] = {}
    skiing: list[athlete.Athlete] = []
    done: list[athlete.Athlete] = []

    # Rendering
    frame: int = 0
    max_place: int = -1
    render = False
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    # Rendering records
    time: dict[str, list[float]] = {}
    dist: dict[str, list[float]] = {}
    frames: dict[int, dict[int, tuple[int, float, float]]] = {}

    def render_save_frame(self, frame: int) -> None:
        """Save the frame on disk. Written to be used via multiprocessing"""
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
        ax.set_xlabel(f"Distance (in m)")
        ax.set_ylabel("Starting position")
        ax.set_ylim([0, self.max_place + 1])
        ax.invert_yaxis()
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
            self.frames[self.frame][a.starting_place] = (
                a.rank,
                m,
                a.distance,
            )
        # self.time[a.name][self.frame] = [0, a.time]
        # self.dist[a.name][self.frame] = [a.starting_place, a.starting_place]
