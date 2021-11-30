# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:59:17 2021

@author: Ryan.Larson
"""

from pubsub import pub
import numpy as np
import matplotlib.pyplot as plt
# import datetime as dt
import time

# def listener1(quantity):
#     print("Quantity increased by 1 at: ",dt.datetime.now())


class Source():
    """Publishes message to Source topic at time intervals specified by
    exponential distribution"""

    def __init__(self,gscale,tmax):
        self.gscale = gscale
        self.tmax = float(tmax)        # integer seconds
        self.tinterval = 0.0
        self.generator_iterator = self.source_generator()

    def __next__(self):
        return next(self.generator_iterator)

    def source_generator(self):
        while True:
            self.tinterval = np.random.exponential(self.gscale)
            yield self.tinterval

    def initiate_source(self):
        start = time.time()
        tfinal = start + self.tmax
        next(self)
        tnext = start + self.tinterval
        while time.time() < tfinal:
            if time.time() > tnext:
                pub.sendMessage("source_changing", quantity=1)
                next(self)
                tnext = time.time() + self.tinterval
                print("Message sent at: ", time.time()-start)




class Queue():
    """Subscribes to SourceTime messages and increments queue value at those times."""

    def __init__(self,source_topic,queue_topic,processor_receive_topic):
        self.queueval = 0
        self.q_quan = []
        self.q_times = []
        self.queue_topic = queue_topic
        self.processor_receive_topic = processor_receive_topic
        pub.subscribe(self.update_queue,source_topic)
        pub.subscribe(self.update_queue,processor_receive_topic)

    def update_queue(self,quantity):
        if quantity >= 0:
            print("Add to queue")
            self.queueval += quantity
            if self.queueval > 0:
                pub.sendMessage(self.queue_topic, q_pos=True)
            self.q_quan.append(self.queueval)
            self.q_times.append(time.time())
        else:
            print("Remove from queue")
            self.queueval += quantity
            if self.queueval <= 0:
                pub.sendMessage(self.queue_topic, q_pos=False)
                print("Queue is zero or less")
            self.q_quan.append(self.queueval)
            self.q_times.append(time.time())

class Processor():
    """Subscribes to Queue messages to check if the queue quantity is a positive
    integer. Sends messages to processor_changing topic that decrement the
    quantity in the queue upstream."""

    def __init__(self,pscale,Queue_object,processor_out_topic):
        self.processing = False
        self.pscale = pscale
        self.Queue_object = Queue_object
        self.tinterval = 0.0
        self.generator_iterator = self.processor_generator()
        self.output_times = []
        pub.subscribe(self.process,self.Queue_object.queue_topic)
        self.processor_receive_topic = self.Queue_object.processor_receive_topic
        self.processor_out_topic = processor_out_topic

    def __next__(self):
        return next(self.generator_iterator)

    def processor_generator(self):
        while True:
            self.tinterval = np.random.exponential(self.pscale)
            yield self.tinterval

    def process(self,q_pos):
        # Check if the queue is good. If q_pos=True, and self.processing=False,
        # send a message to the queue to decrement by 1 and generate a process
        # time. Until the processing time is complete, set self.processing=True,
        # which should prevent the processor from accepting work from the queue
        if q_pos is True:
            if self.processing is False:
                self.processing = True
                pub.sendMessage(self.processor_receive_topic, quantity=-1)
                print("Processor received from queue")
                next(self)
                start = time.time()
                tdone = start + self.tinterval
                # while time.time() < tdone: # This is especially blocking code
                #     pass
                #
                # self.output_times.append(time.time())
                # pub.sendMessage(self.processor_out_topic, quantity=1)
                # self.processing = False
                # print("Processor finished")
            if self.processing is True:
                if time.time() >= tdone:
                    self.output_times.append(tdone)
                pub.sendMessage(self.processor_out_topic, quantity=1)
                self.processing = False
                print("Processor finished")


if __name__ == '__main__':
    source = Source(0.5,20)
    queue1 = Queue("source_changing","queue_state","processor_receiving")
    processor1 = Processor(2.0,queue1,"processor_finished")

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
