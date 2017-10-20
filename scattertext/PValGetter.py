import pandas as pd


def get_p_vals(df, positive_category, term_significance):
	'''
	Parameters
	----------
	df : A data frame from, e.g., get_term_freq_df : pd.DataFrame
	positive_category : str
		The positive category name.
	term_significance : TermSignificance
		A TermSignificance instance from which to extract p-values.
	'''
	df_pos = df[[positive_category]]
	df_pos.columns = ['pos']
	df_neg = pd.DataFrame(df[[c for c in df.columns if
	                          c != positive_category
	                          and c.endswith(' freq')]].sum(axis=1))
	df_neg.columns = ['neg']
	X = df_pos.join(df_neg)[['pos','neg']].values
	return term_significance.get_p_vals(X)
