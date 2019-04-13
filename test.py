import networkx as nx
import numpy as np

from motifs.temporal_motif_analysis import Algorithm

edges = [(1, 2), (1, 3), (2, 4), (1, 3)]
times = [0.1, 0.2, 0.3, 0.4]

alg = Algorithm()
print(alg.main_algorithm(edges, times, 0.4))

g=nx.erdos_renyi_graph(10,0.9,directed=True)
edges=list(g.edges())
times=np.arange(0,0.1*len(edges),0.1)

print(alg.main_algorithm(edges, times, 20))



