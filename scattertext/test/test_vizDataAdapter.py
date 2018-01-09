import json
from unittest import TestCase

from scattertext.viz import VizDataAdapter


PAYLOAD = {"info": {"not_category_name": "Republican", "category_name": "Democratic"},
	              "data": [{"y": 0.33763837638376387, "term": "crises", "ncat25k": 0,
	                        "cat25k": 1, "x": 0.0, "s": 0.878755930416447},
	                       {"y": 0.5, "term": "something else", "ncat25k": 0,
	                        "cat25k": 1, "x": 0.0,
	                        "s": 0.5}]}

def make_viz_data_adapter():
	return VizDataAdapter(PAYLOAD)


class TestVizDataAdapter(TestCase):
	def test_to_javascript(self):
		js_str = make_viz_data_adapter().to_javascript()
		self.assertEqual(js_str[:34], 'function getDataAndInfo() { return')
		self.assertEqual(js_str[-3:], '; }')
		json_str = js_str[34:-3]
		self.assertEqual(PAYLOAD, json.loads(json_str))

	def test_to_json(self):
		json_str = make_viz_data_adapter().to_json()
		self.assertEqual(PAYLOAD, json.loads(json_str))
