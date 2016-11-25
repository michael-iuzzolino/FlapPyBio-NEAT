from modules.synapse import Synapse
from modules.config import *
import numpy as np
import random

random.seed()

class Neuron(object):
    def __init__(self, neuronID, layer=None):
        self.layer = layer
        self.neuronID = neuronID
        self.synapses = []
        self.inputs = []
        self.output = None

    def __repr__(self):
        return '({} Neuron {})'.format(self.layer, self.neuronID)

    def add_synapse(self, new_synapse):
        self.synapses.append(new_synapse)

    def copy(self):
        neuronID = np.copy(self.neuronID)
        layer = np.copy(self.layer)
        new_neuron = Neuron(neuronID, layer)
        return new_neuron


    def activate(self):
        input_sums = 0.0
        for input_value in self.inputs:
            print("\t\t\tinput value: {}".format(input_value))
            input_sums += input_value

        output = 0 if input_sums <= 0.5 else 1
        self.inactivate()
        print("\tFinal Output: {}".format(output))
        return output

    def inactivate(self):
        self.inputs = []

if __name__ == '__main__':
    from unit_tests.neuron_test import *
    unittest.main(Neuron)
