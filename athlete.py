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

    def is_charging(self, t: float) -> bool:
        return self.activate_start != -1

    def reset(self) -> None:
        """Reset a boost"""
        self.activate_start = -1
        self.start_boost = -1


class Athlete:
    """Store information about a athlete"""

    # Values
    rank = -1
    time = 0.0
    distance = 0.0
    avg_speed = 0.0
    dt = 0.0

    # Used with season
    total_time = 0.0
    total_distance = 0.0

    # Slipstream
    boost = Boost()
    energy = 100.0
    locked = False  # Control the ability to get the boost

    # Plot energy expenditure
    energies: list[float] = []
    s = 0.0

    def __init__(
        self, name: str, dt: float, data: dict[str, str], random: bool = False
    ) -> None:
        self.name = name
        self.dt = dt
        self.data = data
        self.starting_place = int(self.get("jump_rank"))
        self.random = random
        r = self.get("rank")
        if (type(r) == str) and (r[:3] == "PF "):
            r = r[3:]
        self.expected_rank = int(r)

    @override
    def __str__(self) -> str:
        # return f"{self.name} ({self.rank})"
        return (
            f"{self.name}: at {self.distance}m / {self.time}s with {self.avg_speed}m/s"
        )

    def get(self, name: str) -> str:
        """Query a specific column"""
        return self.data[name]

    def update(self, dt: float, speed: float | None = None) -> None:
        """Update the time and distance made by the athlete"""
        s = speed

        # Record energy level every 30 seconds
        if (round(self.time, 0) == self.time) and (self.time % 60 == 0):
            if (dt == 0) or (self.s == 0):
                pass
            else:
                self.energies.append(self.s * dt / 60)
            self.s = 0
        self.s += self.energy

        # If we did not get a speed, we compute it
        if s is None:
            p: float
            # Energy level
            if 83 <= self.energy:
                # If enough energy, go faster than your average speed
                p = 125
            else:
                p = 0.9 * self.energy + 50
            s = p / 100 * self.avg_speed
            # s = self.avg_speed * self.energy / 100

        m = 1.0
        if self.random and (speed is None):
            # Add some random to the speed of the athlete
            m = 1 + (random.random() - 0.5) / 5

        # If in slipstream, recover some energy
        if self.boost.is_charging(self.time):  # and (round(self.time, 0) == self.time):
            self.energy += 0.01 * self.dt

        # Allow boost if we were locked but now we have enough energy
        if self.locked and (self.energy > 70):
            self.locked = False

        # Launch the boost
        if self.boost.is_active(self.time):
            if self.can_boost():
                s *= 1.5
            else:
                # Allow the boost to still be "in reach"
                self.boost.start_boost = self.time
                self.locked = True

        speed_before = s
        s *= m
        ds = speed_before - s
        mult = 1.0
        if ds < 0:  # Lose energy more quickly than regenerate it
            mult = 1.2

        # If ds > 0, regenerate energy, if < 0, lose some
        self.energy = max(min(self.energy + mult * dt * ds, 100), 0)

        self.distance += s * dt
        self.time = round(self.time + dt, 3)
        self.energy = round(self.energy, 6)

    def can_boost(self) -> bool:
        return (not self.locked) and (self.energy > 50)

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
