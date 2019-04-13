import networkx as nx
import numpy as np
import itertools

## We define each S* motif as a directed graph in networkx
motifs = {
    'S1': nx.DiGraph([(1, 2), (2, 3)]),
    'S2': nx.DiGraph([(1, 2), (1, 3), (2, 3)]),
    'S3': nx.DiGraph([(1, 2), (2, 3), (3, 1)]),
    'S4': nx.DiGraph([(1, 2), (3, 2)]),
    'S5': nx.DiGraph([(1, 2), (1, 3)])
}


def mcounter(gr, mo=motifs):

    mcount = dict(zip(mo.keys(), list(map(int, np.zeros(len(mo))))))
    nodes = gr.nodes()

    # We use iterools.product to have all combinations of three nodes in the
    # original graph. Then we filter combinations with non-unique nodes, because
    # the motifs do not account for self-consumption.

    triplets = list(itertools.product(*[nodes, nodes, nodes]))
    triplets = [trip for trip in triplets if len(list(set(trip))) == 3]
    triplets = map(list, map(np.sort, triplets))
    u_triplets = []
    [u_triplets.append(trip) for trip in triplets if not u_triplets.count(trip)]

    # The for each each of the triplets, we (i) take its subgraph, and compare
    # it to all fo the possible motifs

    for trip in u_triplets:
        sub_gr = gr.subgraph(trip)
        mot_match = list(map(lambda mot_id: nx.is_isomorphic(sub_gr, mo[mot_id]), motifs.keys()))
        match_keys = [list(mo.keys())[i] for i in range(len(mo)) if mot_match[i]]
        if len(match_keys) == 1:
            mcount[match_keys[0]] += 1

    return mcount
