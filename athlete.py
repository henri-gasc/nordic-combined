#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Boost:
    """ The boost class. Stores information about each athlete's boost """
    def __init__(self) -> None:
        self.time_activation = 2
        self.time_boost = 5
        self.activate_start = -1
        self.start_boost = -1

    def change(self, t: float) -> None:
        if self.activate_start < 0:
            self.activate_start = t
        elif (t - self.activate_start) > self.time_activation:
            self.start_boost = t

    def is_active(self, t: float) -> bool:
        """ Return if an athelete has a boost or not """
        if self.start_boost < 0:
            return False
        return (t - self.start_boost) < self.time_boost

    def reset(self) -> None:
        """ Reset a boost """
        self.activate_start = -1
        self.start_boost = -1

class Athlete:
    """Store information about a athlete"""

    def __init__(self, name: str, rank: int, data: dict[str, str]) -> None:
        self.name = name
        self.data = data
        self.rank = rank
        self.starting_place = rank
        self.time = .0
        self.distance = .0
        self.avg_speed = .0
        self.boost = Boost()

    def __str__(self) -> str:
        return f"{self.name}: at {self.distance}m/{self.time}s with {self.avg_speed}m/s"

    def get(self, name: str) -> str:
        """Query a specific column"""
        return self.data[name]

    def update(self, dt: float, speed: float | None = None) -> None:
        """Update the time and distance made by the athlete"""
        self.time += dt
        s = speed
        if s is None:
            s = self.avg_speed
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
