#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simulation
import athlete

def sum(file: str) -> tuple[dict[str, int], dict[str, int]]:
    points_sim: dict[str, int] = {}
    points_exp: dict[str, int] = {}

    with open("data.csv") as f:
        lines = f.read().split("\n")[:-1]

    for l in lines:
        name, sp, rp = l.split(", ")
        if name in points_sim:
            points_sim[name] += int(sp)
        else:
            points_sim[name] = int(sp)
        if name in points_exp:
            points_exp[name] += int(rp)
        else:
            points_exp[name] = int(rp)

    points_real = {k: v for k, v in sorted(points_exp.items(), key=lambda item: item[1], reverse=True)}
    athletes = list(points_real.keys())
    ranks = {}
    for i in range(len(athletes)):
        ranks[athletes[i]] = i + 1

    points_sorted = {k: v for k, v in sorted(points_sim.items(), key=lambda item: item[1], reverse=True)}
    i = 1
    sim_ranks = {}
    for a in points_sorted:
        sim_ranks[a] = i
        i += 1
    return ranks, sim_ranks

def read(file: str, file_sum: str) -> tuple[dict[str, int], dict[str, int]]:
    trash, sim_ranks = sum(file_sum)
    complete = {}
    with open(file) as f:
        lines = f.read().split("\n")[:-1]
    for l in lines:
        name, rank = l.split(", ")
        complete[name] = int(rank)

    return complete, sim_ranks

# ranks, ranks_sim = read("data_2.csv", "data.csv")
ranks, ranks_sim = sum("data.csv")
s = simulation.SlipstreamSim(0)

for name in ranks_sim:
    if name not in ranks:
        continue
    at = athlete.Athlete(name, 0, {"jump_rank": "0", "rank": str(ranks[name])})
    at.rank = ranks_sim[name]
    s.done.append(at)

s.ended = True
s.num_athlete = len(s.done)

s.correctness()
s.compare_positions()
