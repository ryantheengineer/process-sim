import numpy as np
import matplotlib.pyplot as plt

# MAIN FLAW IN THE APPROACH AS IT STANDS:
# Processors have to be able to react to whether there is something in the
# queue. If there is nothing in the queue, nothing can be processed.


# Generate a time vector
n = 100
tmax = 50.
time = np.linspace(0., tmax, n)
gen_scale = 1.0
# gen_intervals = np.random.exponential(gen_scale, n)
# gen_intervals[0] = 0.
gen_times = np.zeros((1,1))

# Calculate the times at which flow items will be generated
while max(gen_times) < tmax:
    gen_interval = np.random.exponential(gen_scale)
    gensum = 0
    gensum = gen_times[-1] + gen_interval
    gen_times = np.append(gen_times,[gensum])

# Calculate the number of flow items in the queue at the time vector times
queue = np.zeros(time.shape)
for i in range(len(queue)):
    nqueue = 0
    for t in gen_times:
        if t <= time[i]:
            nqueue += 1

    queue[i] = nqueue

# plt.figure(1)
# plt.plot(time, queue)
# plt.title('Queue vs. Time with Generators Only')
# plt.xlabel('Time')
# plt.ylabel('Queue')

# Calculate the times at which flow items will be processed
nprocessors = 1
prcs_capacity = 1
prcs_scale = 2.0
prcs_intervals = np.random.exponential(prcs_scale, (n,nprocessors))
prcs_times = np.zeros(prcs_intervals.shape)
for j in range(prcs_times.shape[1]):
    for i in range(prcs_times.shape[0]):
        prcs_times[i,j] = sum(prcs_intervals[0:i,j])



# Adjust the queue values by the processor capacity, accounting for the number
# of total processors
prcs_queue = np.zeros(time.shape)
for i in range(prcs_times.shape[0]):
    nprocessed = 0
    for j in range(prcs_times.shape[1]):
        for t in prcs_times[:,j]:
            if t <= time[i]:
                # nprocessed += prcs_capacity
                if prcs_capacity <= queue[i]:
                    nprocessed += prcs_capacity
                else:
                    nprocessed += queue[i]

    prcs_queue[i] = nprocessed

plt.figure(2)
plt.plot(time,prcs_queue,label="Processed Items")
plt.plot(time,queue,label="Queue")
plt.legend()
# plt.title('Processed items over time')
plt.xlabel('Time')
plt.ylabel('Items')

for i in range(len(queue)):
    queue[i] = queue[i] - prcs_queue[i]

# Plot results
# plt.figure(3)
# plt.title('Queue with Processors Included')
# plt.plot(time,queue)
# plt.xlabel('Time')
# plt.ylabel('Queue')
# plt.show()
