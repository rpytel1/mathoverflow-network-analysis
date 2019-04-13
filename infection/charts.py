import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import math

# general settings for charts
font = {'family': 'normal',
        'weight': 'bold',
        'size': 22}

main_color = '#0000b3'
main_color2 = '#b30000'
secondary_color = '#b3b3ff'


def recognitionRateChart(for_report, ranking1name, ranking1, ranking2name, ranking2):
    step = 0.05
    f = np.arange(0, 1 + step, step)
    recognition_degrees = []
    for i in f:
        rr = top_f_recognition_rate(ranking1, ranking2, i)
        recognition_degrees.append(rr)

    if for_report:
        plt.figure(figsize=(15, 8), dpi=180, facecolor='w', edgecolor='k')

    plt.bar(f, recognition_degrees, width=step, align='center', color=main_color, edgecolor='black')
    plt.xlabel('Fraction of Nodes')
    plt.ylabel('Score')
    plt.title('r_' + ranking1name + '' + ranking2name + '(f) for f between 0 and 1')
    plt.xlim((-(step / 2), 1 + (step / 2)))
    plt.ylim((0, 1))
    plt.grid(True)


def top_f_recognition_rate(ranking1, ranking2, fraction):
    num_nodes = math.ceil(min(len(ranking1), len(ranking2)) * fraction)
    nodes_r1 = ranking1[0:num_nodes, 0]
    nodes_r2 = ranking2[0:num_nodes, 0]
    intersection = np.intersect1d(nodes_r1, nodes_r2)
    return len(intersection) / num_nodes if num_nodes != 0 else 0


def infectionProcessChart(for_report, processes_info):
    random_cumm_infections = processes_info[1].cumsum(axis=0)
    means = random_cumm_infections.mean(axis=1)
    stds = random_cumm_infections.std(axis=1)
    ts = np.arange(len(means))

    if for_report:
        plt.figure(figsize=(15, 8), dpi=180, facecolor='w', edgecolor='k')

    plt.errorbar(ts, means, yerr=stds, ecolor=secondary_color, color=main_color, linewidth=3)
    plt.xlabel('Time')
    plt.ylabel('# Infected Nodes')
    plt.xlim(0, 57791)
    plt.title('Information Spreading Process (N=' + str(processes_info[1].shape[1]) + ')')
    plt.grid(True)


def get_rankings_node_feature(array, column_to_order, asc):
    # The input array must have the nodes ids in the first column
    # and the value of the metric in the 'column to order' column.
    rankings = np.zeros((len(array), 3));
    ordered_array = array[((1 if asc else -1) * array[:, column_to_order]).argsort()]
    for i in range(len(rankings)):
        rankings[i, 0] = ordered_array[i, 0]
        rankings[i, 1] = ordered_array[i, column_to_order]
        rankings[i, 2] = i + 1
    return rankings


def get_G_local_clustering(G):
    G_local_clustering = np.zeros((G.number_of_nodes(), 2))
    for k, v in nx.clustering(G).items():
        G_local_clustering[k - 1, 0] = k
        G_local_clustering[k - 1, 1] = v
    return G_local_clustering
