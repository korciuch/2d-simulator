"""The ViewController drives the visualization of the simulation.""" 

import numpy as np
from turtle import Turtle, Screen, color, done
from projects.pj02.model import Model, Point
from projects.pj02 import constants
from typing import Any
from time import time_ns, sleep


NS_TO_MS: int = 1000000


class ViewController:
    """This class is responsible for controlling the simulation and visualizing it."""
    screen: Any
    pen: Turtle
    model: Model

    def __init__(self, model: Model):
        """Initialize the VC."""
        self.model = model
        self.screen = Screen()
        self.screen.setup(constants.VIEW_WIDTH+50, constants.VIEW_HEIGHT+50)
        self.screen.tracer(0, 0)
        self.screen.delay(0)
        self.screen.title("Cluster Funk v2")
        self.pen = Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)

    def start_simulation(self) -> None:
        """Call the first tick of the simulation and begin turtle gfx."""
        self.tick()
        done()

    def initialize_grid(self) -> None:
        # COLUMNS
        for c in range(0,constants.NUM_COLS+1):
            x_coord = constants.MIN_X + constants.BOUNDS_WIDTH / constants.NUM_COLS * c
            self.pen.penup()
            self.pen.goto(x_coord, constants.MIN_Y)
            self.pen.pendown()
            self.pen.goto(x_coord,constants.MAX_Y)
        # ROWS
        for r in range(0,constants.NUM_ROWS+1):
            y_coord = constants.MIN_Y + constants.BOUNDS_HEIGHT / constants.NUM_ROWS * r
            self.pen.penup()
            self.pen.goto(constants.MIN_X,y_coord)
            self.pen.pendown()
            self.pen.goto(constants.MAX_X,y_coord)

    def fill_grid(self) -> None:

        def fill_square(x_start,y_start,c):
            delta_x = constants.BOUNDS_HEIGHT / constants.NUM_COLS
            delta_y = constants.BOUNDS_WIDTH / constants.NUM_ROWS
            self.pen.penup()
            self.pen.goto(x_start,y_start)
            self.pen.pendown()
            self.pen.fillcolor(c)
            self.pen.begin_fill()
            self.pen.goto(x_start,y_start-delta_y)
            self.pen.goto(x_start+delta_x,y_start-delta_y)
            self.pen.goto(x_start+delta_x,y_start)
            self.pen.goto(x_start,y_start)
            self.pen.end_fill()

        self.screen.colormode(255)
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        for c in range(0,constants.NUM_COLS):
            for r in range(0,constants.NUM_ROWS):
                #c = tuple(np.random.random_integers(1,255,size=3))
                color = self.model.color_grid[r,c]
                delta_x = constants.BOUNDS_WIDTH / constants.NUM_COLS * c
                delta_y = constants.BOUNDS_HEIGHT / constants.NUM_ROWS * r
                fill_square(upper_left.x+delta_x,upper_left.y-delta_y,color)

    def tick(self) -> None:
        """Update the model state and redraw visualization."""
        start_time = time_ns() // NS_TO_MS
        self.model.tick()
        self.pen.clear()
        self.initialize_grid()
        self.fill_grid()
        #sleep(1)
        for cell in self.model.population:
            self.pen.penup()
            self.pen.goto(cell.location.x, cell.location.y)
            self.pen.pendown()
            self.pen.color(cell.color())
            self.pen.dot(constants.CELL_RADIUS-5)
        self.screen.update()

        if self.model.is_complete():
            return
        else:
            end_time = time_ns() // NS_TO_MS
            next_tick = 30 - (end_time - start_time)
            if next_tick < 0:
                next_tick = 0
            self.screen.ontimer(self.tick, next_tick)
