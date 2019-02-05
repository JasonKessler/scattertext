from scattertext.diachronic.DiachronicVisualizer import DiachronicVisualizer


class BubbleDiachronicVisualization(DiachronicVisualizer):
	@staticmethod
	def visualize(display_df):
		viridis = ['#440154', '#472c7a', '#3b518b', '#2c718e', '#21908d', '#27ad81', '#5cc863', '#aadc32', '#fde725']
		import altair as alt
		return alt.Chart(display_df).mark_circle().encode(
			alt.X('variable'),
			alt.Y('term'),
			size='frequency',
			color=alt.Color('trending:Q', scale=alt.Scale(domain=(display_df.dropna().trending.min(),
			                                                      0,
			                                                      display_df.dropna().trending.max()),
			                                              range=[viridis[0], viridis[len(viridis) // 2], viridis[-1]]
			                                              )
			                ),
		)
