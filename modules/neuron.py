from modules.config import *

import numpy as np
np.random.seed()

class Neuron(object):
    def __init__(self, neuron_id=None):
        self.ID = neuron_id

        self.input = 0.0
        self.output = 0.0
    

    def activate(self):
        self.output = 2.0 / (1.0 + np.exp(-4.9 * self.input)) - 1.0
        self.__inactivate()


    def __inactivate(self):
        self.input = 0.0

    def __repr__(self):
        return "{}".format(self.ID)
