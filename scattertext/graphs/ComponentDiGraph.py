import numpy as np
import pandas as pd

DEFAULT_GRAPH_PARAMS = {
    'charset': "latin1",
    'outputorder': "edgesfirst",
    'overlap': "prism"
}

DEFAULT_NODE_PARAMS = {
    'fontname': "'IBM Plex Sans'",
    'fontsize': 10
}


class ComponentDiGraph(object):
    def __init__(self, orig_edge_df, id_node_df, node_df, edge_df, components, graph_params=None, node_params=None):
        self.edge_df = edge_df
        self.orig_edge_df = orig_edge_df
        self.id_node_df = id_node_df
        self.node_df = node_df
        self.components = components
        self.graph_params = DEFAULT_GRAPH_PARAMS
        if graph_params is not None:
            for k, v in graph_params.items():
                self.graph_params[k] = v
        self.node_params = DEFAULT_NODE_PARAMS
        if node_params is not None:
            for k, v in node_params.items():
                self.node_params[k] = v

    def get_dot(self, component):
        # graph = '''digraph {\n node [fixedsize="true", fontname="'IBM Plex Sans'", height="0.0001", label="\n", margin="0", shape="plaintext", width="0.0001"];\n'''

        # graph = '''digraph  \n{\n graph [bb="0,0,1297.2,881.5", charset="latin1", outputorder="edgesfirst", overlap="prism"]\n node [fontname="'IBM Plex Sans'", fontsize=10] ;\n'''
        graph = '''digraph  \n{\n graph [%s]\n node [%s] ;\n''' % (
            self._format_graphviz_paramters(self.graph_params),
            self._format_graphviz_paramters(self.node_params)
        )

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

    def _format_graphviz_paramters(self, params):
        return ', '.join([k + '=' + ('"' if type(v) == str else '') + str(v) + ('"' if type(v) == str else '')
                          for k, v in params.items()])
