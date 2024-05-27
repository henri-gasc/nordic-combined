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
    return selected


l = os.listdir("extracted")
if len(l) == 0:
    print("There is no data extracted. Please use extract.py")
    exit(1)
i = select(l)
if i == -1:
    exit(0)

sim = simulation.SlitstreamSim(0.5)
# sim = simulation.SimpleSim(1)
sim.load_csv(os.path.join("extracted", l[i]))
sim.render = True
sim.start()
while not sim.ended:
    sim.update()

print("The rank are as follow:")
for i in range(len(sim.done)):
    print(
        f"- {sim.done[i].rank:2}. {sim.done[i].name} in {simulation.time_convert_to_str(sim.done[i].time)}"
    )

# sim.write()

# ffmpeg command:
# ffmpeg -i imgs/%5d.png video.mp4
