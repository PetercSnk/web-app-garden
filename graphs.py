import matplotlib.pyplot as plt
import random
import numpy as np


plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
line_1, = ax.plot(x, y, "-o")

time = 0
while True:
    moisture_1 = random.randint(0, 0.7)
    moisture_2 = random.randint(0.5, 0.9)
    temp = random.randint(10, 25)
    time = time + 1
    line_1.set_ydata(moisture_1)
    fig.canvas.draw()


