import networkx as nx
import numpy as np


def infect_iteration(G):
    infected_nodes = [x for x, y in G.nodes(data=True) if y['infected'] == True]
    num_new_infected = 0
    for node in infected_nodes:
        for neighbor in nx.all_neighbors(G, node):
            if not G.nodes()[neighbor]['infected']:
                G.nodes()[neighbor]['infected'] = True
                num_new_infected += 1
    return num_new_infected


def update_graph_iteration(G, nodes, temporal_edges, times, t_id):
    t = times[t_id]
    if t_id >= 1:
        prev_t = times[t_id - 1]
        old_edges = list(dict.fromkeys(temporal_edges[prev_t]))  # removing duplicates
        for u, v in old_edges:
            G.remove_edge(u, v)
    new_edges = list(dict.fromkeys(temporal_edges[t]))  # removing duplicates
    for u, v in new_edges:
        G.add_edge(u, v)


def information_spreading_process(G, nodes, temporal_edges, t_iters):
    infections_per_step = []
    times = list(temporal_edges.keys())
    # Run iterations
    for t_id in range(t_iters):
        t = times[t_id]
        update_graph_iteration(G, nodes, temporal_edges, times, t_id)
        num_infected = infect_iteration(G)

        infections_per_step.append(num_infected)

    return infections_per_step


def multiple_processes(nodes, temporal_edges, mode, iterations_limit, t_steps):
    # Fix number of iterations to run
    t_iters = len(temporal_edges.keys())
    if t_steps != -1:
        t_iters = t_steps

    # Initialize the array with the nodes that we are going to iterate
    if mode == 'all_nodes':
        indexes = np.arange(0, min(iterations_limit, len(nodes)) + 1)
        iteration_range = [nodes[elem] for elem in indexes]

    elif mode == 'random':
        random_indexes = np.random.randint(0, len(nodes), iterations_limit)
        iteration_range = [nodes[elem] for elem in random_indexes]

    all_processes_info = np.ndarray((t_iters + 1, len(iteration_range) + 1))

    for process_run_id in range(len(iteration_range)):

        # Graph initialization
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        nx.set_node_attributes(G, False, 'infected')

        # Get seed node and infect it (t = 0)
        selected_node = iteration_range[process_run_id]

        G.nodes()[selected_node]['infected'] = True
        all_processes_info[0, process_run_id] = 1

        print(str(process_run_id) + '. Seed: ' + str(selected_node))

        infections_info = information_spreading_process(G, nodes, temporal_edges, t_iters)
        print(all_processes_info.shape)
        for i in range(len(infections_info)):
            all_processes_info[i + 1, process_run_id] = infections_info[i]

        G.clear()

    return (iteration_range, all_processes_info)
