#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import os
import sys

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import FuncAnimation

import simulation
import utils

correct_a = 0
correct_e = 0
total_a = 0
total_e = 0


def start(i: int | None = None, j: int | None = None) -> simulation.Simulation:
    l = os.listdir("extracted")
    if len(l) == 0:
        print("There is no data extracted. Please use extract.py")
        exit(1)
    if i is None:
        i = utils.select(l)

    path_season = os.path.join("extracted", l[i])
    is_season = os.path.isdir(path_season) and (l[i][:6].lower() == "season")
    is_race = os.path.isdir(path_season) and (l[i][:6].lower() == "race")
    if is_season:
        l = sorted(os.listdir(path_season))
        if len(l) == 0:
            print("There is no race data here")
            exit(1)
        if j is None:
            print("Season detected. Which race do you want to simulate ?")
            j = utils.select(l)
        path = os.path.join(path_season, l[j])
    elif is_race:
        l = sorted(os.listdir(path_season))
        if len(l) == 0:
            print("There is no race data here")
            exit(1)
        if j is None:
            print("Race detected. For which season do you want to simulate ?")
            j = utils.select(l)
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


def run(values: tuple[int | None, int | None, bool, int]) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    i, j, render, s = values
    if s is not None:
        import time; time.sleep(s)
    sim = start(i, j)
    sim.render = render

    sim.start()
    while not sim.ended:
        sim.update()

    # sim.show_energy_evol(-1)
    # sim.correctness()
    # sim.compare_positions()

    sim.write()

    sim.render_write()
    return (sim.excat_rate(), sim.adapt_rate())


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
            use_multi = int(sys.argv[k + 1])
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
    # for _ in range(1000):
    run((i, j, use_render, None))
else:
    pool = multiprocessing.Pool()
    out = pool.map(run, [(i, j, use_render, k) for k in range(use_multi)])
    for race in out:
        e, a = race
        correct_a += a[0]
        total_a += a[1]
        correct_e += e[0]
        total_e += e[1]

print(
    f"\nExact position: {correct_e} / {total_e} ({(correct_e / total_e * 100):6.3}%)"
)
print(
    f"Adapted metric: {correct_a} / {total_a} = ({(correct_a / total_a * 100):6.3}%)"
)

# ffmpeg command:
# ffmpeg -i imgs/%5d.png video.mp4
