import pkgutil


class InvalidProtocolException(Exception):
	pass


class HTMLVisualizationAssembly:
	def __init__(self, visualization_data):
		'''
		:param visualization_data: VisualizationData
		'''
		self._visualization_data = visualization_data

	def to_html(self, protocol='http'):
		if protocol not in ('https', 'http'):
			raise InvalidProtocolException("Invalid protocol: '" + protocol + "'.  Protocol must be either http or https.")
		html_file = pkgutil.get_data('scattertext',
		                             'data/viz/scattertext.html').decode('utf-8')
		scripts = '\n'.join([pkgutil.get_data('scattertext',
		                                      'data/viz/scripts/' + script_name).decode('utf-8')
		                     for script_name in ['range-tree.js',
		                                         'main.js']])
		viz_data_in_javascript_command_form = self._visualization_data.to_javascript()
		scripts += '\n' + viz_data_in_javascript_command_form
		html_file = (html_file
		             .replace('<!-- INSERT SCRIPT -->', scripts, 1)
		             .replace('http://', protocol + '://'))
		return html_file
