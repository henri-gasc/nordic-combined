#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import utils

l = os.listdir("extracted")
race = utils.select(l)
name = input("Name: ")

os.chdir(f"extracted/{l[race]}")
path = f"../Season 2024 2025/{name} S24_25_10.0.csv"

athletes = []
with open("last.csv") as f:
    lines = f.read().strip().split("\n")[1:]
    for i in lines:
        athletes.append(i.split(",")[0])

races = os.listdir(".")

f = open(path, "a")
f.write(
    "name,nationality,team,birthdate,rank,bib,jump_points,jump_rank,jump_time_diff,cross_time,cross_rank,time_behind\n"
)

for a in athletes:
    jump_time_diff = 0
    cross_time = 0
    n = 0
    for r in races:
        if (r == "last.csv") or (r[:2] == "00"):
            continue
        year, month, day = utils.extract_date(r)

        yes = False
        yes = 2020 <= year < 2024
        if not yes:
            yes = month < 9
        if yes:
            file = open(r)
            data = file.read()
            file.close()
            start = data.find(a)
            if start == -1:
                continue
            end = data[start:].find("\n") + start
            line = data[start:end].split(",")
            jump_time_diff += utils.time_convert_to_float(line[8])
            cross_time += utils.time_convert_to_float(line[9])
            n += 1
    if n == 0:
        continue
    f.write(
        f"{a},0,0,0,0,0,0,0,{utils.time_convert_to_str(jump_time_diff/n)},{utils.time_convert_to_str(cross_time/n)},0,0\n"
    )

f.close()
os.remove("last.csv")
