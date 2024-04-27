#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Athlete:
    """Store information about a athlete"""

    def __init__(self, name: str, avg_speed: float, data: dict[str, str]) -> None:
        self.name = name
        self.avg_speed = avg_speed
        self.rank = 0
        self.time = 0.0
        self.distance = 0.0
        self.data = data

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
        """Not used for now, exchange the rank of two athlete"""
        if type(other) != Athlete:
            raise TypeError(f"'{other}' is not an instance of Athlete")
        tmp = self.rank
        self.rank = other.rank
        other.rank = tmp
