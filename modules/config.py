import numpy as np

POPULATION = 80
SPECIES_STALE_INDEX_THRESHOLD = 5

INPUTS = 6
OUTPUTS = 1

FRACTION_SELECTED = 0.05

ACTIVATION_THRESHOLD = 0.5

FLAP_THRESHOLD = 0.0

# Speciation Constants
C1 = 1.0        # Excess gene weight
C2 = 1.0        # Disjoint gene weight
C3 = 0.25        # Weight average weight
DELTA_T = 0.8  # New species threshold


WEAK_BREED_THRESHOLD = 2    # Cull 'weak' species that will not produce a breed greater than 1% of the organism population


DISABLE_INHERITED_GENE_CHANCE = 0.75
CROSSOVER_CHANCE = 0.5

# MUTATION RATES
# ------------------------------------------
CONNECTION_WEIGHT_MUTATION_RATE = 0.9
WEIGHT_MUTATION_RATE = 0.9

CONNECTION_MUTATION_RATE = 0.65
NEURON_MUTATION_RATE = 0.35

ENABLE_MUTATION_RATE = 0.2
DISABLE_MUTATION_RATE = 0.4
# ------------------------------------------
STEP_SIZE = 0.1
WEIGHT_MUT_FACTOR = 100.0
