"""The ViewController drives the visualization of the simulation.""" 

from math import cos
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

    def fill_grid(self, r_cmap) -> None:

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

        def draw_policy(x_start,y_start,unraveled_index):
            action_index = self.model.policies[unraveled_index] - 1
            #print(action_index)
            self.pen.penup()
            self.pen.goto(x_start,y_start)
            self.pen.pendown()
            self.pen.dot(constants.CELL_RADIUS/16)
            self.pen.goto(x_start+self.model.actions[action_index][1]*constants.CELL_RADIUS/4,y_start-self.model.actions[action_index][0]*constants.CELL_RADIUS/4)
        self.screen.colormode(255)
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        for c in range(0,constants.NUM_COLS):
            for r in range(0,constants.NUM_ROWS):
                color = r_cmap[r,c]
                delta_x = constants.BOUNDS_WIDTH / constants.NUM_COLS * c
                delta_y = constants.BOUNDS_HEIGHT / constants.NUM_ROWS * r
                fill_square(upper_left.x+delta_x,upper_left.y-delta_y,color)
                draw_policy(upper_left.x+delta_x+constants.CELL_RADIUS/2,upper_left.y-delta_y-constants.CELL_RADIUS/2, np.ravel_multi_index((r,c),(constants.NUM_ROWS,constants.NUM_COLS)))

    def draw_los(self, cell_x, cell_y, depth, origin_cell) -> None:
        print("COORD: ", cell_x, cell_y)
        
        def in_bounds(x, y) -> bool:
            if x < constants.MIN_X or x > constants.MAX_X: return False
            elif y < constants.MIN_Y or y > constants.MAX_Y: return False
            else: return True

        """def detect(x, y, origin_cell) -> bool:
            for cell in self.model.population:
                if cell != origin_cell and x == cell.location.x and y == cell.location.y:
                    return True
            return False"""

        def draw_line(rad):
            #delta_x = constants.BOUNDS_WIDTH / constants.NUM_COLS
            #delta_y = constants.BOUNDS_HEIGHT / constants.NUM_ROWS
            self.pen.penup()
            self.pen.goto(cell_x,cell_y)
            self.pen.pendown()
            for d in range(depth,0,-1):
                x_new = cell_x + np.cos(rad) * constants.CELL_RADIUS * d
                y_new = cell_y + np.sin(rad) * constants.CELL_RADIUS * d
                if not in_bounds(x_new, y_new): continue
                self.pen.goto(x_new, y_new)

        for coeff in self.model.sensor_angles:
            draw_line(coeff * 2.0 * np.pi)

    def tick(self) -> None:
        reward_cmap = np.asarray([np.asarray([tuple((int(-self.model.r[m,n]/np.max(self.model.r)*127+128),0,0)) if self.model.r[m,n] < 0 else tuple((0,int(self.model.r[m,n]/np.max(self.model.r)*127+128),0)) for n in range(0,constants.NUM_COLS)]) for m in range(0,constants.NUM_ROWS)])
        #print(reward_cmap)
        #print(self.model.policies)
        #reward_cmap[self.model.start_state] = tuple((255,255,255))
        #reward_cmap[self.model.end_state] = tuple((0,0,0))
        """Update the model state and redraw visualization."""
        start_time = time_ns() // NS_TO_MS
        self.model.tick()
        self.pen.clear()
        self.initialize_grid()
        self.fill_grid(reward_cmap)
        sleep(1)
        """for cell in self.model.population:
            self.pen.penup()
            self.pen.goto(cell.location.x, cell.location.y)
            self.pen.pendown()
            self.pen.color(cell.color())
            self.pen.color('black')
            self.pen.dot(constants.CELL_RADIUS/2)
            self.draw_los(cell.location.x,cell.location.y,depth=4, origin_cell=cell)"""
        self.screen.update()
        sleep(100)
        if self.model.is_complete():
            return
        else:
            end_time = time_ns() // NS_TO_MS
            next_tick = 30 - (end_time - start_time)
            if next_tick < 0:
                next_tick = 0
            self.screen.ontimer(self.tick, next_tick)
