import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph._traversal import connected_components
from scattertext.graphs.ComponentDiGraph import ComponentDiGraph


class SimpleDiGraph(object):
    def __init__(self, orig_edge_df):
        self.orig_edge_df = orig_edge_df
        self.id_node_df = pd.DataFrame({'name': list(set(orig_edge_df.source.values)
                                                     | set(orig_edge_df.target.values))})
        self.node_df = self.id_node_df.reset_index().set_index('name')
        self.edge_df = pd.merge(
            pd.merge(
                self.orig_edge_df, self.node_df, left_on='source', right_index=True
            ).rename(columns={'index': 'source_id'}),
            self.node_df,
            left_on='target',
            right_index=True
        ).rename(columns={'index': 'target_id'})

    def make_component_digraph(self, graph_params, node_params):
        components = self.get_connected_components()
        return ComponentDiGraph(
            edge_df=self.edge_df.assign(Component=lambda df: components[df.source_id]),
            orig_edge_df=self.orig_edge_df.assign(Component=components[self.edge_df.source_id]),
            node_df=self.node_df.assign(Component=lambda df: components[df['index']]),
            id_node_df=self.id_node_df.assign(Component=lambda df: components[df.index]),
            components=components,
            graph_params=graph_params,
            node_params=node_params
        )

    def get_connected_subgraph_df(self):
        return pd.DataFrame({'component': self.get_connected_components(),
                             'nodes': self.node_df['index'].values,
                             'values': self.node_df.index}
                            ).groupby('component').agg(list).assign(
            size=lambda df: df.nodes.apply(len)
        ).sort_values(by='size', ascending=False).reset_index(drop=True)

    def get_connected_components(self):
        return connected_components(self.get_sparse_graph(), True)[1]

    def get_sparse_graph(self):
        return csr_matrix(
            (np.ones(len(self.edge_df)),
             (self.edge_df.source_id.values, self.edge_df.target_id.values)),
            shape=(len(self.node_df), len(self.node_df))
        )

    def limit_nodes(self, nodes):
        return SimpleDiGraph(self.edge_df[
                                 self.edge_df.target_id.isin(nodes) | self.edge_df.source_id.isin(nodes)
                                 ][['source', 'target']])
