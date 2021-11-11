"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from typing import List
from random import random
from projects.pj02 import constants
from math import sin, cos, pi
import numpy as np


__author__ = ""  # TODO


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = 0

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    # Part 1) Define a method named `tick` with no parameters.
    # Its purpose is to reassign the object's location attribute
    # the result of adding the self object's location with its
    # direction. Hint: Look at the add method.
    def tick(self):
        self.location = self.location.add(self.direction)    

    def color(self) -> str:
        """Return the color representation of a cell."""
        return "black"


class Model:
    """The state of the simulation."""

    population: List[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float):
        """Initialize the cells with random locations and directions."""
        self.population = []
        for _ in range(0, cells):
            start_loc = self.random_location()
            start_dir = self.random_direction(speed)
            self.population.append(Cell(start_loc, start_dir))
    
    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)

    def random_location(self) -> Point:
        """Generate a random location."""
        xCoord = float(np.random.randint(constants.MIN_X,constants.MAX_X))
        yCoord = float(np.random.randint(constants.MIN_Y,constants.MAX_Y))
        return Point(xCoord, yCoord)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle = 2.0 * np.pi * np.random.random()
        dirX = np.cos(random_angle) * speed
        dirY = np.sin(random_angle) * speed
        return Point(dirX, dirY)

    def enforce_bounds(self, cell: Cell):
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X:
            cell.location.x = constants.MAX_X
            cell.direction.x *= -1
        if cell.location.x < constants.MIN_X:
            cell.location.x = constants.MIN_X
            cell.direction.x *= -1
        if cell.location.y > constants.MAX_Y:
            cell.location.y = constants.MAX_Y
            cell.direction.y *= -1    
        if cell.location.y < constants.MIN_Y:
            cell.location.y = constants.MIN_Y
            cell.direction.y *= -1 

    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        return False
