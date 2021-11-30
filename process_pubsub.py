# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:59:17 2021

@author: Ryan.Larson
"""

from pubsub import pub
import numpy as np
import matplotlib.pyplot as plt
import time

# def listener1(quantity):
#     print("Quantity increased by 1 at: ",dt.datetime.now())


class Source():
    """Publishes message to Source topic at time intervals specified by
    exponential distribution"""

    def __init__(self,gscale,tmax):
        self.gscale = gscale
        self.tmax = tmax
        self.t = 0.0
        self.generator_iterator = self.source_generator()

    def __next__(self):
        return next(self.generator_iterator)

    def source_generator(self):
        while True:
            yield self.t
            interval = np.random.exponential(self.gscale)
            self.t += interval

    def activate_source(self):
        while self.t <= self.tmax:
            next(self)
            pub.sendMessage("source_changing", time=self.t, quantity=1)

    def reset_source(self):
        self.t = 0.0
        self.generator_iterator = self.source_generator()


class Queue():
    """Subscribes to SourceTime messages and increments queue value at those times."""

    def __init__(self,source_topic,queue_topic,processor_receive_topic):
        self.q_val = 0
        self.q_quan = []
        self.q_times = []
        self.queue_topic = queue_topic
        self.processor_receive_topic = processor_receive_topic
        pub.subscribe(self.update_queue,source_topic)
        pub.subscribe(self.update_queue,processor_receive_topic)

    def update_queue(self,time,quantity):
        self.q_times.append(time)
        if (self.q_val + quantity) >= 0:
            self.q_val += quantity
            print("1 item received at {}. Total: {}".format(time,self.q_val))
        else:
            self.q_val = 0

        self.q_quan.append(self.q_val)
        if self.q_val > 0:
            pub.sendMessage(self.queue_topic, qtime=self.q_times[-1], q_pos=True)
        else:
            pub.sendMessage(self.queue_topic, qtime=self.q_times[-1], q_pos=False)


class Processor():
    """Subscribes to Queue messages to check if the queue quantity is a positive
    integer. Sends messages to processor_changing topic that decrement the
    quantity in the queue upstream."""

    def __init__(self,pscale,Queue_object,processor_out_topic):
        self.pscale = pscale
        self.Queue_object = Queue_object
        self.processor_out_topic = processor_out_topic

        self.processing = False
        self.output_times = []
        self.t = 0.0
        next(self)
        self.p_receive = 0.0
        next(self)
        self.p_output = self.t
        self.generator_iterator = self.processor_generator()

        pub.subscribe(self.process,self.Queue_object.queue_topic)
        self.processor_receive_topic = self.Queue_object.processor_receive_topic

    def __next__(self):
        return next(self.generator_iterator)

    def send(self, value):
        self.t = value

    def processor_generator(self):
        while True:
            interval = np.random.exponential(self.pscale)
            self.t += interval
            yield self.t

    def process(self,q,q_pos):
        if q_pos is True:
            if self.processing = False:
                if self.p_receive >= qtime:
                    self.processing = True
                    pub.sendMessage(self.processor_receive_topic, time=self.p_receive, quantity=-1)
                    pub.sendMessage(self.processor_out_topic, time=self.p_output, quantity=1)
                    self.p_receive = self.p_output
                    next(self)
                    self.p_output = self.t

                    self.processing = False

                if self.p_receive < qtime:
                    self.processing = True
                    pub.sendMessage(self.processor_receive_topic, time=self.p_receive, quantity=-1)
                    pub.sendMessage(self.processor_out_topic, time=self.p_output, quantity=1)






if __name__ == '__main__':
    source = Source(0.5,20)
    queue1 = Queue("source_changing","queue_state","processor_receiving")
    # processor1 = Processor(2.0,queue1,"processor_finished")

    source.initiate_source()

    # Adjust queue times so they start from zero
    start = queue1.q_times[0]
    for i in range(len(queue1.q_times)):
        queue1.q_times[i] -= start

    plt.plot(queue1.q_times,queue1.q_quan)
    plt.title('Queue 1 Quantity over Time')
    plt.xlabel('Time')
    plt.ylabel('Quantity')
    plt.show()
