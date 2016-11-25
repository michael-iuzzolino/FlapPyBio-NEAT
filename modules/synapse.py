import numpy as np
import random
random.seed()

ACTIVATION_THRESHOLD = 0.5

class Synapse(object):
    def __init__(self, input_neuron=None, output_neuron=None, innovation_number=None, weight=None, enabled=True):
        self.input_neuron = input_neuron
        self.output_neuron = output_neuron
        if not weight:
        	self.weight = np.random.randn()
        else:
        	self.weight = weight
        self.innovation = innovation_number
        self.enabled = enabled

    def __repr__(self):
    	return "Innovation number {}\n\t\tConnections: {} --> {}".format(self.innovation, self.input_neuron, self.output_neuron)

    def activate(self):
    	input_sum = 0
    	output_value = 0
    	for input_value in self.input_neuron.inputs:
    		input_sum += input_value

    	input_sum = 1.0 / (1.0 + np.exp(-input_sum))
    	print("\t\tInput value: {}".format(input_sum))

    	output_value = input_sum * self.weight
    	print("\t\tOutput value: {}\n".format(output_value))

    	self.output_neuron.inputs.append(output_value)

    def inactivate(self):
    	self.input_neuron.inactivate()

    def copy(self):
        new_input_neuron = self.input_neuron.copy()
        new_output_neuron = self.output_neuron.copy()
        innovation = self.innovation
        new_weight = np.copy(self.weight)

        enabled = self.enabled

        new_synapse = Synapse(new_input_neuron, new_output_neuron, innovation, new_weight, enabled)
        return new_synapse


if __name__ == '__main__':
    from unit_tests.synapse_test import *
    unittest.main(Synapse)
