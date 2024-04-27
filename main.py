#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
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

sim = simulation.SimpleSim(1)
sim.load_csv(os.path.join("extracted", l[i]))
sim.start()
while not sim.ended:
    sim.update()

print("The rank are as follow:")
for i in range(len(sim.done)):
    print(f"- {i+1:2}. {sim.done[i].name} in {simulation.time_convert_to_str(sim.done[i].time)}")
