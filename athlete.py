#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from typing import override


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

    def reset(self) -> None:
        """Reset a boost"""
        self.activate_start = -1
        self.start_boost = -1


class Athlete:
    """Store information about a athlete"""

    def __init__(self, name: str, data: dict[str, str], random: bool = False) -> None:
        self.name = name
        self.data = data
        self.rank = -1
        self.starting_place = int(self.get("jump_rank"))
        self.time = 0.0
        self.distance = 0.0
        self.avg_speed = 0.0
        self.boost = Boost()
        self.random = random
        self.total_time = 0.0
        self.total_distance = 0.0
        r = self.get("rank")
        if (type(r) == str) and (r[:3] == "PF "):
            r = r[3:]
        self.expected_rank = int(r)

    @override
    def __str__(self) -> str:
        return f"{self.name} ({self.rank})"
        # return f"{self.name}: at {self.distance}m / {self.time}s with {self.avg_speed}m/s"

    def get(self, name: str) -> str:
        """Query a specific column"""
        return self.data[name]

    def update(self, dt: float, speed: float | None = None) -> None:
        """Update the time and distance made by the athlete"""
        self.time += dt
        s = speed
        if s is None:
            s = self.avg_speed
            if self.random:
                # Add some random to the speed of the athlete
                s *= 1 + (random.random() - 0.5) / 10
        if self.boost.is_active(self.time):
            s *= 1.5
        self.distance += s * dt

    def overtake(self, other: object) -> None:
        """Exchange the rank of two athlete if other is ahead of self"""
        if type(other) == Athlete:
            tmp = self.rank
            self.rank = other.rank
            other.rank = tmp
        else:
            raise TypeError(f"'{other}' is not an instance of Athlete")

    def start_time(self) -> float:
        return time_convert_to_float(self.get("jump_time_diff"))
