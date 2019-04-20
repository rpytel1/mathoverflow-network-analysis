import networkx as nx
import function as fn
import hypothesis_testing as ht
import numpy as np
import statistics
import matplotlib.pyplot as plt
import pickle


def create_rich_graph(init_G, rich_nodes):
    return init_G.subgraph([r[0] for r in rich_nodes])


def get_in_degree_sorting(G):
    tuples = []
    for ind, d in enumerate(sorted(list(G.in_degree(weight='weight')), key=lambda tup: tup[1], reverse=True)):
        tuples.append((d[0], d[1], ind))
    return tuples


def get_out_degree_sorting(G):
    tuples = []
    for ind, d in enumerate(sorted(list(G.out_degree(weight='weight')), key=lambda tup: tup[1], reverse=True)):
        tuples.append((d[0], d[1], ind))
    return tuples


def get_degree_sorting(G):
    tuples = []
    for ind, d in enumerate(sorted(list(G.degree(weight='weight')), key=lambda tup: tup[1], reverse=True)):
        tuples.append((d[0], d[1], ind))
    return tuples


def list_to_percentiles(numbers):
    pairs = list(zip(numbers, range(len(numbers))))
    pairs.sort(key=lambda p: p[0])
    result = [0]*len(numbers)
    for rank in range(len(numbers)):
        result[pairs[rank][1]] = rank*100.0/(len(numbers)-1)
    return result


def find_rich_coeff(G_total, num_of_nodes):
    rich_dict = {}
    check = ''
    for sel in [0, 1, 2, 3]:
        if sel == 0:
            metric_dict = ht.get_degree_centrality(degree_type='out')
            metric_tuples = sorted(metric_dict['total'], key=lambda tup: tup[2])
            rich_dict['out-degree'] = {}
            check = 'out-degree'
        elif sel == 1:
            metric_dict = ht.get_degree_centrality(degree_type='in')
            metric_tuples = sorted(metric_dict['total'], key=lambda tup: tup[2])
            rich_dict['in-degree'] = {}
            check = 'in-degree'
        elif sel == 2:
            metric_dict = ht.get_closeness_centrality(cc_type='out')
            metric_tuples = sorted(metric_dict['total'], key=lambda tup: tup[2])
            rich_dict['out-closeness'] = {}
            check = 'out-closeness'
        elif sel == 3:
            metric_dict = ht.get_closeness_centrality(cc_type='in')
            metric_tuples = sorted(metric_dict['total'], key=lambda tup: tup[2])
            rich_dict['in-closeness'] = {}
            check = 'in-closeness'
        elif sel == 4:
            metric_dict = ht.get_closeness_centrality(cc_type='in')
            metric_tuples = sorted(metric_dict['c2q'], key=lambda tup: tup[2])
        elif sel == 5:
            metric_dict = ht.get_eigenvector_centrality(ec_type='out')
            metric_tuples = sorted(metric_dict['total'], key=lambda tup: tup[2])
        elif sel == 6:
            metric_dict = ht.get_eigenvector_centrality(ec_type='in')
            metric_tuples = sorted(metric_dict['total'], key=lambda tup: tup[2])
        elif sel == 7:
            metric_dict = ht.get_eigenvector_centrality(ec_type='out')
            metric_tuples = sorted(metric_dict['c2q'], key=lambda tup: tup[2])
        else:
            metric_tuples = get_out_degree_sorting(G_total)
        print('Now processing', check)
        # std = statistics.stdev([d[1] for d in metric_tuples])
        # rich_nodes = [d for d in metric_tuples if abs(d[1]-metric_tuples[0][1]) <= 45*std]
        for ind, i in enumerate(list(np.linspace(0.001, 0.25, 100))):
            print(ind)
            rich_nodes = metric_tuples[0:int(i * num_of_nodes)]
            # percentiles = list_to_percentiles([d[1] for d in metric_tuples])
            # rich_nodes = [d for ind, d in enumerate(metric_tuples) if percentiles[ind] >= 99.5]
            rich_G = create_rich_graph(G_total, rich_nodes)
            # print('number of rich nodes:', rich_G.number_of_nodes())
            # print('number of rich interactions:', rich_G.number_of_edges())
            # rich_club_coeff = 2*rich_G.number_of_edges()/(rich_G.number_of_nodes()*(rich_G.number_of_nodes()-1))
            # print('rich club coefficient:', rich_club_coeff)
            undirected_rich_G = rich_G.to_undirected(reciprocal=False)
            # print('number of rich undirected interactions:', undirected_rich_G.number_of_edges())
            rich_club_coeff = 2 * undirected_rich_G.number_of_edges() / \
                              (undirected_rich_G.number_of_nodes() * (undirected_rich_G.number_of_nodes() - 1))
            importance = rich_G.size(weight='weight') / G_total.size(weight='weight')
            rich_dict[check][ind] = {'nodes': int(i * num_of_nodes),
                                     'coefficient': round(rich_club_coeff, 4),
                                     'importance': round(importance, 4)
                                     }
    filehandler = open("rich_club/rich_club_recordings_more_zoomed.pickle", "wb")
    pickle.dump(rich_dict, filehandler)
    filehandler.close()


