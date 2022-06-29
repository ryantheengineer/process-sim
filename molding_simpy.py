# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 15:12:06 2022

@author: Ryan.Larson
"""

import simpy
import random
# import statistics
# import numpy as np

orders = []
cycle_times = []

# A part is an individual product that must be produced
class Part():
    def __init__(self):
        color_options = ["Tan", "Gray"]
        size_options = [36, 48, 60, 72, 84, 96, 102]
        self.color = random.choice(color_options)
        self.size = random.choice(size_options)
        
# An order is a list of parts
class Order():
    def __init__(self, size):
        self.size = size
        self.order_list = [Part() for i in range(self.size)]
        
    def enumerate_order(self):
        # print("\nOrder received:")
        for part in self.order_list:
            print("{} {}".format(part.color, part.size))

# Generate random new orders at random intervals
def order_arrival(env):
    while True:
        order_time = random.normalvariate(10.0, 2.0)
        yield env.timeout(order_time)
        size = random.randint(2,10)
        order = Order(size)
        print("\nOrder received at {}".format(env.now))
        order.enumerate_order()
        orders.append(order)

    
class Plant(object):
    def __init__(self, env, num_operators, num_floats, num_molds):
        self.env = env
        self.op_mold = simpy.PreemptiveResource(env, num_operators)
        self.op_float = simpy.PreemptiveResource(env, num_floats)
        # self.mold_colors = ["Brown", "Pink", "Purple", "Orange", "Red", "Green"]
        
        self.molds = simpy.Resource(env, num_molds)
        
        self.kitting = Kitting(env, self.op_float)
        
        self.mold = Mold(env, self.op_mold)
        
        # self.mold_area = MoldArea(env, self.op_mold, self.mold_colors)
        
        # env.process(self.kitting.working(self.op_float))
        

class Kitting(object):
    def __init__(self, env, floats):
        self.env = env
        self.op_float = floats
        
    def make_kit(self, part, op_float):
        done_in = random.normalvariate(5.0, 1.0)
        yield self.env.timeout(done_in)
        # print("Kitting completed in {} at {}".format(done_in, env.now))
                
                
class Mold(object):
    def __init__(self, env, mold_operators):
        self.env = env
        self.op_mold = mold_operators
        
    def layup(self, part, op_mold):
        done_in = random.normalvariate(15.0, 3.0)
        yield self.env.timeout(done_in)
        # print("Layup completed in {} at {}".format(done_in, env.now))
        
    def close_mold(self, part, op_mold):
        done_in = random.normalvariate(10.0, 2.0)
        yield self.env.timeout(done_in)
        # print("Close and pull vacuum completed in {} at {}".format(done_in, env.now))
        
    def shoot_part(self, part, op_mold):
        done_in = random.normalvariate(30.0, 5.0)
        yield self.env.timeout(done_in)
        # print("Shoot part completed in {} at {}".format(done_in, env.now))
        
        
# class MoldArea(object):
#     def __init__(self, env, mold_operators, mold_colors):
#         self.env = env
#         self.op_mold = mold_operators
#         self.mold_colors = mold_colors
#         self.molds = [Mold(env, self.op_mold, color) for color in self.mold_colors]
        
        
        
def process_part(env, part, plant):
    
    
    # Build the kit for the part
    with plant.op_float.request(priority=1) as request:
        yield request
        yield env.process(plant.kitting.make_kit(part, plant.op_float))
        
    start = env.now
    # Mold the part
    # Layup
    with plant.op_mold.request(priority=1) as op_mold_request:
        with plant.molds.request() as mold_request:
            yield env.all_of([op_mold_request, mold_request])
            yield env.process(plant.mold.layup(part, plant.op_mold))
    
    # Close mold and pull vacuum
    with plant.op_mold.request(priority=1) as op_mold_request:
        with plant.molds.request() as mold_request:
            yield env.all_of([op_mold_request, mold_request])
            yield env.process(plant.mold.close_mold(part, plant.op_mold))
            
    # Shoot the part
    with plant.op_mold.request(priority=1) as op_mold_request:
        with plant.molds.request() as mold_request:
            yield env.all_of([op_mold_request, mold_request])
            yield env.process(plant.mold.shoot_part(part, plant.op_mold))
    
    duration = env.now - start
    # print(start)
    # print(duration)
    # print("")
    cycle_times.append(duration)
        
        
        
def run_plant(env, num_operators, num_floats, num_molds):
    plant = Plant(env, num_operators, num_floats, num_molds)
    part = 0
    
    while True:
        yield env.timeout(50.0)
        
        part += 1
        orders.append(part)
        # print("\nPart received at {}".format(env.now))
        env.process(process_part(env, part, plant))


        
if __name__ == '__main__':
    # order = Order(5)
    # order.enumerate_order()
    env = simpy.Environment()
    # env.process(order_arrival(env))
    # plant = Plant(env, 2, 2)
    num_operators = 2
    num_floats = 2
    num_molds = 6
    env.process(run_plant(env, num_operators, num_floats, num_molds))
    env.run(until=800)
    
    # part_count = 0
    # for order in orders:
    #     part_count += order.size