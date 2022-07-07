# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 15:12:06 2022

@author: Ryan.Larson
"""

import simpy
import random
# import statistics
import numpy as np

orders = []
order_completion_times = []

def positive_done_in(mu, sigma):
    done_in = -1
    while done_in < 0:
        done_in = np.around(random.normalvariate(mu, sigma),1)
    return done_in

# A part is an individual product that must be produced
class Part():
    def __init__(self, order_num):
        color_options = ["Tan", "Gray"]
        size_options = [36, 48, 60, 72, 84, 96, 102]
        dice_rolls = [4, 5, 6, 7, 8, 9, 10]
        dsum = 0
        while dsum < 4 or dsum > 10:
            d1 = random.randint(1,6)
            d2 = random.randint(1,6)
            dsum = d1 + d2
        size_idx = dice_rolls.index(dsum)
        self.color = random.choice(color_options)
        self.size = size_options[size_idx]
        self.order_num = order_num
        
# # An order is a list of parts
# class Order():
#     def __init__(self, size):
#         self.size = size
#         self.order_list = [Part() for i in range(self.size)]
        
#     def enumerate_order(self):
#         # print("\nOrder received:")
#         for part in self.order_list:
#             print("{} {}".format(part.color, part.size))

# # # Generate random new orders at random intervals
# # def order_arrival(env):
# #     while True:
# #         order_time = random.normalvariate(10.0, 2.0)
# #         yield env.timeout(order_time)
# #         size = random.randint(2,10)
# #         order = Order(size)
# #         print("\nOrder received at {}".format(env.now))
# #         order.enumerate_order()
# #         orders.append(order)

    
class Plant(object):
    def __init__(self, env, num_operators, num_floats, num_molds):
        self.env = env
        self.op_mold = simpy.PreemptiveResource(env, num_operators)
        self.op_float = simpy.PreemptiveResource(env, num_floats)
        # self.mold_colors = ["Brown", "Pink", "Purple", "Orange", "Red", "Green"]
        
        self.molds = simpy.Resource(env, num_molds)
        
        self.kitting = Kitting(env, self.op_float)
        
        self.finishing = Finishing(env, self.op_float)
        
        self.mold_brown = Mold(env, self.op_mold, "BROWN")
        self.mold_pink = Mold(env, self.op_mold, "PINK")
        self.mold_purple = Mold(env, self.op_mold, "PURPLE")
        self.mold_orange = Mold(env, self.op_mold, "ORANGE")
        self.mold_red = Mold(env, self.op_mold, "RED")
        self.mold_green = Mold(env, self.op_mold, "GREEN")
        
        # self.mold_area = MoldArea(env, self.op_mold, self.mold_colors)
        
        # env.process(self.kitting.working(self.op_float))
        

class Kitting(object):
    def __init__(self, env, floats):
        self.env = env
        self.op_float = floats
        
    def make_kit(self, part, op_float):
        done_in = positive_done_in(5.0, 1.0)
        # done_in = np.around(random.normalvariate(5.0, 1.0),1)
        yield self.env.timeout(done_in)
        print("Kitting completed in {} at {}".format(done_in, np.around(env.now),1))
                
                
class Mold(object):
    def __init__(self, env, mold_operators, color):
        self.env = env
        self.op_mold = mold_operators
        self.color = color
        
    def layup(self, part, op_mold):
        done_in = positive_done_in(15.0, 3.0)
        # done_in = np.around(random.normalvariate(15.0, 3.0),1)
        yield self.env.timeout(done_in)
        print("{}:\tLayup completed in {} at {}".format(self.color, done_in, np.around(env.now,1)))
        
    def close_mold(self, part, op_mold):
        done_in = positive_done_in(10.0, 2.0)
        # done_in = np.around(random.normalvariate(10.0, 2.0),1)
        yield self.env.timeout(done_in)
        print("{}:\tClose and pull vacuum completed in {} at {}".format(self.color, done_in, np.around(env.now,1)))
        
    def shoot_part(self, part, op_mold):
        done_in = positive_done_in(15.0, 5.0)
        # done_in = np.around(random.normalvariate(15.0, 5.0),1)
        yield self.env.timeout(done_in)
        print("{}:\tShoot part completed in {} at {}".format(self.color, done_in, np.around(env.now,1)))
        
    # Dave's suggestion: Secondary process that doesn't require any
    # resources that immediately follows a process that does require an
    # operator resource. This would simulate tasks like shooting a part that 
    # don't require the operator to be fully engaged in the process for the
    # duration of the process
    def part_curing(self, part):
        # done_in = np.around(random.normalvariate())
        done_in = positive_done_in(15.0, 5.0)
        yield self.env.timeout(done_in)
        print("{}:\tPart curing completed in {} at {}".format(self.color, done_in, np.around(env.now,1)))
        
        
class Finishing(object):
    def __init__(self, env, floats):
        self.env = env
        self.op_float = floats
    
    def trim_part(self, part, op_float):
        done_in = positive_done_in(5.0, 1.0)
        yield self.env.timeout(done_in)
        print("Part trimmed in {} at {}".format(done_in, np.around(env.now, 1)))
        
    def apply_tint(self, part, op_float):
        done_in = positive_done_in(3.0, 0.5)
        yield self.env.timeout(done_in)
        print("Tint applied in {} at {}".format(done_in, np.around(env.now, 1)))


def process_part(env, part, plant):
    if plant.op_mold.capacity > 6:
        moldnum = part.order_num % plant.molds.capacity
    else:
        limiting_capacity = np.min([plant.molds.capacity, plant.op_mold.capacity])
        moldnum = part.order_num % limiting_capacity
    # print(moldnum)
    
    if moldnum == 0:
        mold = plant.mold_brown
    elif moldnum == 1:
        mold = plant.mold_pink
    elif moldnum == 2:
        mold = plant.mold_purple
    elif moldnum == 3:
        mold = plant.mold_orange
    elif moldnum == 4:
        mold = plant.mold_red
    elif moldnum == 5:
        mold = plant.mold_green
    else:
        raise ValueError("Mold number out of scope")
    
    # Build the kit for the part
    with plant.op_float.request(priority=2) as request:
        yield request
        yield env.process(plant.kitting.make_kit(part, plant.op_float))
        
    start = env.now
    # Mold the part
    # Request a mold
    with plant.molds.request() as mold_request:
        # Request an operator
        with plant.op_mold.request(priority=2) as op_mold_request:
            yield env.all_of([op_mold_request, mold_request])
            yield env.process(mold.layup(part, plant.op_mold))
            yield env.process(mold.close_mold(part, plant.op_mold))
            yield env.process(mold.shoot_part(part, plant.op_mold))
            yield env.process(mold.part_curing(part))   # This doesn't always force curing to happen before a mold can be used for layup
            
    # Finish the part
    with plant.op_float.request(priority=2) as request:
        yield request
        yield env.process(plant.finishing.trim_part(part, plant.op_float))
        yield env.process(plant.finishing.apply_tint(part, plant.op_float))
    
    duration = env.now - start
    order_completion_times.append(duration)
        
    
# def take_lunch(env, operator):
#     done_in = np.around(random.normalvariate(15.0, 3.0),1)
#     with operator.request(priority=1) as req:
#         yield req
#         try:
#             yield env.timeout(done_in)
#         except simpy.Interrupt:
#             pass
    
    
def run_plant(env, num_operators, num_floats, num_molds):
    plant = Plant(env, num_operators, num_floats, num_molds)
    partcount = 0
    
    start_idx = partcount
    
    # Start the simulation with 10 orders in the queue
    for i in range(10):
        partcount += 1
        orders.append(Part(partcount))
    
    print("\n{} parts ordered at {}".format(10, env.now))
    
    for part in orders[start_idx:-1]:
        env.process(process_part(env, part, plant))
    
    # Start generating orders of 10 parts at random intervals
    while True:        
        # Every n_hours, create a random number of orders to be processed
        # n_parts = random.randint(10,15)
        n_parts = 10    # 10 parts per pallet
        n_hours = 2
        n_minutes = n_hours*60.0
        random_time = -1
        
        random_time = positive_done_in(n_minutes, 60.0)
            
        yield env.timeout(random_time)
        
        start_idx = partcount
        
        # add n_parts to part count
        for i in range(n_parts):
            partcount += 1
            orders.append(Part(partcount))
        
        print("\n{} parts ordered at {}".format(n_parts, env.now))
        
        for part in orders[start_idx:-1]:
            env.process(process_part(env, part, plant))
        
        
if __name__ == '__main__':
    pct_complete = []
    n_sims = 100
    num_operators = 26
    num_floats = 2
    num_molds = 6
    sim_length = 5*480
    
    for i in range(n_sims):
        orders = []
        order_completion_times = []
        env = simpy.Environment()
        env.process(run_plant(env, num_operators, num_floats, num_molds))
        env.run(until=sim_length)
        
        parts_made = len(order_completion_times)
        sim_hours, frac_hours = divmod(sim_length, 60)
        print("\n{}/{} orders completed in {} hours, {} minutes".format(parts_made, orders[-1].order_num, sim_hours, frac_hours))
        
        pct_complete.append(100*(parts_made/orders[-1].order_num))
        
    mean_pct = np.mean(pct_complete)
    stdev_pct = np.std(pct_complete)
    
    print("\n\n##########################")
    print("RESULTS OF {} SIMULATIONS".format(n_sims))
    print("##########################")
    
    print("\nMolds:\t{}".format(num_molds))
    print("Mold Operators:\t{}".format(num_operators))
    print("Floats:\t{}".format(num_floats))
    print("\nAverage % Orders Complete:\t{}".format(mean_pct))
    print("Standard Dev. % Orders Complete:\t{}".format(stdev_pct))