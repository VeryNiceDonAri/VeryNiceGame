import random
from value_plotter import plot_value

data_list = [0]

def append_and_get():
    data_list.append(random.random())
    return data_list[-1]

plot_value(append_and_get, interval=1/60)

while True:
    print("Hi~!")