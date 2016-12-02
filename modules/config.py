import numpy as np

POPULATION = 80
SPECIES_STALE_INDEX_THRESHOLD = 15

INPUTS = 6
OUTPUTS = 1

ACTIVATION_THRESHOLD = 0.5


# Speciation Constants
C1 = 2.0        # Excess weight
C2 = 2.0        # Disjoint weight
C3 = 0.4        # Weight average weight
DELTA_T = 0.5   # New species threshold


WEAK_BREED_THRESHOLD = 2    # Cull 'weak' species that will not produce a breed greater than 1% of the organism population


DISABLE_INHERITED_GENE_CHANCE = 0.75
CROSSOVER_CHANCE = 0.75

# MUTATION RATES
# ------------------------------------------
CONNECTION_WEIGHT_MUTATION_RATE = 0.8
WEIGHT_MUTATION_RATE = 0.9

CONNECTION_MUTATION_RATE = 0.3
NEURON_MUTATION_RATE = 0.03

ENABLE_MUTATION_RATE = 0.2
DISABLE_MUTATION_RATE = 0.4
# ------------------------------------------
STEP_SIZE = 0.1
