#!/usr/bin/python

import matplotlib.pyplot as plt

data = [1, 2, 3, 4]
plt.plot(data, data)
plt.xticks(data, ['8/6', '8/13', '8/20', '8/27'], rotation='vertical')
plt.axes().xaxis.grid()

plt.show()
