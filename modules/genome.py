
class Genome(object):

	def __init__(self, synapse_list):
		self.synapses = synapse_list
		
		self.gene_list = []
		self._generate_gene_list() 		# generates a list of synapse innovation numbers

		self.ave_gene_weight = 0
		self._generate_ave_synapse_weight()

	def _generate_gene_list(self):
		for synapse in self.synapses:
			self.gene_list.append(synapse.innovation)

	def _generate_ave_synapse_weight(self):
		for synapse in self.synapses:
			self.ave_gene_weight += (synapse.weight / len(self.gene_list))


	def __repr__(self):
		return "{}".format(self.synapses)