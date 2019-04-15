import function as fn
from infection.infection_process import multiple_processes
from infection.charts import *

dataset_options = {
    1 : 'data/mathoverflow/sx-mathoverflow-a2q.txt',
    2 : 'data/mathoverflow/sx-mathoverflow-c2q.txt',
    3 : 'data/mathoverflow/sx-mathoverflow-c2a.txt',
}


nodes, edges_per_t = fn.read_graph_from_file(dataset_options[1])
edges_per_t_day = fn.aggregate_edges_by_granularity(edges_per_t, 'day')

processes_info_G2 = multiple_processes(nodes, edges_per_t_day, 'random', 10000, -1)

np.save('infection_data/process_info_hours_more', processes_info_G2)
