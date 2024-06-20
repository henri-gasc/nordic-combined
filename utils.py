#!/usr/bin/env python
# -*- coding: utf-8 -*-


def time_convert_to_str(time: int | float) -> str:
    """Convert time (in seconds) to a string of format hh:mm:ss
    The hh: is ommitted if equal to 0"""
    out = ""
    h = time // 3600
    if h != 0:
        out = f"{int(h)}:"
        time -= h * 3600
    # We want to keep the decisecond
    return f"{out}{int(time // 60):02}:{int(time - (time//60)*60):02}"

def extract_date(filename: str) -> tuple[int, int, int]:
    parts = filename.split(" ")
    if parts[-1][0] == "S":
        date = parts[-2]
    else:
        date = parts[-1][:8]
    year = int(date[-4:])
    month = int(date[2:-4])
    day = int(date[:2])
    return (year, month, day)

def select(l: list[str]) -> int:
    if len(l) == 1:
        return 0
    for i in range(len(l)):
        print(f"[{i+1:02}] {l[i]}")
    selected = len(l) + 1
    while (-1 > selected) or (selected > len(l)):
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


def time_convert_to_float(time: str) -> float:
    """Split time at : and return the time in seconds"""
    m, s = time.split(":")
    return float(m) * 60 + float(s)


class Boost:
    """The boost class. Stores information about each athlete's boost"""

    def __init__(self) -> None:
        self.time_activation: float = 2.0
        self.time_boost: float = 5.0
        self.activate_start: float = -1.0
        self.start_boost: float = -1.0

    def change(self, t: float) -> None:
        """Change the state of the boost for this athlete"""
        if self.activate_start < 0:
            self.activate_start = t
        elif (t - self.activate_start) > self.time_activation:
            self.start_boost = t

    def is_active(self, t: float) -> bool:
        """Return if an athlete has a boost or not"""
        if self.start_boost < 0:
            return False
        return (t - self.start_boost) < self.time_boost

    def is_charging(self, t: float) -> bool:
        return self.activate_start != -1

    def reset(self) -> None:
        """Reset a boost"""
        self.activate_start = -1
        self.start_boost = -1
