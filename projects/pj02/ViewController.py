"""The ViewController drives the visualization of the simulation.""" 

import numpy as np
from turtle import Turtle, Screen, done
from projects.pj02.model import Cell, Model, Point
from projects.pj02 import constants
from typing import Any
from time import time_ns
import time

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
        self.collected_rewards = []

    def start_simulation(self) -> None:
        """Call the first tick of the simulation and begin turtle gfx."""
        startTime = time.time()
        self.tick()
        done()
        print("time")
        print(time.time() - startTime)

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

    def fill_square(self,x_start,y_start,c):
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

    def fill_grid(self, r_cmap) -> None:

        def draw_policy(x_start,y_start,unraveled_index):
            action_index = self.model.policies[unraveled_index] - 1
            self.pen.penup()
            self.pen.goto(x_start,y_start)
            self.pen.pendown()
            self.pen.dot(constants.CELL_RADIUS/16)
            self.pen.goto(
                x_start+self.model.actions[action_index][1]*constants.CELL_RADIUS/4,
                y_start-self.model.actions[action_index][0]*constants.CELL_RADIUS/4
            )
        self.screen.colormode(255)
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        for c in range(0,constants.NUM_COLS):
            for r in range(0,constants.NUM_ROWS):
                color = r_cmap[r,c]
                delta_x = constants.BOUNDS_WIDTH / constants.NUM_COLS * c
                delta_y = constants.BOUNDS_HEIGHT / constants.NUM_ROWS * r
                self.fill_square(upper_left.x+delta_x,upper_left.y-delta_y,color)
                draw_policy(
                    upper_left.x+delta_x+constants.CELL_RADIUS/2,
                    upper_left.y-delta_y-constants.CELL_RADIUS/2, 
                    np.ravel_multi_index((r,c),
                    (constants.NUM_ROWS,constants.NUM_COLS))
                )

    def draw_los(self, cell_x, cell_y, depth, origin_cell, is_adversary, cmap):
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        origin = self.model.find_grid_pos(upper_left,origin_cell,True)

        def in_bounds(x, y) -> bool:
            if x <= constants.MIN_X or x >= constants.MAX_X: return False
            elif y <= constants.MIN_Y or y >= constants.MAX_Y: return False
            else: return True

        def calculate_penalty(adjacent):
            l2_dist = (abs(adjacent[0]-origin[0])**2 + abs(adjacent[1]-origin[1])**2)**1/2
            return l2_dist

        raw_coords = set()
        adjacency_set = set()

        def draw_line(rad):
            self.pen.penup()
            self.pen.goto(cell_x,cell_y)
            self.pen.pendown()
            for d1 in list(np.linspace(depth,0,17)):
                x_new = cell_x + np.cos(rad) * constants.CELL_RADIUS * d1
                y_new = cell_y + np.sin(rad) * constants.CELL_RADIUS * d1
                grid_pos = self.model.find_grid_pos(upper_left,Cell(Point(x_new,y_new),Point(0,0)),True)
                if not in_bounds(x_new, y_new): continue
                adjacency_set.add(tuple((grid_pos,1/(calculate_penalty(grid_pos)+0.5))))
                raw_coords.add(grid_pos)
                self.pen.goto(x_new, y_new)
        
        for coeff in self.model.sensor_angles:
            draw_line(coeff * 2.0 * np.pi)
        max_val = sorted(adjacency_set,key=lambda x:x[1])[-1][1]
        norm_penalties = set([tuple((grid_pos[0],grid_pos[1]/max_val)) for grid_pos in adjacency_set])
        for grid_pos in norm_penalties:
            if grid_pos[0] == origin: continue
            x_sq = constants.MIN_X + grid_pos[0][1] * constants.CELL_RADIUS 
            y_sq = constants.MAX_Y - grid_pos[0][0] * constants.CELL_RADIUS
            val = int(grid_pos[1]*255)
            if is_adversary:
                self.fill_square(x_sq,y_sq,tuple((val,0,0)))
            else:
                self.fill_square(x_sq,y_sq,tuple((0,val,0)))
        if is_adversary:
            return (
                    self.model.find_grid_pos(
                        upper_left,
                        Cell(Point(cell_x,cell_y),
                        Point(0,0)),
                        True),
                    norm_penalties, 
                    origin
            )
        else: 
            return (raw_coords, norm_penalties)

    def tick(self) -> None:
        """Update the model state and redraw visualization."""
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        max_val = max(abs(np.min(self.model.r)),np.max(self.model.r))

        reward_cmap = np.asarray([np.asarray([tuple((int(-self.model.r[m,n]/max_val*127+128),0,0)) \
            if self.model.r[m,n] < 0 else tuple((0,int(self.model.r[m,n]/max_val*127+128),0)) \
            for n in range(0,constants.NUM_COLS)]) for m in range(0,constants.NUM_ROWS)])

        start_time = time_ns() // NS_TO_MS
        self.pen.color('black')
        self.pen.width(1)
        self.model.tick()
        self.pen.clear()
        self.initialize_grid()
        self.fill_grid(reward_cmap)
        adv_coords = []
        adv_masks = {}
        # ADVERSARY UPDATES
        for cell in self.model.population[1:]:
            self.pen.penup()
            #self.model.follow_offline_policy(cell)
            self.pen.goto(cell.location.x, cell.location.y)
            self.pen.pendown()
            self.pen.color(cell.color())
            self.pen.color('black')
            self.pen.dot(constants.CELL_RADIUS/2)
            obj = self.draw_los(
                cell.location.x,
                cell.location.y,depth=2,
                origin_cell=cell,
                is_adversary=True,
                cmap=reward_cmap
            )
            adv_coords.append(obj[0])
            adv_masks[obj[2]] = obj[1]
        # MAIN AGENT UPDATE
        for cell in self.model.population[:1]:
            self.pen.color('white')
            self.pen.pensize(2)
            sensor_obj = self.draw_los(
                cell.location.x,
                cell.location.y,
                depth=3, 
                origin_cell=cell,
                is_adversary=False,
                cmap=reward_cmap
            )
            intersections = self.model.intersect_los(sensor_obj[0],adv_coords,adv_masks)
            if len(intersections) == 0:
                self.model.follow_offline_policy(cell,is_random=False)
            else:
                self.model.follow_online_policy(cell, intersections)
            self.pen.penup()
            self.pen.goto(cell.location.x, cell.location.y)
            self.pen.pendown()
            self.pen.dot(constants.CELL_RADIUS/2)
            grid_pos = self.model.find_grid_pos(upper_left,cell,True)
            self.collected_rewards.append(self.model.r[grid_pos])
        self.screen.update()
        # CHECK FOR END STATE
        game_state = self.model.is_complete(self.model.population[0])
        if game_state != 'continue':
            if game_state == 'loss':
                self.collected_rewards.append(constants.LOSS_REWARD)
            print(self.collected_rewards)
            with open('./res/collected_rewards_offline_only.csv', 'a') as f:
                f.write(str(self.collected_rewards)+'\n')
            return
        else:
            end_time = time_ns() // NS_TO_MS
            next_tick = 30 - (end_time - start_time)
            if next_tick < 0:
                next_tick = 0
            self.screen.ontimer(self.tick, next_tick)
