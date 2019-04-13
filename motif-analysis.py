import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import function as fn
from motifs.static_motif_analysis import mcounter
from motifs.temporal_motif_analysis import Algorithm

# general settings for charts
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
matplotlib.rc('font', **font)

main_color = '#0000b3'
main_color2 = '#b30000'
secondary_color = '#b3b3ff'

dataset_options = {
    0: 'data/mathoverflow/sx-mathoverflow.txt',
    1 : 'data/mathoverflow/sx-mathoverflow-a2q.txt',
    2 : 'data/mathoverflow/sx-mathoverflow-c2q.txt',
    3 : 'data/mathoverflow/sx-mathoverflow-c2a.txt',
    4 : 'data/superuser/sx-superuser-a2q.txt',
    5 : 'data/superuser/sx-superuser-c2q.txt',
    6 : 'data/superuser/sx-superuser-c2a.txt',
    7 : 'data/askubintu/sx-askubintu-a2q.txt',
    8 : 'data/askubintu/sx-askubintu-c2q.txt',
    9 : 'data/askubintu/sx-askubintu-c2a.txt'
}


nodes_a2q, edges_per_t_a2q = fn.read_graph_from_file(dataset_options[0])
edges_per_t_hour = fn.aggregate_edges_by_granularity(edges_per_t_a2q, 'hour')

algorithm = Algorithm()
edges=[e[0] for e in edges_per_t_hour.values()]
times=[]
for t in edges_per_t_hour.keys():
    for elem in edges_per_t_hour[t]:
        times.append(int(t))
print(len(edges))
for i in range(1,24):
    print(algorithm.main_algorithm(edges, times, delta=i))