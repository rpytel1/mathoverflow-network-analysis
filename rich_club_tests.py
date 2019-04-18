import networkx as nx
import function as fn
import hypothesis_testing as ht
import statistics


def create_rich_graph(init_G, rich_nodes):
    return init_G.subgraph([r[0] for r in rich_nodes])


a2q = nx.read_gpickle('pickles/graphs/mathoverflow/a2q.gpickle')
c2q = nx.read_gpickle('pickles/graphs/mathoverflow/c2q.gpickle')
c2a = nx.read_gpickle('pickles/graphs/mathoverflow/c2a.gpickle')
G_total = fn.generate_weighted_total_graph(a2q, 1, c2q, 1, c2a, 1)
degree_dict = ht.get_degree_centrality()
degree_tuples = sorted(degree_dict['a2q'], key=lambda tup: tup[2])
std = statistics.stdev([d[1] for d in degree_tuples])
rich_nodes = [d for d in degree_tuples if abs(d[1]-degree_tuples[0][1]) <= 40*std]
rich_G = create_rich_graph(G_total, rich_nodes)
rich_club_coeff = 2*rich_G.number_of_edges()/(rich_G.number_of_nodes()*(rich_G.number_of_nodes()-1))
print('rich club coefficient:', rich_club_coeff)
# clust_coeff = nx.average_clustering(rich_G)
# assortativity_out_in = nx.degree_assortativity_coefficient(rich_G, x='out', y='in', weight='weight')
# assortativity_out_out = nx.degree_assortativity_coefficient(rich_G, x='out', y='out', weight='weight')
# assortativity_in_in = nx.degree_assortativity_coefficient(rich_G, x='in', y='in', weight='weight')
# assortativity_in_out = nx.degree_assortativity_coefficient(rich_G, x='in', y='out', weight='weight')

