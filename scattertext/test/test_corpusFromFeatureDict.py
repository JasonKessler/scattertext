from unittest import TestCase
import numpy as np
import pandas as pd

from scattertext import CorpusFromFeatureDict


class TestCorpusFromFeatureDict(TestCase):
	def test_build(self):
		df = pd.DataFrame([
			{
				'text': '''The President opened the speech by welcoming the Speaker, Vice President, Members of Congress, and fellow Americans. He noted that this was his eighth speech, and promised it would be shorter than usual, joking that he knew "some of you are antsy to get back to Iowa." He recognized people's generally low expectations for meaningful legislature due to 2016 being an election year, and thanked the House Speaker Paul Ryan for his help passing the budget and making tax cuts permanent for working families. He expressed hope that progress could be made on "bipartisan priorities like criminal justice reform, and helping people who are battling prescription drug abuse." He then listed proposals for the year ahead, per tradition. They included helping students learn to write computer code, personalizing medical treatments for patients, fixing the immigration system he called broken, protecting US children from gun violence, achieving equal pay for equal work in a nod towards gender equality, implementing paid leave, and raising the minimum wage.''',
				'feats': {'president': 3, 'he': 2},
				'category': '2016'},
			{
				'text': '''He then addressed the third question, how to ensure America's safety without either becoming isolationist or having to nation-build across the world. He highlighted the strength of the US military, and criticized those who claimed America was getting weaker as its enemies were getting stronger. He pointed out that failing states were the biggest threat to the US, not evil empires. He listed as his top priority "protecting the American people and going after terrorist networks." He discussed the threat of al Qaeda and ISIL, but pointed out that they did not threaten "our national existence," and dismissed claims otherwise as harmful propaganda. He then detailed the American and 60 country coalition efforts to defeat terrorism and to "cut off ISIL’s financing, disrupt their plots, stop the flow of terrorist fighters, and stamp out their vicious ideology. With nearly 10,000 air strikes, we are taking out their leadership, their oil, their training camps, and their weapons. We are training, arming, and supporting forces who are steadily reclaiming territory in Iraq and Syria."''',
				'feats': {'addressed': 5, 'he': 2},
				'category': '2016'},
			{
				'text': '''Senator Bernie Sanders of Vermont (an independent who caucuses with the Democrats in the Senate) responded to the speech in a 14-minute video posted to Facebook, in which he criticized Trump for failing to make any mention of income inequality, criminal justice reform, or climate change.[23] Sanders also stated: "President Trump once again made it clear he plans on working with Republicans in Congress who want to repeal the Affordable Care Act, throw 20 million Americans off of health insurance, privatize Medicare, make massive cuts in Medicaid, raise the cost of prescription drugs to seniors, eliminate funding for Planned Parenthood, while at the same time, he wants to give another massive tax break to the wealthiest Americans."[23]."''',
				'feats': {'medicare': 2, 'Trump': 3, 'senator bernie sanders': 8, 'he': 2},
				'category': '2017'
			},
			{
				'text': '''The 45th President of the United States, Donald Trump, gave his first public address before a joint session of the United States Congress on Tuesday, February 28, 2017. Similar to a State of the Union address, it was delivered before the 115th United States Congress in the Chamber of the United States House of Representatives in the United States Capitol.[6] Presiding over this joint session was the House Speaker, Paul Ryan. Accompanying the Speaker of the House was the President of the United States Senate, Mike Pence, the Vice President of the United States."''',
				'feats': {'trump': 9, 'president': 8, 'he': 2},
				'category': '2017'
			},
		])
		corpus = CorpusFromFeatureDict(
			df=df,
			category_col='category',
			text_col='text',
			feature_col='feats'
		).build()
		self.assertEquals(len(corpus.get_terms()), 7)
		self.assertEqual(len(corpus.get_categories()), 2)
		self.assertEqual(len(corpus.get_texts()), 4)
		self.assertEqual(corpus.get_texts()[0], df.text.iloc[0])
		self.assertEqual(corpus.get_texts()[3], df.text.iloc[3])
		self.assertFalse(np.array_equal(corpus._X[0,:], corpus._X[0,:]))
		corpus.get_df()


	def test_metadata(self):
		df = pd.DataFrame([
			{
				'text': '''The President opened the speech by welcoming the Speaker, Vice President, Members of Congress, and fellow Americans. He noted that this was his eighth speech, and promised it would be shorter than usual, joking that he knew "some of you are antsy to get back to Iowa." He recognized people's generally low expectations for meaningful legislature due to 2016 being an election year, and thanked the House Speaker Paul Ryan for his help passing the budget and making tax cuts permanent for working families. He expressed hope that progress could be made on "bipartisan priorities like criminal justice reform, and helping people who are battling prescription drug abuse." He then listed proposals for the year ahead, per tradition. They included helping students learn to write computer code, personalizing medical treatments for patients, fixing the immigration system he called broken, protecting US children from gun violence, achieving equal pay for equal work in a nod towards gender equality, implementing paid leave, and raising the minimum wage.''',
				'feats': {'president': 3, 'he': 2},
				'meta': {'word_count': 32},
				'category': '2016'},
			{
				'text': '''He then addressed the third question, how to ensure America's safety without either becoming isolationist or having to nation-build across the world. He highlighted the strength of the US military, and criticized those who claimed America was getting weaker as its enemies were getting stronger. He pointed out that failing states were the biggest threat to the US, not evil empires. He listed as his top priority "protecting the American people and going after terrorist networks." He discussed the threat of al Qaeda and ISIL, but pointed out that they did not threaten "our national existence," and dismissed claims otherwise as harmful propaganda. He then detailed the American and 60 country coalition efforts to defeat terrorism and to "cut off ISIL’s financing, disrupt their plots, stop the flow of terrorist fighters, and stamp out their vicious ideology. With nearly 10,000 air strikes, we are taking out their leadership, their oil, their training camps, and their weapons. We are training, arming, and supporting forces who are steadily reclaiming territory in Iraq and Syria."''',
				'feats': {'addressed': 5, 'he': 2},
				'meta': {'word_count': 44},
				'category': '2016'},
			{
				'text': '''Senator Bernie Sanders of Vermont (an independent who caucuses with the Democrats in the Senate) responded to the speech in a 14-minute video posted to Facebook, in which he criticized Trump for failing to make any mention of income inequality, criminal justice reform, or climate change.[23] Sanders also stated: "President Trump once again made it clear he plans on working with Republicans in Congress who want to repeal the Affordable Care Act, throw 20 million Americans off of health insurance, privatize Medicare, make massive cuts in Medicaid, raise the cost of prescription drugs to seniors, eliminate funding for Planned Parenthood, while at the same time, he wants to give another massive tax break to the wealthiest Americans."[23]."''',
				'feats': {'medicare': 2, 'Trump': 3, 'senator bernie sanders': 8, 'he': 2},
				'meta': {'word_count': 20},
				'category': '2017'
			},
			{
				'text': '''The 45th President of the United States, Donald Trump, gave his first public address before a joint session of the United States Congress on Tuesday, February 28, 2017. Similar to a State of the Union address, it was delivered before the 115th United States Congress in the Chamber of the United States House of Representatives in the United States Capitol.[6] Presiding over this joint session was the House Speaker, Paul Ryan. Accompanying the Speaker of the House was the President of the United States Senate, Mike Pence, the Vice President of the United States."''',
				'feats': {'trump': 9, 'president': 8, 'he': 2},
				'meta': {'word_count': 10},
				'category': '2017'
			},
		])
		corpus = CorpusFromFeatureDict(
			df=df,
			category_col='category',
			text_col='text',
			feature_col='feats',
			metadata_col='meta'
		).build()
		self.assertEquals(len(corpus.get_terms()), 7)
		self.assertEqual(len(corpus.get_categories()), 2)
		self.assertEqual(len(corpus.get_texts()), 4)
		self.assertEqual(corpus.get_texts()[0], df.text.iloc[0])
		self.assertEqual(corpus.get_texts()[3], df.text.iloc[3])
		self.assertFalse(np.array_equal(corpus._X[0,:], corpus._X[0,:]))
		expected = pd.DataFrame([{'term': 'word_count', '2016 freq': np.int32(76), '2017 freq': np.int32(30)}]).set_index('term').astype(np.int32)
		pd.testing.assert_frame_equal(corpus.get_metadata_freq_df(), expected)
