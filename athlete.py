#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from typing import override

import utils


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
    boost = utils.Boost()
    energy = 100.0
    locked = False  # Control the ability to get the boost
    in_slipstream = False

    # Plot energy expenditure
    # For some reason, all athletes share the same 'energies' list
    energies: dict[str, list[float]] = {}
    speeds: dict[str, list[float]] = {}
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
            # f"{self.name}: at {self.distance}m / {self.time}s with {self.avg_speed}m/s"
            f"{self.name} ({self.expected_rank} -> {self.rank})"
        )

    def get(self, name: str) -> str:
        """Query a specific column"""
        return self.data[name]

    def update(self, dt: float, speed: float | None = None) -> None:
        """Update the time and distance made by the athlete"""
        s = speed

        # If we did not get a speed, we compute it
        if s is None:
            p: float
            x = self.energy
            # Energy level
            if 83 <= x:
                # If enough energy, go faster than your average speed
                p = 125
            elif 55 <= x:
                p = 0.9 * x + 50
            else:
                p = 1.3 * x + 28
            s = p / 100 * self.avg_speed
            # s = self.avg_speed

        m = 1.0
        if self.random and (speed is None):
            # Add some random to the speed of the athlete
            m = 1 + (random.random() - 0.5) / 5
        s *= m

        # If in slipstream, recover some energy
        if self.boost.is_charging(self.time):  # and (round(self.time, 0) == self.time):
            self.energy += 0.1 * self.dt

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

        ds = self.avg_speed - s
        mult = 1.0
        if ds < 0.0:  # Lose energy more quickly than regenerate it
            mult = 2.47 # Got this number after running a race with a single athlete

        # If ds > 0, regenerate energy, if < 0, lose some
        re = mult * dt * ds / 10
        self.energy = max(min(self.energy + re, 100), 0)

        self.distance += s * dt
        self.time = round(self.time + dt, 3)
        self.energy = round(self.energy, 6)

        self.s += s
        # if round(self.time, 0) == self.time:
        # Record energy level every 30 seconds
        if self.name in self.speeds:
            self.speeds[self.name].append(self.s)
        else:
            self.speeds[self.name] = [self.s]
        self.s = 0

        if self.name in self.energies:
            self.energies[self.name].append(self.energy)
        else:
            self.energies[self.name] = [self.energy]

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
        return utils.time_convert_to_float(self.get("jump_time_diff"))
