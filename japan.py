import os

import utils

l = os.listdir("extracted/Season 2023_2024")
path = "extracted/Season 2024 2025/00 Japan.csv"

athletes = set()
for file in l:
    with open(f"extracted/Season 2023_2024/{file}") as f:
        text = f.read().strip().split("\n")[1:]
    for line in text:
        athletes.add(line.split(",")[0])

f = open(path, "w")
f.write(
    "name,nationality,team,birthdate,rank,bib,jump_points,jump_rank,jump_time_diff,cross_time,cross_rank,time_behind\n"
)

for a in athletes:
    jump_time_diff = 0
    cross_time = 0
    n = 0
    for file in l:
        with open(f"extracted/Season 2023_2024/{file}") as file:
            data = file.read()
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
