import copy
import math
import operator
from collections import OrderedDict

import networkx as nx
import pandas as pd
import numpy as np
from operator import itemgetter


def get_num_active_nodes(graph):
    Gc = max(nx.connected_component_subgraphs(graph), key=len)
    return len(Gc.nodes())


def get_num_of_clusters(graph):
    sub_graphs = list(nx.connected_component_subgraphs(graph))
    return len(sub_graphs)


def remove_nodes_from_graph(graph, nodes_to_be_removed):
    new_graph = copy.deepcopy(graph)

    new_graph.remove_nodes_from(nodes_to_be_removed)
    return new_graph


def perform_robustness_test(graph, fraction, nodes_ranking):
    nodes_to_be_removed = get_failed_nodes(graph, fraction, nodes_ranking)
    new_graph = remove_nodes_from_graph(graph, nodes_to_be_removed)

    return get_num_active_nodes(new_graph), get_num_of_clusters(new_graph)


def get_nodes_ordered_by_degree(graph, reverse=True):
    degree_view = list(graph.degree)
    sorted_list = sorted(degree_view, key=lambda tup: tup[1], reverse=reverse)
    nodes_ranking = [elem[0] for elem in sorted_list]
    return nodes_ranking


def get_nodes_ordered_by_clustering(graph, reverse=True):
    clustering = nx.clustering(graph)
    ordered_clustering = OrderedDict(sorted(clustering.items(), key=lambda t: t[1], reverse=reverse))
    return list(ordered_clustering.keys())


def get_nodes_ordered_by_betweeness(graph, reverse=True):
    betweeness = nx.betweenness_centrality(graph)
    ordered_clustering = OrderedDict(sorted(betweeness.items(), key=lambda t: t[1], reverse=reverse))
    return list(ordered_clustering.keys())


def get_failed_nodes(graph, fraction, nodes_ranking):
    final_id = math.floor(fraction * len(graph.nodes()))
    return nodes_ranking[:final_id]


def make_active_nodes_graph(graph, fraction, nodes_ranking):
    nodes_to_be_removed = get_failed_nodes(graph, fraction, nodes_ranking)

    new_graph = remove_nodes_from_graph(graph, nodes_to_be_removed)
    Gc = max(nx.connected_component_subgraphs(new_graph), key=len)

    nodes_list = Gc.nodes
    final_graph = copy.deepcopy(graph)

    nx.set_node_attributes(final_graph, True, 'operational')
    for i in nodes_list:
        final_graph.nodes()[i]['operational'] = False

    pos = nx.spring_layout(final_graph)
    plot_graph_by_attr(final_graph, 'operational', pos)


def make_failed_nodes_graph(graph, fraction, nodes_ranking):
    nodes_to_be_removed = get_failed_nodes(graph, fraction, nodes_ranking)

    final_graph = copy.deepcopy(graph)

    nx.set_node_attributes(final_graph, True, 'operational')
    for i in nodes_to_be_removed:
        final_graph.nodes()[i]['operational'] = False

    pos = nx.spring_layout(final_graph)
    plot_graph_by_attr(final_graph, 'operational', pos)


def plot_graph_by_attr(G, attr, pos):
    nodes_attr_on = [x for x, y in G.nodes(data=True) if y[attr] == True]
    nodes_attr_off = [x for x, y in G.nodes(data=True) if y[attr] == False]
    # pos = nx.spring_layout(G)
    nx.draw(G, pos, node_color='g', node_size=100, with_labels=True)
    nx.draw_networkx_nodes(G, pos, nodelist=nodes_attr_on, node_color='r', node_size=100)
    nx.draw_networkx_nodes(G, pos, nodelist=nodes_attr_off, node_color='g', node_size=50, label='')


def get_nodes_ordered_by_reputation(graph):
    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    reputation_dict = dict(zip(df.UserId, df.Reputation))

    reputation_dict = OrderedDict(sorted(reputation_dict.items()))

    temp_reputation_dict = {k: v for k, v in reputation_dict.items() if str(k) in graph.nodes}
    temp_reputation_dict = OrderedDict(sorted(temp_reputation_dict.items(), key=operator.itemgetter(1), reverse=True))
    #
    std = np.std(list(temp_reputation_dict.values()))
    max_value = max(list(temp_reputation_dict.values()))
    i = 0
    for v in temp_reputation_dict.values():
        if v > max_value - 3 * std:
            i += 1

    return list(temp_reputation_dict.keys()), i / len(graph.nodes())


def get_nodes_ordered_by_upvotes(graph):
    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    reputation_dict = dict(zip(df.UserId, df.UpVotes))

    reputation_dict = OrderedDict(sorted(reputation_dict.items()))

    temp_reputation_dict = {k: v for k, v in reputation_dict.items() if str(k) in graph.nodes}
    temp_reputation_dict = OrderedDict(sorted(temp_reputation_dict.items(), key=operator.itemgetter(1), reverse=True))
    #
    std = np.std(list(temp_reputation_dict.values()))
    max_value = max(list(temp_reputation_dict.values()))
    i = 0
    for v in temp_reputation_dict.values():
        if v > max_value - 3 * std:
            i += 1

    return list(temp_reputation_dict.keys()), i / len(graph.nodes())

