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


# Initializes the user dictionary with keys the ids of the users and as values
# dictionaries with keys the timestamps in the dataset and values empty strings
def init_user_dict(nodes_a2q, edges_a2q, nodes_c2q, edges_c2q, nodes_c2a, edges_c2a):
    user_dict = {}
    temp = {t: '' for t in sorted(list(map(lambda x: int(x),
                                    set(list(edges_a2q.keys()) + list(edges_c2q.keys()) + list(edges_c2a.keys())))))}
    for n in nodes_a2q + nodes_c2q + nodes_c2a:
        if n not in user_dict.keys():
            user_dict[n] = temp
    return user_dict


# Creates the user-interaction history dictionary - for each user in the dictionary
# his interaction history is recorded in another dict
def create_user_interactions_dict(path, nodes_a2q, edges_a2q, nodes_c2q, edges_c2q, nodes_c2a, edges_c2a):
    user_dict = init_user_dict(nodes_a2q, edges_a2q, nodes_c2q, edges_c2q, nodes_c2a, edges_c2a)
    with open(path) as file_handle:
        csv_reader = csv.reader(file_handle, delimiter=' ')
        for row in csv_reader:
            a = int(row[0])
            b = int(row[1])
            t = int(row[2])
            if str(t) in edges_a2q.keys() and (str(a), str(b)) in edges_a2q[str(t)]:
                user_dict[str(a)][t] = 'giving answer'
                user_dict[str(b)][t] = 'receiving answer'
            if str(t) in edges_c2q.keys() and (str(a), str(b)) in edges_c2q[str(t)]:
                user_dict[str(a)][t] = 'giving comment to question'
                user_dict[str(b)][t] = 'receiving comment for question'
            if str(t) in edges_c2a.keys() and (str(a), str(b)) in edges_c2a[str(t)]:
                user_dict[str(a)][t] = 'giving comment to answer'
                user_dict[str(b)][t] = 'receiving comment for answer'
    return user_dict


# Creates the interaction value dictionary for each user
# by aggregating the basic and the cumulative values
def calculate_interaction_model(user_dict):
    a = 8  # alpha parameter is the weight of the cumulative part
    weight_map = {'giving answer': 5,
                  'receiving answer': 3,
                  'giving comment to question': 1,
                  'receiving comment for question': 1.5,
                  'giving comment to answer': 1,
                  'receiving comment for answer': 1,
                  '': 0
                  }
    basic_dict = {}
    cumulative_dict = {}
    activity_dict = {}
    interactions_dict = {}
    for user, history in user_dict.items():
        last = 0
        for t, activity in dict(sorted(history.items())):
            if user not in activity_dict.keys():
                if activity != '':
                    last += 1
                activity_dict[user] = {t: last}
            else:
                if activity != '':
                    last += 1
                activity_dict[user][t] = last
    for user, history in user_dict.items():
        basic_dict[user] = {t: weight_map[activity] for t, activity in history.items()}
        cumulative_dict[user] = {t: 0 if act_weight == 0 else act_weight*a*(1-1/(activity_dict[user][t]+1))
                                 for t, act_weight in basic_dict[user].items()}
        interactions_dict[user] = {t: basic_dict[user][t]+cumulative_dict[user][t] for t in history.keys()}
    return interactions_dict


# Calculates the delta_n value of each user
# so that frequency of the interactions in a given time period are considered
def calculate_interval(user_dict):
    t_a = 86400  # 1 day time space is checked
    interval_dict = {}
    for user, history in user_dict.items():
        last_t = 0
        for t, activity in dict(sorted(history.items())):
            if user not in interval_dict.keys():
                interval_dict[user] = {t: 0}
            else:
                interval_dict[user][t] = (t-last_t)/t_a
            last_t = t
    return interval_dict


# Calculates the trust for each user per timestamp
# using the interaction and interval dictionaries
def calculate_trust(interactions_dict, interval_dict):
    beta = 0.88  # parameter to adjust the forgetting factor
    trust_dict = {}
    for user in interactions_dict.keys():
        trust_dict[user] = {0: 1}  # all users gain a trust of 1 in zero time
    for user, history in interactions_dict.items():
        last_t = 0
        for t, activity in dict(sorted(history.items())):
            trust_dict[user][t] = trust_dict[user][last_t]*beta**interval_dict[user][t]+interactions_dict[user][t]
            last_t = t
    return trust_dict

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
