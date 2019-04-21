import networkx as nx
import csv
import matplotlib.pyplot as plt
import graphviz
import numpy as np
import math
import operator
from datetime import datetime


def find_date_limits(t1, t2):
    print('from')
    print(datetime.utcfromtimestamp(int(t1)).strftime('%Y-%m-%d %H:%M:%S'))
    print('to')
    print(datetime.utcfromtimestamp(int(t2)).strftime('%Y-%m-%d %H:%M:%S'))


def read_graph_from_file(path):
    edges_per_t = {}
    nodes = []
    with open(path) as file_handle:
        csv_reader = csv.reader(file_handle, delimiter=' ')
        #next(csv_reader) # skipping the header
        for row in csv_reader:  
            a = int(row[0])
            b = int(row[1])
            t = int(row[2])
            if a not in nodes:
                nodes.append(a)
            if b not in nodes:
                nodes.append(b)                
            if t in edges_per_t.keys():
                edges_per_t[t].append((a, b))
            else:
                edges_per_t[t] = [(a, b)] 
    return nodes, edges_per_t


# Aggregates all the edges. If there are duplicate edges 
# (multiple interactions in time) it collapses them. 
def generate_aggregated_graph(nodes, edges_per_t, repeated_edges_behavior=[]):
    G = nx.DiGraph()
    temp_edges = []
    for k, v in edges_per_t.items():
        temp_edges = temp_edges + v
    temp_edges = list(dict.fromkeys(temp_edges))
    # setup graph
    G.add_nodes_from(nodes)
    for e in temp_edges:
        G.add_edge(e[0], e[1])

    return G


# Computes the directed aggregated graph with a weight equal to the number
# of interactions that each node has
def generate_weighted_aggregated_graph(nodes, edges_per_t):
    G = nx.DiGraph()
    temp_edges = []
    for v in edges_per_t.values():
        temp_edges += v
    weight_dict = {i: temp_edges.count(i) for i in set(temp_edges)}
    # setup graph
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from([k+(weight_dict[k],) for k in weight_dict.keys()])
    return G


# Function that takes as an input the weighted graphs of each layer
# and creates a new directed graph with the accumulated weight based on 3-layer weights
def generate_weighted_total_graph(a2q, a2q_weight, c2q, c2q_weight, c2a, c2a_weight):
    G = nx.DiGraph()
    for s, d, e_weight in a2q.edges.data('weight'):
        G.add_edge(s, d, weight=e_weight*a2q_weight)
    for e in list(c2q.edges):
        if e in G.edges:
            nx.set_edge_attributes(G, {e: {'weight': G.edges[e[0], e[1]]['weight'] + c2q.edges[e[0], e[1]]['weight']*c2q_weight}})
        else:
            G.add_edge(e[0], e[1], weight=c2q.edges[e[0], e[1]]['weight']*c2q_weight)
    for e in list(c2a.edges):
        if e in G.edges:
            nx.set_edge_attributes(G, {e: {'weight': G.edges[e[0], e[1]]['weight'] + c2a.edges[e[0], e[1]]['weight']*c2a_weight}})
        else:
            G.add_edge(e[0], e[1], weight=c2a.edges[e[0], e[1]]['weight']*c2a_weight)
    return G


# Initializes a dictionary with all the timestamps sorted as the keys
# and their relative index as the value
def initiate_timestamps(edges_a2q, edges_c2q, edges_c2a):
    timestamps = {t: ind for ind, t in enumerate(sorted(list(map(lambda x: int(x),
                                                 set(list(edges_a2q.keys()) + list(edges_c2q.keys()) + list(
                                                     edges_c2a.keys()))))))}
    return timestamps


# Initializes the user dictionary with keys the ids of the users and as values
# empty dictionaries
def init_user_dict(nodes_a2q,  nodes_c2q, nodes_c2a):
    user_dict = {}
    for n in nodes_a2q + nodes_c2q + nodes_c2a:
        if n not in user_dict.keys():
            user_dict[n] = {}
    return user_dict


