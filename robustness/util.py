import copy
import math
from collections import OrderedDict

import networkx as nx


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
    final_id = math.floor(fraction * len(graph.nodes()))
    nodes_to_be_removed = nodes_ranking[:final_id]
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


