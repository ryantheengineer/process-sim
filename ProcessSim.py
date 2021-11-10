# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 09:36:54 2021

@author: Ryan.Larson

A new implementation of source_sim.py that runs off incremental time generated
by the Timer class, with class objects that can be built together into a
network and simulated within a simulation class.
"""

import numpy as np
import matplotlib.pyplot as plt
# import pandas as pd

class Timer():
    """
    Incrementally generate one time step until max value is reached.
    """
    
    def __init__(self,tmax,step):
        self.t = 0.0
        self.tmax = tmax
        self.tstep = step
        self.generator_iterator = self.tstep_generator()

    def __next__(self):
        return next(self.generator_iterator)

    def tstep_generator(self):
        while self.t <= self.tmax:
            yield self.t
            self.t += self.tstep


class Source():
    """
    Generate the times at which an item comes into a queue.
    """
    
    def __init__(self,tmax,gscale):
        self.tmax = tmax
        self.gscale = gscale
        self.t = 0.0
        self.generator_iterator = self.source_generator()
        
    def __next__(self):
        return next(self.generator_iterator)
    
    def source_generator(self):
        while self.t <= self.tmax:
            yield self.t
            g_interval = np.random.exponential(self.gscale)
            self.t += g_interval
        

class Queue():
    """
    Hold the current number of items in a queue based on the times the Source
    or Processors upstream generate items.
    """
    
    def __init__(self):
        # self.Tqueue = 0     # Queue at timer step
        self.queueval = 0      # General queue holding value
        self.q_times = []
        self.q_quan = []
        # self.p_times = []
        # self.p_quan = []
        self.T = 0.0       # initial timer time
        self.ST = 0.0      # initial source time (might be an array later)
        
    def update_queue(self, source, processor):
        """
        Increment the queue quantity and queue times based on source inputs
        and processor subtraction. Calculate the queue value at the timer
        step increments as well as at the queue times, which will be all exact
        times when a source adds an item or a processor takes away an item.
        """
        
        S_time = source.t
        P_time = processor.t
        
        # Update queue quantity
        if  S_time < P_time:
            self.q_times.append(S_time)
            self.queueval += 1
            # return False
        else:
            if self.queueval > 0:
                self.q_times.append(P_time) # FIX: Somewhere in here, there are some missing times (in the end the time vector is a fair bit shorter than the queue quantity vector)
                self.queueval -= 1
                # return False
            else:
                P_time = S_time
                self.q_times.append(P_time)
                # return P_time
                
                
        self.q_quan.append(self.queueval)


class Processor():
    """
    Generate the times at which a processor will take away an item from a
    queue. Includes ability of Queue object to modify processor times if there
    are no items to process in the Queue.
    """
    
    def __init__(self,pscale):
        self.pscale = pscale
        self.t = 0.0
        self.generator_iterator = self.processor_generator()
        
    def __next__(self):
        return next(self.generator_iterator)
    
    def send(self, value):
        self.t = value
    
    def processor_generator(self):
        while True:
            p_interval = np.random.exponential(self.pscale)
            self.t += p_interval
            yield self.t
    

class Simulation():
    """
    Take information on Sources, Queues, Processors, and Operators, and
    run a simulation of the production over time. Plots can be generated and
    the simulation can be optimized.
    """
    
    def __init__(self,source,queue,processor):
        self.source = source
        self.queue = queue
        self.processor = processor
        
    def simulate(self):
        """
        Run the simulation.
        """
        
        while self.source.t <= self.source.tmax:
            try:
                if self.source.t < self.processor.t:
                    next(self.source)
                else:
                    next(self.processor)
                self.queue.update_queue(self.source,self.processor)
            except StopIteration:
                pass
                
        print('Simulation COMPLETE')
                
        plt.figure()
        plt.plot(self.queue.q_times,self.queue.q_quan)
        plt.xlabel('Time')
        plt.ylabel('Queue')
        
        
        
        
        
# Use a try except StopIteration to catch the end of the Timer object within
# the simulation