import random
import numpy


def random_generator():
    random.seed(1337)
    while True:
        yield random.random() * 2.0 - 1.0


def sine_generator():
    t = 0.0
    while True:
        yield numpy.sin(t)
        t += 0.05
