import numpy as np
import function as fn
import robustness.util as rb


def order_nodes_frac_infected_ranking(processes_info, frac):
    cumsum = processes_info[1].cumsum(axis=0)
    nodes_reached_fraction = np.zeros((cumsum.shape[1], 3))
    for i in range(cumsum.shape[1]):  # per node
        for j in range(cumsum.shape[0]):  # per time-step
            if cumsum[j][i] >= frac:
                nodes_reached_fraction[i, 0] = i + 1
                nodes_reached_fraction[i, 1] = j
                break
            if j == cumsum.shape[0] - 1:
                nodes_reached_fraction[i, 0] = i + 1
                nodes_reached_fraction[i, 1] = cumsum.shape[0] * 2

    # Order list by column and append index
    nodes_reached_fraction = nodes_reached_fraction[nodes_reached_fraction[:, 1].argsort()]
    for i in range(len(nodes_reached_fraction)):
        nodes_reached_fraction[i, 2] = i + 1

    return nodes_reached_fraction


dataset_options = {
    1: 'data/mathoverflow/sx-mathoverflow-a2q.txt',
    2: 'data/mathoverflow/sx-mathoverflow-c2q.txt',
    3: 'data/mathoverflow/sx-mathoverflow-c2a.txt',
}

nodes, edges_per_t = fn.read_graph_from_file(dataset_options[1])

G2 = fn.generate_aggregated_graph(nodes, edges_per_t)
G2 = G2.to_undirected()
nodes_by_clustering = rb.get_nodes_ordered_by_clustering(G2)
nodes_by_degree = rb.get_nodes_ordered_by_degree(G2)
nodes_by_betweeness = rb.get_nodes_ordered_by_betweeness(G2)

print(rb.perform_robustness_test(G2, 0.2, nodes_by_degree))
print(rb.perform_robustness_test(G2, 0.2, nodes_by_clustering))
print(rb.perform_robustness_test(G2, 0.2, nodes_by_betweeness))
