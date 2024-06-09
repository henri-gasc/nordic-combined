#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

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


l = os.listdir("extracted")
if len(l) == 0:
    print("There is no data extracted. Please use extract.py")
    exit(1)
i = select(l)

path_season = os.path.join("extracted", l[i])
is_season = os.path.isdir(path_season) and (l[i][:6].lower() == "season")
if is_season:
    l = sorted(os.listdir(path_season))
    if len(l) == 0:
        print("There is no race data here")
        exit(1)
    print("Season detected. Which race do you want to simulate ?")
    i = select(l)
    path = os.path.join(path_season, l[i])
else:
    path = path_season

sim = simulation.SlipstreamSim(0.05)
# sim = simulation.SimpleSim(0.05)
sim.load_csv(path)
sim.render = False

if is_season:
    num = int(os.path.basename(path).split(" ")[0])
    l = os.listdir(path_season)
    for race in l:
        if int(race.split(" ")[0]) < num:
            sim.prepare_race(os.path.join(path_season, race))

sim.start()
while not sim.ended:
    sim.update()

sim.compare_positions()
sim.correctness()

sim.render_write()

# ffmpeg command:
# ffmpeg -i imgs/%5d.png video.mp4
