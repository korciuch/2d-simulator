"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from simulation import create_reward_matrix, load_policy, ACTIONS
from q_learning import load_Q
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

    def tick(self):
        self.location = self.location.add(self.direction)    

    def color(self) -> str:
        """Return the color representation of a cell."""
        return "black"

class Model:
    """The state of the simulation."""

    population: List[Cell]
    agent: List[Cell]
    time: int = 0
    adjacency_sets: List[set()]
    r = create_reward_matrix(create_new=False)
    Q = load_Q('q_matrix.csv')
    actions = [(1,0), (-1,0), (0,-1), (0,1)] # down - 1, up - 2, left - 3, right - 4
    angles = [0.75,0.25,0.5,0]
    policies = load_policy(src_file='sim.policy')
    sensor_angles = np.asarray(np.linspace(0,1,17))
    start_state = (constants.NUM_ROWS-1,0)
    end_state = (0,constants.NUM_COLS-1)

    def __init__(self, cells: int, speed: float):
        """Initialize the cells with random locations and directions."""
        self.population = []
        self.agent = []
        for i in range(0, cells):
            start_loc = self.random_location()
            start_dir = self.random_direction(speed)
            if i == 0:
                xCoord = constants.MIN_X + constants.CELL_RADIUS/2
                yCoord = constants.MIN_Y + constants.CELL_RADIUS/2
                self.population.append(Cell(Point(xCoord, yCoord), start_dir))
            else: self.population.append(Cell(start_loc, start_dir))
    
    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.agent:
            cell.tick()
            self.enforce_bounds(cell)
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)
            self.randomMove()
    
    def randomMove(self):
        for cell in self.population:
            num = np.random.randint(0,30)
            #change x dir
            if num == 0:
                #print("X")
                if cell.direction.x != 0:
                    cell.direction.x *= -1
                else:
                    cell.direction.x = cell.direction.y
                    cell.direction.y = 0
            #change y dir
            if num == 2:
                #print("Y")
                if cell.direction.y != 0:
                    cell.direction.y *= -1
                else:
                    cell.direction.y = cell.direction.x
                    cell.direction.x = 0

    def random_location(self) -> Point:
        """Generate a random location."""
        xCoord = np.random.choice([constants.MIN_X + constants.BOUNDS_WIDTH / constants.NUM_COLS * i + constants.CELL_RADIUS/2 for i in range(0, constants.NUM_COLS+1)])
        yCoord = np.random.choice([constants.MIN_Y + constants.BOUNDS_HEIGHT / constants.NUM_ROWS * i + constants.CELL_RADIUS/2 for i in range(0, constants.NUM_ROWS+1)])
        #print('RANDOM_LOCATION: ', (xCoord,yCoord))
        return Point(xCoord, yCoord)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle = 2.0 * np.pi * np.random.choice([0,0.25,0.5,0.75])
        dirX = np.cos(random_angle) * speed
        dirY = np.sin(random_angle) * speed
        return Point(dirX, dirY)

    def enforce_bounds(self, cell: Cell):
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x+constants.CELL_RADIUS/2 > constants.MAX_X:
            cell.location.x = constants.MAX_X-constants.CELL_RADIUS/2
            cell.direction.x *= -1
        if cell.location.x-constants.CELL_RADIUS/2 < constants.MIN_X:
            cell.location.x = constants.MIN_X+constants.CELL_RADIUS/2
            cell.direction.x *= -1
        if cell.location.y+constants.CELL_RADIUS/2 > constants.MAX_Y:
            cell.location.y = constants.MAX_Y-constants.CELL_RADIUS/2
            cell.direction.y *= -1    
        if cell.location.y-constants.CELL_RADIUS/2 < constants.MIN_Y:
            cell.location.y = constants.MIN_Y+constants.CELL_RADIUS/2
            cell.direction.y *= -1 

    def intersect_los(self,main_adj_set,adv_locations,adv_masks):
        #print('main adjacency set: ', main_adj_set)
        #print('locations of adversaries: ', adv_locations)
        #print('reward masks of adversaries: ', adv_masks)
        other_agents = set()
        output = {}
        for s in adv_locations: other_agents.add(s)
        intersection = main_adj_set.intersection(other_agents)
        for conflict in intersection:
            for cell in adv_masks[conflict]:
                if cell[0] in main_adj_set:
                    output[cell[0]] = output.get(cell[0], 0) + cell[1]
                    if output.get(cell[0]) > 1: output[cell[0]] = 1
        #print('I see: ', intersection)
        #print('los_intersections: ', output)
        return output

    def follow_offline_policy(self, cell):
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        policy_index = self.find_grid_pos(upper_left,cell,True)
        ravel_index = np.ravel_multi_index(policy_index,(constants.NUM_ROWS,constants.NUM_COLS))
        action = self.policies[ravel_index]
        angle = self.angles[action-1]*2.0*np.pi
        x_dir = np.cos(angle) * constants.CELL_SPEED
        y_dir = np.sin(angle) * constants.CELL_SPEED
        cell.direction.x = x_dir
        cell.direction.y = y_dir

    def follow_online_policy(self, cell, intersections):
        outcomes = []
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        coord = self.find_grid_pos(upper_left,cell,True)
        #ss_index = np.ravel_multi_index(coord,(constants.NUM_ROWS,constants.NUM_COLS))
        # down - 0, up - 1, left - 2, right - 3
        def lookahead(coord, cum_reward, depth, actions):
            if depth == 2: 
                outcomes.append((cum_reward,actions))
                return
            else:
                for a in range(0,len(ACTIONS)):
                    curr_state_index = np.ravel_multi_index(coord,(constants.NUM_ROWS,constants.NUM_COLS))
                    m = coord[0] + ACTIONS[a][0]
                    n = coord[1] + ACTIONS[a][1]
                    if m < 0 or n < 0: continue
                    elif m >= constants.NUM_ROWS or n >= constants.NUM_COLS: continue
                    sp = (m, n)
                    val = self.Q[curr_state_index][a]
                    if sp in intersections.keys(): 
                        val += np.iinfo(np.int64).min * intersections[sp]
                    lookahead(sp, cum_reward + val, depth+1, actions+[a])

        lookahead(coord,0,0,[])
        print(sorted(outcomes,key=lambda x:x[0],reverse=True))
        action = sorted(outcomes,key=lambda x:x[0],reverse=True)[0][1][0]
        angle = self.angles[action]*2.0*np.pi
        x_dir = np.cos(angle) * constants.CELL_SPEED
        y_dir = np.sin(angle) * constants.CELL_SPEED
        cell.direction.x = x_dir
        cell.direction.y = y_dir

    def find_grid_pos(self,upper_left,cell,is_structured):
        offset = constants.CELL_RADIUS/2 if is_structured else 0
        r = abs((upper_left.y-cell.location.y + offset)/constants.CELL_RADIUS)-1
        c = abs((upper_left.x-cell.location.x - offset)/constants.CELL_RADIUS)-1
        return (round(r),round(c))

    def is_complete(self,cell) -> bool:
        """Method to indicate when the simulation is complete."""
        upper_left = Point(constants.MIN_X,constants.MAX_Y)
        grid_pos = self.find_grid_pos(upper_left,cell,True)
        if grid_pos == constants.END_STATE: return True
        for adv in self.population[1:]:
            adv_pos = self.find_grid_pos(upper_left,adv,True)
            if grid_pos == adv_pos:
                return True
        else: return False