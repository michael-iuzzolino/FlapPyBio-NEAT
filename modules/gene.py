from modules.config import *

import numpy as np
np.random.seed()


class Gene(object):
    """
        The gene is analogous to the synapse. It contains the following key data elements:
            1. Innovation numbers
            2. Input neuron
            3. Output neuron
            4. Weight of connection
            5. Enabled / Disabled
    """


    def __init__(self, innovation_number=None, input_neuron_id=None, output_neuron_id=None, weight=None):

        self.innovation_number = innovation_number

        # Need to implement
        self.input_neuron_id = input_neuron_id
        self.output_neuron_id = output_neuron_id

        if weight is None:
            weight = np.random.randn()
        self.weight = weight

        self.enabled = True