# Creates the user-interaction history dictionary - for each user in the dictionary
# his interaction history is recorded in another dict
def create_user_interactions_dict(path, nodes_a2q, edges_a2q, nodes_c2q, edges_c2q, nodes_c2a, edges_c2a):
    user_dict = init_user_dict(nodes_a2q, nodes_c2q, nodes_c2a)
    with open(path) as file_handle:
        csv_reader = csv.reader(file_handle, delimiter=' ')
        for row in csv_reader:
            a = int(row[0])
            b = int(row[1])
            t = int(row[2])
            if str(t) in edges_a2q.keys() and (str(a), str(b)) in edges_a2q[str(t)]:
                if t not in user_dict[str(a)].keys():
                    user_dict[str(a)][t] = ['giving answer']
                else:
                    user_dict[str(a)][t] += ['giving answer']
                if t not in user_dict[str(b)].keys():
                    user_dict[str(b)][t] = ['receiving answer']
                else:
                    user_dict[str(b)][t] += ['receiving answer']
            if str(t) in edges_c2q.keys() and (str(a), str(b)) in edges_c2q[str(t)]:
                if t not in user_dict[str(a)].keys():
                    user_dict[str(a)][t] = ['giving comment to question']
                else:
                    user_dict[str(a)][t] += ['giving comment to question']
                if t not in user_dict[str(b)].keys():
                    user_dict[str(b)][t] = ['receiving comment for question']
                else:
                    user_dict[str(b)][t] += ['receiving comment for question']
            if str(t) in edges_c2a.keys() and (str(a), str(b)) in edges_c2a[str(t)]:
                if t not in user_dict[str(a)].keys():
                    user_dict[str(a)][t] = ['giving comment to answer']
                else:
                    user_dict[str(a)][t] += ['giving comment to answer']
                if t not in user_dict[str(b)].keys():
                    user_dict[str(b)][t] = ['receiving comment for answer']
                else:
                    user_dict[str(b)][t] += ['receiving comment for answer']
    return user_dict


# Calculates the accumulative degree (in and out) of each user
# per timestep of active interaction
def calculate_degree_per_time(user_dict):
    degree_dict = {}
    in_degree_dict = {}
    out_degree_dict = {}
    for user, history in user_dict.items():
        last = 0
        last_in = 0
        last_out = 0
        for t, activity in dict(sorted(history.items())).items():
            last += len(activity)
            last_in += len([a for a in activity if a.startswith('receiving')])
            last_out += len([a for a in activity if a.startswith('giving')])
            if user not in degree_dict.keys():
                degree_dict[user] = {t: last}
                in_degree_dict[user] = {t: last_in}
                out_degree_dict[user] = {t: last_out}
            else:
                degree_dict[user][t] = last
                in_degree_dict[user][t] = last_in
                out_degree_dict[user][t] = last_out
    return degree_dict, in_degree_dict, out_degree_dict


# Creates the interaction value dictionary for each user
# by aggregating the basic and the cumulative values
def calculate_interaction_model(user_dict):
    a = 1.6  # alpha parameter is the weight of the cumulative part
    weight_map = {'giving answer': 0.4823,
                  'receiving answer': 0.4713,
                  'giving comment to question': 0.5870,
                  'receiving comment for question': 0.3744,
                  'giving comment to answer': 0.6156,
                  'receiving comment for answer': 0.4832
                  }
    basic_dict = {}
    cumulative_dict = {}
    activity_dict = {}
    interactions_dict = {}
    for user, history in user_dict.items():
        last = 0
        for t, activity in dict(sorted(history.items())).items():
            last += len(activity)
            if user not in activity_dict.keys():
                activity_dict[user] = {t: last}
            else:
                activity_dict[user][t] = last
    for user, history in user_dict.items():
        basic_dict[user] = {t: sum(list(map(lambda x: weight_map[x], activity))) for t, activity in history.items()}
        cumulative_dict[user] = {t: act_weight*a*(1-1/(activity_dict[user][t]+1))
                                 for t, act_weight in basic_dict[user].items()}
        interactions_dict[user] = {t: basic_dict[user][t]+cumulative_dict[user][t] for t in history.keys()}
    return interactions_dict


