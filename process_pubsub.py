# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:59:17 2021

@author: Ryan.Larson
"""

from pubsub import pub
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

def listener1(arg1):
    print('Listener received time: ', arg1)

pub.subscribe(listener1, 'SourceTime')

# time = str(dt.datetime.now())

# pub.sendMessage('rootTopic', arg1=time)
#
class Source():
    """Publishes message to Source topic at time intervals specified by
    exponential distribution"""

    def __init__(self,gscale,tmax):
        self.gscale = gscale
        self.tmax = tmax        # integer seconds
        self.tinterval = 0.0
        self.generator_iterator = self.source_generator()

    def __next__(self):
        return next(self.generator_iterator)

    def source_generator(self):
        while True:
            # pub.sendMessage('SourceTime',arg1=self.t)
            g_int = np.random.exponential(self.gscale)
            sec = int(g_int)
            millisec = int((g_int - int(g_int))*1000.0)
            microsec = int(((g_int - int(g_int))*1000.0 - int((g_int - int(g_int))*1000.0))*1000.0)
            self.tinterval = dt.timedelta(seconds = sec, milliseconds = millisec, microseconds=microsec)
            yield self.tinterval

    def initiate_source(self):
        start = dt.datetime.now()
        tfinal = start + dt.timedelta(seconds = self.tmax)
        next(self)
        tnext = start + self.tinterval
        while dt.datetime.now() < tfinal:
            if dt.datetime.now() > tnext:
                pub.sendMessage("source_changing", quantity=1)
                next(self)
                tnext = dt.datetime.now() + self.tinterval
                print('Message sent at: ', dt.datetime.now())


def listener1(quantity):
    print("Quantity increased by 1 at: ",dt.datetime.now())



class Queue():
    """Subscribes to SourceTime messages and increments queue value at those times."""

    def __init__(self,source_topic,queue_topic,processor_topic):
        self.queueval = 0
        self.q_quan = []
        self.q_times = []
        self.queue_topic = queue_topic
        pub.subscribe(self.update_queue,source_topic)
        pub.subscribe(self.update_queue,processor_topic)

    def update_queue(self,quantity):
        if quantity >= 0:
            self.queueval += quantity
            if self.queueval > 0:
                pub.sendMessage(self.queue_topic, queue_good=True)
            self.q_quan.append(self.queueval)
            self.q_times.append(dt.datetime.now())
        else:
            self.queueval -= quantity
            if self.queueval <= 0:
                pub.sendMessage(self.queue_topic, queue_good=False)
            self.q_quan.append(self.queueval)
            self.q_times.append(dt.datetime.now())

class Processor():
    """Subscribes to Queue messages to check if the queue quantity is a positive
    integer. Sends messages to processor_changing topic that decrement the
    quantity in the queue upstream."""

    def __init__(self,pscale,queue_topic,processor_receive_topic,processor_out_topic):
        self.processing = False
        self.pscale = pscale
        self.tinterval = 0.0
        self.generator_iterator = self.processor_generator()
        self.output_times = []
        pub.subscribe(self.process,queue_topic)
        self.processor_receive_topic = processor_receive_topic
        self.processor_out_topic = processor_out_topic

    def __next__(self):
        return next(self.generator_iterator)

    def processor_generator(self):
        while True:
            p_int = np.random.exponential(self.pscale)
            sec = int(p_int)
            millisec = int((p_int - int(p_int))*1000.0)
            microsec = int(((p_int - int(p_int))*1000.0 - int((p_int - int(p_int))*1000.0))*1000.0)
            self.tinterval = dt.timedelta(seconds = sec, milliseconds = millisec, microseconds=microsec)
            yield self.tinterval

    def process(self,queue_topic):
        # Check if the queue is good. If queue_good=True, and self.processing=False,
        # send a message to the queue to decrement by 1 and generate a process
        # time. Until the processing time is complete, set self.processing=True,
        # which should prevent the processor from accepting work from the queue
        if queue_good is True:
            if self.processing is False:
                self.processing = True
                pub.sendMessage(self.processor_receive_topic, quantity=-1)
                next(self)
                start = dt.datetime.now()
                tdone = start + self.tinterval
                while dt.datetime.now() < tdone:
                    pass

                self.output_times.append(dt.datetime.now())
                pub.sendMessage(self.processor_out_topic, quantity=1)
                self.processing = False



# source = Source(1.2,1000)
# queue = Queue('source_changing')
#
# plt.plot(queue.q_times,queue.queue)
# plt.show()



# while True:
#     # time = str(dt.datetime.now())
#     # pub.sendMessage('rootTopic', arg1=time)
#
