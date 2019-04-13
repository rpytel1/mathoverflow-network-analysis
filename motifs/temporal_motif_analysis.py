import copy
from collections import Counter
import networkx as nx
import numpy as np


class Algorithm:
    counts = Counter()
    l = 3
    WEIGHT = 0.1
    motifs = {}

    def setup_motifs(self):
        s3 = nx.MultiDiGraph()
        s3.add_edge(1, 2)
        s3.add_edge(1, 3)
        s3.add_edge(1, 3)
        s2 = nx.MultiDiGraph()
        s2.add_edge(1,3)
        s2.add_edge(1,2)
        s2.add_edge(1,4)

        self.motifs = {
            'S3': s3,
            'S4': s2
        }

    def main_algorithm(self, edges, times, delta):
        self.setup_motifs()
        start = 1
        self.counts = Counter()

        for end in range(len(edges)):
            # print(end)
            while times[start] + delta < times[end]:
                self.decrement_count(edges[start])
                start += 1
            self.increment_count(edges[end])
        edges_list = [elem.edges() for elem in self.counts.keys()]
        print("Keys:" + str(len(self.counts.keys())))
        # values for which key has 3 edges
        key_list = [elem for elem in self.counts if len(elem.edges()) == 3]
        triple_motifs = 0

        for key in key_list:
            triple_motifs += self.counts[key]

        print("Motifs" + str(triple_motifs))
        return self.check_isomorphism(self.counts)

    def decrement_count(self, edge):
        self.counts[self.edge_to_di_graph(edge)] -= 1
        suffix_list = self.get_list_of_keys_sorted(self.l - 1)
        for suffix in suffix_list:
            if self.length(suffix) < self.l - 1:
                self.counts[self.concat(edge, suffix)] -= self.counts[suffix]
            else:
                break

    def increment_count(self, edge):
        prefix_list = self.get_list_of_keys_sorted(self.l)
        prefix_list.reverse()
        for prefix in prefix_list:
            if self.length(prefix) < self.l:
                self.counts[self.concat(edge, prefix)] += self.counts[prefix]
            else:
                break
        self.counts[self.edge_to_di_graph(edge)] += 1

    def concat(self, edge, graph):
        new_graph = copy.deepcopy(graph)
        new_graph.add_edge(edge[0], edge[1])

        match_keys = [key for key in self.counts.keys() if nx.is_isomorphic(new_graph, key)]
        if len(match_keys) > 0:
            return match_keys[0]

        return new_graph

    def edge_to_di_graph(self, edge):
        graph = nx.MultiDiGraph()
        graph.add_edge(edge[0], edge[1])

        match_keys = [key for key in self.counts.keys() if nx.is_isomorphic(graph, key)]
        if len(match_keys) > 0:
            return match_keys[0]

        return graph

    def check_isomorphism(self, graph_list):
        mcount = dict(zip(self.motifs.keys(), list(map(int, np.zeros(len(self.motifs))))))
        for graph in graph_list:
            if nx.is_isomorphic(graph, self.motifs['S3']):
                mcount['S3'] += 1
        return mcount

    def get_list_of_keys_sorted(self, limit):
        suffix_list = [elem for elem in self.counts.keys() if len(elem.edges) < limit]
        suffix_list.sort(key=lambda s: len(s.edges))
        return suffix_list

    @staticmethod
    def length(graph):
        return len(graph.edges)