# Calculates the delta_n value of each user
# so that frequency of the interactions in a given time period are considered
def calculate_interval(user_dict):
    t_a = 30*86400  # 1 month time space is checked
    interval_dict = {}
    for user, history in user_dict.items():
        last_t = 0
        for t, activity in dict(sorted(history.items())).items():
            if user not in interval_dict.keys():
                interval_dict[user] = {t: 0}
            else:
                interval_dict[user][t] = (t-last_t)/t_a
            last_t = t
    return interval_dict


# Calculates the trust for each user per timestamp
# using the interaction and interval dictionaries
def calculate_trust(interactions_dict, interval_dict):
    beta = 0.99  # parameter to adjust the forgetting factor
    trust_dict = {}
    for user in interactions_dict.keys():
        trust_dict[user] = {0: 1}  # all users gain a trust of 1 in zero time
    for user, history in interactions_dict.items():
        last_t = 0
        for t, activity in dict(sorted(history.items())).items():
            trust_dict[user][t] = trust_dict[user][last_t]*beta**interval_dict[user][t]+interactions_dict[user][t]
            last_t = t
    return trust_dict


# Aggregates the activity of each user for the given granularity factor
# by keeping the latest value that the user reported in the granularity bin
def aggregate_user_dict_by_granularity(user_dict, granularity, timestamps):
    aggregated_dict = {}
    granularity_factor = 1 if granularity == 'sec' else 60 if granularity == 'min' else 3600 if granularity == 'hour' \
        else 3600 * 24
    min_t = min([k for k in list(map(lambda x: int(x), list(timestamps.keys()))) if k != 0])
    for user, history in user_dict.items():
        for t, activity in dict(sorted(history.items())).items():
            bin_id = math.floor((float(t) - float(min_t))/granularity_factor)
            if user in aggregated_dict.keys():
                aggregated_dict[user][bin_id] = activity
            else:
                aggregated_dict[user] = {bin_id: activity}
    return aggregated_dict


# Aggregates the timestamps appearing in the dataset by
# the given granularity factor
def aggregate_timestamps_by_granularity(timestamps, granularity):
    binned_timestamps = {}
    granularity_factor = 1 if granularity == 'sec' else 60 if granularity == 'min' else 3600 if granularity == 'hour' \
        else 3600 * 24
    min_t = min([k for k in list(map(lambda x: int(x), list(timestamps.keys()))) if k != 0])
    for t, ind in dict(sorted(timestamps.items())).items():
        bin_id = math.floor((float(t) - float(min_t))/granularity_factor)
        if bin_id not in binned_timestamps.keys():
            binned_timestamps[bin_id] = 1
        else:
            binned_timestamps[bin_id] += 1
    return binned_timestamps


def make_modelled_trust_chart(metric_dict, trust_dict, binned_timestamps, best_nodes, filename):
    y_pos = np.arange(max(binned_timestamps.keys())+1)
    for ind, dict_in_check in enumerate([metric_dict, trust_dict]):
        m = [0]*(max(binned_timestamps.keys())+1)
        if not best_nodes:
            last_t = {i: 0 for i in metric_dict.keys()}
        else:
            last_t = {i: 0 for i in metric_dict.keys() if i in best_nodes}
        for t in range(0, max(binned_timestamps.keys())+1):
            if not best_nodes:
                for user, history in dict_in_check.items():
                    if t in history.keys():
                        m[t] += history[t]
                        last_t[user] = t
                    else:
                        if last_t[user] != 0:
                            m[t] += history[last_t[user]]
            else:
                for user in best_nodes:
                    if t in dict_in_check[user].keys():
                        m[t] += dict_in_check[user][t]
                        last_t[user] = t
                    else:
                        if last_t[user] != 0:
                            m[t] += dict_in_check[user][last_t[user]]
        if not best_nodes:
            if not ind:
                plt.plot(y_pos, m, label='degree')
            else:
                plt.plot(y_pos, m, label='modelled trust')
        else:
            if not ind:
                plt.plot(y_pos, list(map(lambda x: x/len(best_nodes), m)), label='average degree')
            else:
                plt.plot(y_pos, list(map(lambda x: x/len(best_nodes), m)), label='average modelled trust')
    plt.xticks(y_pos[0:len(y_pos):200], y_pos[0:len(y_pos):200])
    # plt.xticks(rotation=45)
    plt.xlabel('Days')
    # plt.ylabel('Users\' aggregated degree and reputation per day')
    if not best_nodes:
        plt.title('Degree and Modelled Trust through time')
    else:
        plt.title('Degree and Modelled Trust through time for best 100users')
    plt.grid(True)
    plt.legend()

    #plt.show()
    plt.savefig(filename)
    plt.clf()