def print_rich_club_graphs(filename1, filename2):
    filehandler = open("rich_club/rich_club_recordings_more_zoomed.pickle", "rb")
    rich_dict = pickle.load(filehandler)
    filehandler.close()
    fn.make_rich_club_coefficient_chart(rich_dict, filename1)
    fn.make_rich_club_importance_chart(rich_dict, filename2)


a2q = nx.read_gpickle('pickles/graphs/mathoverflow/a2q.gpickle')
c2q = nx.read_gpickle('pickles/graphs/mathoverflow/c2q.gpickle')
c2a = nx.read_gpickle('pickles/graphs/mathoverflow/c2a.gpickle')
G_total = fn.generate_weighted_total_graph(a2q, 1, c2q, 1, c2a, 1)
num_of_nodes = G_total.number_of_nodes()
# print('Total number of users:', G_total.number_of_nodes())
# print('Total number of interactions:', G_total.number_of_edges())
# print('Pure answers to questions:', a2q.number_of_edges())
# print('Pure comments to questions:', c2q.number_of_edges())
# print('Pure comments to answers:', c2a.number_of_edges())
# find_rich_coeff(G_total, num_of_nodes)
filename1 = 'rich_club/rich_coefficient_graph_more_zoomed.png'
filename2 = 'rich_club/rich_importance_graph_more_zoomed.png'
print_rich_club_graphs(filename1, filename2)
# print('rich club coefficient:', rich_club_coeff)
# nx.draw_networkx(undirected_rich_G, pos=nx.random_layout(undirected_rich_G), arrowsize=5,
#                  node_size=100, font_size=10, edge_color='b', label='rich club graph')
# plt.show()
# size = G_total.size(weight='weight')
# print('size of the original graph:', size)
# num_strong_components = nx.number_strongly_connected_components(G_total)
# num_weak_components = nx.number_weakly_connected_components(G_total)
# num_components = nx.number_connected_components(G_total.to_undirected(reciprocal=False))
# print('number of components:', num_components)
# print('number of strongly connected components:', num_strong_components)
# print('number of weakly connected components:', num_weak_components)
# size = rich_G.size(weight='weight')
# print('size of the rich graph:', size)
# num_strong_components = nx.number_strongly_connected_components(rich_G)
# num_weak_components = nx.number_weakly_connected_components(rich_G)
# num_components = nx.number_connected_components(undirected_rich_G)
# print('number of rich components:', num_components)
# print('number of rich strongly connected components:', num_strong_components)
# print('number of rich weakly connected components:', num_weak_components)
# clust_coeff = nx.average_clustering(rich_G)
# assortativity_out_in = nx.degree_pearson_correlation_coefficient(rich_G, x='out', y='in', weight='weight')
# assortativity_out_out = nx.degree_pearson_correlation_coefficient(rich_G, x='out', y='out', weight='weight')
# assortativity_in_in = nx.degree_pearson_correlation_coefficient(rich_G, x='in', y='in', weight='weight')
# assortativity_in_out = nx.degree_pearson_correlation_coefficient(rich_G, x='in', y='out', weight='weight')

