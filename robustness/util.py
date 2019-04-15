import copy
import math

import networkx as nx


def get_num_active_nodes(graph):
    Gc = max(nx.connected_component_subgraphs(graph), key=len)
    return len(Gc.nodes())


def get_num_of_clusters(graph):
    return len(nx.connected_component_subgraphs(graph))


def remove_nodes_from_graph(graph, nodes_to_be_removed):
    new_graph = copy.deepcopy(graph)

    new_graph.remove_nodes_from(nodes_to_be_removed)
    return new_graph


def perform_robustness_test(graph, fraction, nodes_ranking):
    final_id = math.floor(fraction * len(graph.nodes()))
    nodes_to_be_removed = nodes_ranking[final_id]
    new_graph = remove_nodes_from_graph(graph, nodes_to_be_removed)

    return get_num_active_nodes(new_graph), get_num_of_clusters(new_graph)

