import numpy as np
import networkx as nx

class TimeseriesToOrdinalPatternGraph:
    def __init__(self, w, tau, use_quantiles=False, Q=4):
        self.w = w
        self.tau = tau
        self.use_quantiles = use_quantiles
        self.Q = Q

    def embeddings(self, time_series):
        n = len(time_series)
        embedded_series = [time_series[i:i + self.w * self.tau:self.tau] for i in range(n - self.w * self.tau + 1)]
        return np.array(embedded_series)

    def ordinal_pattern(self, vector):
        if self.use_quantiles:
            quantiles = np.linspace(0, 1, self.Q + 1)[1:-1]
            thresholds = np.quantile(vector, quantiles)
            ranks = np.zeros(len(vector), dtype=int)
            for i, value in enumerate(vector):
                ranks[i] = np.sum(value > thresholds)
        else:
            indexed_vector = [(value, index) for index, value in enumerate(vector)]
            sorted_indexed_vector = sorted(indexed_vector, key=lambda x: x[0])
            ranks = [0] * len(vector)
            for rank, (value, index) in enumerate(sorted_indexed_vector):
                ranks[index] = rank
        return tuple(ranks)

    def to_graph(self, time_series):
        embedded_series = self.embeddings(time_series)
        ordinal_patterns = [self.ordinal_pattern(vec) for vec in embedded_series]

        G = nx.DiGraph()
        transitions = {}

        for i in range(len(ordinal_patterns) - 1):
            pattern = ordinal_patterns[i]
            next_pattern = ordinal_patterns[i + 1]
            if pattern not in G:
                G.add_node(pattern)
            if next_pattern not in G:
                G.add_node(next_pattern)
            if (pattern, next_pattern) not in transitions:
                transitions[(pattern, next_pattern)] = 0
            transitions[(pattern, next_pattern)] += 1

        for (start, end), weight in transitions.items():
            G.add_edge(start, end, weight=weight / len(ordinal_patterns))

        return G