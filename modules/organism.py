from modules.neuron import Neuron
from modules.genome import Genome
from modules.synapse import Synapse
from modules.config import *

from sklearn import preprocessing
import numpy as np
import random
random.seed()


class Organism(object):

    ID = 0

    def __init__(self, genes=[]):

        if not genes:
            self.neurons = [Neuron(neuron_index) for neuron_index in range(INPUTS+OUTPUTS)]
            self.input_neurons = []
            self.output_neuron = self.neurons[-1]
            self.synapse_network = None
            self._init_synapse_network()
            self.topology = [INPUTS, OUTPUTS]
        else:
            self.neurons = genes[1]
            self.input_neurons = [neuron for neuron in self.neurons if neuron.layer == 'input']

            for neuron in self.neurons:
                if neuron.layer == 'output':
                    self.output_neuron = neuron
            

            self.synapse_network = genes[2]
            self.topology = genes[0]


        # Set unique ID
        self.ID = Organism.ID
        Organism.ID += 1

        self.speciesID = None
        self.intra_species_rank = None
        self.fitness = None
        self.species_matched = False

    def __repr__(self):
        return "Network {} -- Species ID {} -- Toplogy: {} -- Fitness: {} -- Rank: {}".format(self.ID, self.speciesID, self.topology, self.fitness, self.intra_species_rank)

    def _init_synapse_network(self):
        self.output_neuron.layer = 'output'
        new_synapses = []
        for input_index in range(INPUTS):
            input_neuron = self.neurons[input_index]
            new_synapse = Synapse(input_neuron=input_neuron, output_neuron=self.output_neuron, innovation_number=input_index)

            input_neuron.add_synapse(new_synapse)
            input_neuron.layer = 'input'

            new_synapses.append(new_synapse)
            self.input_neurons.append(input_neuron)

        self.synapse_network = Genome(new_synapses)


    def compare_genomes(self, other):
        number_excess_genes = 0
        number_disjoint_genes = 0
        W = 0
        N = 0

        organism_gene_list = self.synapse_network.gene_list
        species_gene_list = other.gene_list

        organism_min, organism_max = min(organism_gene_list), max(organism_gene_list)
        species_min, species_max = min(species_gene_list), max(species_gene_list)

        lower_bound = max(organism_min, species_min)    # lower bound of genome with largest innovation number
        upper_bound = min(organism_max, species_max)    # upper bound of genome with smallest innovation number


        # Calculate excess genes - number of genes outside of smallest domain
        for gene in organism_gene_list:
            if gene < lower_bound or gene > upper_bound:
                number_excess_genes += 1

        for gene in species_gene_list:
            if gene < lower_bound or gene > upper_bound:
                number_excess_genes += 1


        # Calculate disjoint genes - number of genes in the gaps
        for gene in range(lower_bound, upper_bound+1):
            if (gene in organism_gene_list) and (gene not in species_gene_list):
                number_disjoint_genes += 1
            if (gene in species_gene_list) and (gene not in organism_gene_list):
                number_disjoint_genes += 1

        # Calculate difference of average gene weights of genomes
        W = self.synapse_network.ave_gene_weight - other.ave_gene_weight

        # Calculate max length genome
        N = max(len(organism_gene_list), len(species_gene_list))

        return number_excess_genes, number_disjoint_genes, W, N



    def learn(self, environment_information):
        # Normalize information
        information = preprocessing.scale(np.asarray(environment_information))
        print("Input Evironment Info: {}".format(information))

        # Load input neurons
        for input_val, input_neuron in zip(information, self.input_neurons):
            for synapse in input_neuron.synapses:
                weight = synapse.weight
                print("weight: {}".format(weight))
                synapse.output_neuron.inputs.append(input_val*weight)


        # Feed forward through graph
        self._feed_forward()



    def replicate_unique_genes(self, new_synapses, parent, parent_gene_list):
        for gene_innovation_number in parent_gene_list:
            print("Replicating Gene: {}".format(gene_innovation_number))

            for synapse in parent.synapse_network.synapses:
                if gene_innovation_number == synapse.innovation:
                    new_synapse = synapse.copy()
                    new_synapses.append(new_synapse)
                    print("\tparent synapse: {}".format(synapse))
                    print("\tchild synapse: {}".format(new_synapse))

            print("\n")


    def mate(self, other):

        new_synapses = []
        new_neurons = []
        new_neuron_ID_tracker = []
        new_topology = self.topology

        parent1_genes = self.synapse_network.gene_list
        parent2_genes = other.synapse_network.gene_list
        print("\t\tParent 1 genes: {}".format(parent1_genes))
        print("\t\tParent 2 genes: {}".format(parent2_genes))


        parent1_unique_genes_list = list(set(parent1_genes) - set(parent2_genes))
        parent2_unique_genes_list = list(set(parent2_genes) - set(parent1_genes))
        shared_genes = list(set(parent1_genes) & set(parent2_genes))

        print("\t\tGenes unique to parent 1: {}".format(parent1_unique_genes_list))
        print("\t\tGenes unique to parent 2: {}".format(parent2_unique_genes_list))
        print("\t\tShared Genes amongst parent 1 and 2: {}".format(shared_genes))

        # Genes shared are 50/50 for inheritance
        inherit_from = [self, other]
        new_synapses = []
        for gene_innovation_number in shared_genes:
            print("Replicating Gene: {}".format(gene_innovation_number))

            random_parent_index = np.random.randint(2)


            for synapse in inherit_from[random_parent_index].synapse_network.synapses:
                if gene_innovation_number == synapse.innovation:
                    new_synapse = synapse.copy()
                    new_synapses.append(new_synapse)
                    print("\tparent synapse: {}".format(synapse))
                    print("\tchild synapse: {}".format(new_synapse))


                    new_ID = new_synapse.input_neuron.neuronID
                    if new_ID not in new_neuron_ID_tracker:
                        new_neuron_ID_tracker.append(new_synapse.input_neuron.neuronID)
                        new_neurons.append(new_synapse.input_neuron)

                    new_ID = new_synapse.output_neuron.neuronID
                    if new_ID not in new_neuron_ID_tracker:
                        new_neuron_ID_tracker.append(new_synapse.output_neuron.neuronID)
                        new_neurons.append(new_synapse.output_neuron)


            print("\n")
        print("*** NEW NEURONS: {}".format(new_neurons))
        print("type: {}".format(type(new_neurons)))

        # Inherit unique genes from parent 1
        self.replicate_unique_genes(new_synapses, self, parent1_unique_genes_list)

        # Inherit unique genes from parent 2
        self.replicate_unique_genes(new_synapses, other, parent2_unique_genes_list)


        new_genes = [new_topology, new_neurons, Genome(new_synapses)]
        new_organism = Organism(new_genes)



        return new_organism






    def _feed_forward(self):
        for synapse in self.synapse_network.synapses[INPUTS:]:
            print("Synapse: {}".format(synapse))
            synapse.activate()
            synapse.inactivate()


    def decision(self):
        output = self.output_neuron.activate()
        print("Decision: {}".format("not flap" if output == 0 else "flap"))
        print("\n")
        return output


if __name__ == '__main__':
    from unit_tests.nn_test import *
    unittest.main(Organism)