# Computes the degree of each node in the graph
# First column is the id and second is the degree
def get_graph_degrees(G):
    G_degrees = np.zeros((len(G.degree()), 2))
    position = 0
    for i, v in G.degree():
        G_degrees[position, 0] = i
        G_degrees[position, 1] = v
        position += 1
    return G_degrees


# Recomputes the edges_per_t so aggregating them with 
# a given granularity (This is relative to the first 
# timestamp of the dataset) 
def aggregate_edges_by_granularity(edges_per_t, granularity):
    new_edges = {}
    min_t = min([k for k in edges_per_t.keys()])
    max_t = max([k for k in edges_per_t.keys()])

    granularity_factor = 1 if granularity == 'sec' else 60 if granularity == 'min' else 3600 if granularity == 'hour' \
        else 3600 * 24

    for k, v in edges_per_t.items():
        second_since_start = float(k) - float(min_t)  # the start is the first element's timestamp
        bin_id = math.floor(second_since_start/granularity_factor)
        
        if bin_id in new_edges:
            new_edges[bin_id] = new_edges[bin_id] + v
        else:
            new_edges[bin_id] = [] + v
    
    return new_edges


def make_rich_club_coefficient_chart(rich_dict, filename):
    y_pos = np.arange(len(rich_dict['out-degree'].keys()))
    for metric, metric_in_time in rich_dict.items():
        m = []
        for metric_dict in metric_in_time.values():
            m.append(metric_dict['coefficient'])
        plt.plot(y_pos, m, label=metric)
    plt.xticks(y_pos[0:len(y_pos):25], [round(metric_dict['nodes']/24818*100,1)
                                        for ind, metric_dict in rich_dict['out-degree'].items()
                                         if ind in y_pos[0:len(y_pos):25]])
    # plt.xticks(rotation=45)
    plt.xlabel('Fraction of nodes (%)')
    plt.ylabel('Rich club coefficient')
    plt.title('Rich club coefficient based on 4 centrality metrics')
    plt.grid(True)
    plt.legend()

    #plt.show()
    plt.savefig(filename)
    plt.clf()


def make_rich_club_importance_chart(rich_dict, filename):
    y_pos = np.arange(len(rich_dict['out-degree'].keys()))
    for metric, metric_in_time in rich_dict.items():
        m = []
        for metric_dict in metric_in_time.values():
            m.append(metric_dict['importance'])
        plt.plot(y_pos, m, label=metric)
    plt.xticks(y_pos[0:len(y_pos):25], [round(metric_dict['nodes']/24818*100,1)
                                        for ind, metric_dict in rich_dict['out-degree'].items()
                                         if ind in y_pos[0:len(y_pos):25]])
    # plt.xticks(rotation=45)
    plt.xlabel('Fraction of nodes (%)')
    plt.ylabel('Importance')
    plt.title('Rich club importance based on 4 centrality metrics')
    plt.grid(True)
    plt.legend()

    #plt.show()
    plt.savefig(filename)
    plt.clf()
