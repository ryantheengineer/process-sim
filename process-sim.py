# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 09:36:54 2021

@author: Ryan.Larson
"""

import numpy as np
import matplotlib.pyplot as plt

class Timer():
    # Incrementally generate one time step until max value is reached. Store
    # time steps for later plotting of results
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
    # Calculate a vector of the times that the source generates ngen items

    # For tsim, use np.linspace(0, tmax, npts)
    def __init__(self,tsim,g_scale,ngen):
        self.update_src(tsim, g_scale, ngen)

    def update_src(self,tsim,g_scale,ngen):
        self.tsim = tsim
        self.g_scale = g_scale
        self.ngen = ngen
        self.g_times = np.zeros((1,1))
        # self.gqueue = np.zeros(self.tsim.shape)
        while max(self.g_times) < max(self.tsim):
            g_interval = np.random.exponential(self.g_scale)
            gsum = 0
            gsum = self.g_times[-1] + g_interval
            self.g_times = np.append(self.g_times,[gsum])

        # for i in range(len(self.gqueue)):
        #     nqueue = 0
        #     for t in self.g_times:
        #         if t <= self.tsim[i]:
        #             nqueue += ngen

        #     self.gqueue[i] = nqueue

class Queue():
    # Queue that can handle single inputs only
    def __init__(self,tsim,g_times,ngen):
        self.tsim = tsim
        self.g_times = g_times
        self.ngen = ngen
        self.queue = np.zeros(self.tsim.shape)

        for i in range(len(self.queue)):
            nqueue = 0
            for t in self.g_times:
                if t <= self.tsim[i]:
                    nqueue += self.ngen

            self.queue[i] = nqueue


# class Processor():
#     # Calculate a vector of the number of items leaving an individual processor
#     # at the simulation time steps
#     def __init__(self,p_scale,queue):
