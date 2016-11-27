from modules.config import *

import numpy as np
np.random.seed()

class Neuron(object):
    def __init__(self, neuron_id=None):
        self.ID = neuron_id

        self.input = 0.0
        self.output = 0.0

        self.type = None
        self.layer_level = None
