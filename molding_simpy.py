# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 15:12:06 2022

@author: Ryan.Larson
"""

import simpy
import random
import statistics


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
        for part in self.order_list:
            print("{} {}".format(part.color, part.size))
        
if __name__ == '__main__':
    order = Order(5)
    order.enumerate_order()