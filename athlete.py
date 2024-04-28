#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
        self.distance += s * dt

    def overtake(self, other: object) -> None:
        """Exchange the rank of two athlete if other is ahead of self"""
        if type(other) == Athlete:
            tmp = self.rank
            self.rank = other.rank
            other.rank = tmp
        else:
            raise TypeError(f"'{other}' is not an instance of Athlete")
