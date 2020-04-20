import numpy as np
import pandas as pd

class ComponentDiGraph(object):
    def __init__(self, orig_edge_df, id_node_df, node_df, edge_df, components):
        self.edge_df = edge_df
        self.orig_edge_df = orig_edge_df
        self.id_node_df = id_node_df
        self.node_df = node_df
        self.components = components

    def get_dot(self, component):
        # graph = '''digraph {\n node [fixedsize="true", fontname="'IBM Plex Sans'", height="0.0001", label="\n", margin="0", shape="plaintext", width="0.0001"];\n'''

        # graph = '''digraph  \n{\n graph [bb="0,0,1297.2,881.5", charset="latin1", outputorder="edgesfirst", overlap="prism"]\n node [fontname="'IBM Plex Sans'", fontsize=10] ;\n'''
        graph = '''digraph  \n{\n graph [charset="latin1", outputorder="edgesfirst", overlap="prism"]\n node [fontname="'IBM Plex Sans'", fontsize=10] ;\n'''
        mynode_df = self.id_node_df[self.id_node_df['Component'] == component]
        nodes = '\n'.join(mynode_df
                          .reset_index()
                          .apply(lambda x: '''"%s" [label="%s"] ;''' % (x['index'], x['name']), axis=1)
                          .values)
        edges = '\n'.join(self.edge_df[self.edge_df.Component == component].
                          apply(lambda x: '"%s" -> "%s" ;' % (x.source_id, x.target_id), axis=1).values)
        return graph + nodes + '\n\n' + edges + '\n}'

    def get_components_at_least_size(self, min_size):
        component_sizes = (pd.DataFrame({'component': self.components})
                           .reset_index()
                           .groupby('component')[['index']]
                           .apply(len)
                           .where(lambda x: x >= min_size).dropna())
        return np.array(component_sizes.sort_values(ascending=False).index)

    def get_node_to_component_dict(self):
        return self.id_node_df.set_index('name')['Component'].to_dict()

    def component_to_node_list_dict(self):
        return self.id_node_df.groupby('Component')['name'].apply(list).to_dict()