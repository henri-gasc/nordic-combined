#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import os
import sys

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import FuncAnimation

import simulation


def select(l: list[str]) -> int:
    if len(l) == 1:
        return 0
    for i in range(len(l)):
        print(f"[{i+1:02}] {l[i]}")
    selected = len(l)
    while (-1 > selected) or (selected >= len(l)):
        inp = input(f"Enter the number of the file you want to load: ")
        if inp.lower()[0] == "q" or inp == "":
            inp = "-1"
        try:
            selected = int(inp)
        except ValueError:
            print(f"{inp} is not a valid number")
    if selected == -1:
        print("No race selected")
        exit(1)
    return selected - 1


def start(i: int | None = None, j: int | None = None) -> simulation.Simulation:
    l = os.listdir("extracted")
    if len(l) == 0:
        print("There is no data extracted. Please use extract.py")
        exit(1)
    if i is None:
        i = select(l)

    path_season = os.path.join("extracted", l[i])
    is_season = os.path.isdir(path_season) and (l[i][:6].lower() == "season")
    if is_season:
        l = sorted(os.listdir(path_season))
        if len(l) == 0:
            print("There is no race data here")
            exit(1)
        if j is None:
            print("Season detected. Which race do you want to simulate ?")
            j = select(l)
        path = os.path.join(path_season, l[j])
    else:
        path = path_season

    sim = simulation.SlipstreamSim(0.05)
    # sim = simulation.SimpleSim(0.05)
    sim.load_csv(path)

    if is_season:
        num = int(os.path.basename(path).split(" ")[0])
        l = os.listdir(path_season)
        for race in l:
            if int(race.split(" ")[0]) < num:
                sim.prepare_race(os.path.join(path_season, race))

    return sim


def run(values: tuple[int | None, int | None, bool]) -> None:
    i, j, render = values
    sim = start(i, j)
    sim.render = render

    sim.start()
    while not sim.ended:
        sim.update()

    # sim.show_energy_evol()
    sim.correctness()
    # sim.compare_positions()

    sim.render_write()


i = None
j = None
MULTI_DEFAULT = 10
use_multi = -1
use_render = False
k = 0
while k < len(sys.argv):
    arg = sys.argv[k]

    if arg == "-i":
        k += 1
        i = int(sys.argv[k])
    elif arg == "-j":
        k += 1
        j = int(sys.argv[k])
    elif (arg == "-m") or (arg == "--multi"):
        try:
            use_multi = int(sys.argv[k+1])
            k += 1
        except ValueError:
            use_multi = MULTI_DEFAULT
        except IndexError:
            use_multi = MULTI_DEFAULT
    elif (arg == "-r") or (arg == "--render"):
        use_render = True
    elif arg[-7:] == "main.py":
        pass
    else:
        print(f"Unknow argument {arg}")

    k += 1

if use_multi == -1:
    run((i, j, use_render))
else:
    pool = multiprocessing.Pool()
    pool.map(run, [(i, j, use_render) for _ in range(use_multi)])

# ffmpeg command:
# ffmpeg -i imgs/%5d.png video.mp4
