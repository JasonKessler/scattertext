from collections import Counter
from re import split
from sys import version_info

import pandas as pd

from scattertext.Common import GENERAL_INQUIRER_URL
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromGeneralInquirer(FeatsFromSpacyDoc):
    def __init__(self,
                 use_lemmas=False,
                 entity_types_to_censor=set(),
                 tag_types_to_censor=set(),
                 strip_final_period=False,
                 **kwargs):
        '''
        Parameters
        ----------
        empath_analyze_function: function (default=empath.Empath().analyze)
            Function that produces a dictionary mapping Empath categories to

        Other parameters from FeatsFromSpacyDoc.__init__
        '''
        self._lexicon_df = self._download_and_parse_general_inquirer()
        super(FeatsFromGeneralInquirer, self).__init__(use_lemmas,
                                                       entity_types_to_censor,
                                                       tag_types_to_censor,
                                                       strip_final_period)

    def _download_and_parse_general_inquirer(self):
        df = pd.read_csv(GENERAL_INQUIRER_URL, sep='\t')
        return (df.T[2:-4].apply(lambda x: list(df
                                                .Entry
                                                .apply(lambda x: x.split('#')[0])
                                                .loc[x.dropna().index]
                                                .drop_duplicates()
                                                .apply(str.lower)),
                                 axis=1)
                .apply(pd.Series)
                .stack()
                .reset_index()[['level_0', 0]]
                .rename(columns={'level_0': 'cat', 0: 'term'})
                .set_index('term'))

    def _analyze(self, doc):
        text_df = (pd.DataFrame(pd.Series(Counter(t for t in split(r"(\W)", doc.lower()) if t.strip())))
                   .join(self._lexicon_df)
                   .dropna()
                   .groupby('cat')
                   .sum()
                   )
        return text_df

    def get_definitions(self):
        '''
        These definitions are from http://apmc.newmdsx.com/CATA/block3/General%20Inquirer%20Categories.txt

        :return: dict
        '''
        return {
            'Positiv': '1,915 words of positive outlook. (It does not contain words for yes, which has been made a separate category of 20 entries.)',
            'Negativ': '2,291 words of negative outlook (not including the separate category no in the sense of refusal).',
            'Pstv': '1045 positive words, an earlier version of Positiv.',
            'Affil': 'A subset of 557 Pstv words are also tagged for indicating affiliation or supportiveness.',
            'Ngtv': '1160 negative words, an earlier version of Negativ.',
            'Hostile': 'A subset of Ngtv 833 words are also tagged Hostile for words indicating an attitude or concern with hostility or aggressiveness.',
            'Strong': '1902 words implying strength.',
            'Power': 'A subset of 689 Strong words indicating a concern with power, control or authority.',
            'Weak': '755 words implying weakness.',
            'Submit': 'A subset of 284 Weak words connoting submission to authority or power, dependence on others, vulnerability to others, or withdrawal.',
            'Active': '2045 words implying an active orientation.',
            'Passive': '911 words indicating a passive orientation',
            'Pleasur': '168 words indicating the enjoyment of a feeling, including words indicating confidence, interest and commitment.',
            'Pain': '254 words indicating suffering, lack of confidence, or commitment.',
            'Feel': '49 words describing particular feelings, including gratitude, apathy, and optimism, not those of pain or pleasure.',
            'Arousal': '166 words indicating excitation, aside from pleasures or pains, but including arousal of affiliation and hostility.',
            'EMOT': '311 words related to emotion that are used as a disambiguation category, but also available for general use.',
            'Virtue': '719 words indicating an assessment of moral approval or good fortune, especially from the perspective of middle-class society.',
            'Vice': '685 words indicating an assessment of moral disapproval or misfortune.',
            'Ovrst': '"Overstated", 696 words indicating emphasis in realms of speed, frequency, causality, inclusiveness, quantity or quasi-quantity, accuracy, validity, scope, size, clarity, exceptionality, intensity, likelihood, certainty and extremity.',
            'Undrst': '"Understated", 319 words indicating de-emphasis and caution in these realms.',
            'Academ': '153 words relating to academic, intellectual or educational matters, including the names of major fields of study.',
            'Doctrin': '217 words referring to organized systems of belief or knowledge, including those of applied knowledge, mystical beliefs, and arts that academics study.',
            'Econ@': '510 words of an economic, commercial, industrial, or business orientation, including roles, collectivities, acts, abstract ideas, and symbols, including references to money. Includes names of common commodities in business.',
            'Exch': '60 words concerned with buying, selling and trading.',
            'ECON': '502 words (269 in common with Econ@) that is used by the General Inquirer in disambiguating.',
            'Exprsv': '205 words associated with the arts, sports, and self-expression.',
            'Legal': '192 words relating to legal, judicial, or police matters.',
            'Milit': '88 words relating to military matters.',
            'Polit@': '263 words having a clear political character, including political roles, collectivities, acts, ideas, ideologies, and symbols.',
            'POLIT': 'broader category than Polit@ of 507 words that is used in disambiguation.',
            'Relig': '103 words pertaining to religious, metaphysical, supernatural or relevant philosophical matters.',
            'Role': '569 words referring to identifiable and standardized individual human behavior patterns, as used by sociologists.',
            'COLL': '191 words referring to all human collectivities (not animal). Used in disambiguation.',
            'Work': '261 words for socially defined ways for doing work.',
            'Ritual': '134 words for non-work social rituals.',
            'SocRel': '577 words for socially-defined interpersonal processes (formerly called "IntRel", for interpersonal relations).',
            'Race': '15 words (with important use of words senses) referring to racial or ethnic characteristics.',
            'Kin@': '50 terms denoting kinship.',
            'MALE': '56 words referring to men and social roles associated with men. (Also used as a marker in disambiguation)',
            'Female': '43 words referring to women and social roles associated with women.',
            #'NonAdlt': '25 words associated with infants through adolescents.',
            'HU': '795 general references to humans, including roles',
            'ANI': '72 references to animals, fish, birds, and insects, including their collectivities.',
            #'Place': 'category with 318 words subdivided',
            'Social': '111 words for created locations that typically provide for social interaction and occupy limited space',
            'Region': '61 words',
            'Route': '23 words',
            'Aquatic': '20 words',
            'Land': '63 words for places occurring in nature, such as desert or beach',
            'Sky': '34 words for all aerial conditions, natural vapors and objects in outer space',
            'Object': 'category with 661 words subdivided into',
            'Tool': '318 word for tools',
            'Food': '80 words for food',
            'Vehicle': '39 words for vehcile',
            'BldgPt': '46 words for buildings, rooms in buildings, and other building parts',
            'ComnObj': '104 words for the tools of communication',
            'NatObj': '61 words for natural objects including plants, minerals and other objects occurring in nature other than people or animals)',
            'BodyPt': 'a list of 80 parts of the body',
            'ComForm': '895 words relating to the form, format or media of the communication transaction.',
            'COM': '412 communications words used in disambiguation.',
            'Say': '4 words for say and tell.',
            'Need': '76 words related to the expression of need or intent.',
            'Goal': '53 names of end-states towards which muscular or mental striving is directed.',
            'Try': '70 words indicating activities taken to reach a goal, but not including words indicating that the goals have been achieved.',
            'Means': '244 words denoting objects, acts or methods utilized in attaining goals. Only 16 words overlap with Lasswell dictionary 77-word category MeansLw.',
            'Persist': '64 words indicating "stick to it" and endurance.',
            'Complet': '81 words indicating that goals have been achieved, apart from whether the action may continue. The termination of action is indicated by the category Finish.',
            'Fail': '137 words indicating that goals have not been achieved.',
            'NatrPro': '217 words for processes found in nature, birth to death.',
            'Begin': '56 words',
            'Vary': '98 words indicating change without connotation of increase, decrease, beginning or ending',
            'Increas': 'increase, 111 words',
            'Decreas': 'decrease, 82 words',
            'Finish': '87 words Terminiation action of completion',
            'Stay': '25 movement words relating to staying',
            'Rise': '25 movement words relating to rising',
            'Exert': '194 movement words relating to exertion',
            'Fetch': '79 words, includes carrying',
            'Travel': '209 words for all physical movement and travel from one place to another in a horizontal plane',
            'Fall': '42 words referring to falling movement',
            'Think': '81 words referring to the presence or absence of rational thought processes.',
            'Know': '348 words indicating awareness or unawareness, certainty or uncertainty, similarity or difference, generality or specificity, importance or unimportance, presence or absence, as well as components of mental classes, concepts or ideas.',
            'Causal': '112 words denoting presumption that occurrence of one phenomenon is necessarily preceded, accompanied or followed by the occurrence of another.',
            'Ought': '26 words indicating moral imperative.',
            'Perceiv': '192 words referring to the perceptual process of recognizing or identifying something by means of the senses.',
            'Compare': '21 words of comparison.',
            'Eval@': '205 words which imply judgment and evaluation, whether positive or negative, including means-ends judgments.',
            'Solve': '189 words (mostly verbs) referring to the mental processes associated with problem solving.',
            'Abs@': '185 words reflecting tendency to use abstract vocabulary. There is also an ABS category (276 words) used as a marker.',
            'Quality': '344 words indicating qualities or degrees of qualities which can be detected or measured by the human senses. Virtues and vices are separate.',
            'Quan': '314 words indicating the assessment of quantity, including the use of numbers. Numbers are also identified by the NUMBcategory (51 words) which in turn divides into ORDof 15 ordinal words and CARDfor 36 cardinal words.',
            'FREQ': '46 words indicating an assessment of frequency or pattern of recurrences, as well as words indicating an assessment of nonoccurrence or low frequency. (Also used in disambiguation)',
            'DIST': '19 words referring to distance and its measures. (Used in disambiguation)',
            'Time@': '273 words indicating a time consciousness, including when events take place and time taken in an action. Includes velocity words as well. There is also a more restrictive TIME category (75 words) used as a marker for disambiguation.',
            'Space': '302 words indicating a consciousness of location in space and spatial relationships. There are also two more specialized marker categories for disambiguation POS (35 words for position) and DIM (49 words for dimension).',
            #'Rel1': '36 words indicating a consciousness of abstract relationships between people, places, objects and ideas, apart from relations in space and time.',
            'COLOR': '21 words of color, used in disambiguation.',
            'Self': '7 pronouns referring to the singular self',
            'Our': '6 pronouns referring to the inclusive self ("we", etc.)',
            'You': '9 pronouns indicating another person is being addressed directly.',
            'Yes': '20 words directly indicating agreement, including word senses "of course", "to say the least", "all right".',
            'No': '7 words directly indicating disagreement, with the word "no" itself disambiguated to separately identify absence or negation.',
            'Negate': '217 words that refer to reversal or negation, including about 20 "dis" words, 40 "in" words, and 100 "un" words, as well as several senses of the word "no" itself; generally signals a downside view.',
            'Intrj': '42 words and includes exclamations as well as casual and slang references, words categorized "yes" and "no" such as "amen" or "nope", as well as other words like "damn" and "farewell".',
            'IAV': '1947 verbs giving an interpretative explanation of an action, such as "encourage, mislead, flatter".',
            'DAV': '540 straight descriptive verbs of an action or feature of an action, such as "run, walk, write, read".',
            'SV': '102 state verbs describing mental or emotional states. usually detached from specific observable events, such as "love, trust, abhor".',
            'IPadj': '117 adjectives referring to relations between people, such as "unkind, aloof, supportive".',
            'IndAdj': '637 adjectives describing people apart from their relations to one another, such as "thrifty, restless"',
            'PowGain': 'Power Gain, 65 words about power increasing',
            'PowLoss': 'Power Loss, 109 words of power decreasing.',
            'PowEnds': 'Power Ends, 30 words about the goals of the power process.',
            'PowAren': 'Power Arenas, 53 words referring to political places and environments except nation-states.',
            'PowCon': 'Power conflict, 228 words for ways of conflicting.',
            'PowCoop': 'Power cooperation, 118 words for ways of cooperating',
            'PowAuPt': 'Power authoritative participants, 134 words for individual and collective actors in power process',
            'PowPt': 'Power ordinary participants, 81 words for non-authoritative actors (such as followers) in the power process.',
            'PowDoct': 'Power doctrine, 42 words for recognized ideas about power relations and practices.',
            'PowAuth': 'Authoritative power, 79 words concerned with a tools or forms of invoking formal power.',
            'PowOth': 'Residual category of 332 power words not in other subcategories',
            'PowTot': '1,266 words for the whole domain',
            'RcEthic': 'Ethics, 151 words of values concerning the social order.',
            'RcRelig': 'Religion, 83 words that invoke transcendental, mystical or supernatural grounds for rectitude.',
            'RcGain': 'Rectitude gain, 30 words such as worship and forgiveness.',
            'RcLoss': 'Rectitude loss, 12 words such as sin and denounce.',
            'RcEnds': 'Rectitude ends, 33 words including heaven and the high-frequency word "ought".',
            'RcTot': 'Rectitude total, 310 words for the whole domain.',
            'RspGain': '26 words for the garnering of respect, such as congratulations',
            'RspLoss': '38 words for the losing of respect, such as shame.',
            'RspOth': '182 words regarding respect that are neither gain nor loss',
            'RspTot': '245 words in the domain.',
            'AffGain': '35 words for reaping affect.',
            'AffLoss': '11 words for affect loss and indifference',
            'AffPt': 'Affect participant, 55 words for friends and family.',
            'AffOth': '96 affect words not in other categories',
            'AffTot': '196 words in the affect domain',
            'WltPt': 'Wealth participant, 52 words for various roles in business and commerce.',
            'WltTran': 'Wealth transaction, 53 words for pursuit of wealth, such as buying and selling.',
            'WltOth': '271 wealth-related words not in the above, including economic domains and commodities.',
            'WltTot': '378 words in wealth domain.',
            'WlbGain': '37 various words related to a gain in well being.',
            'WlbLoss': '60 words related to a loss in a state of well being, including being upset.',
            'WlbPhys': '226 words connoting the physical aspects of well being, including its absence.',
            'WlbPsyc': '139 words connoting the psychological aspects of well being, including its absence.',
            'WlbPt': '27 roles that evoke a concern for well-being, including infants, doctors, and vacationers.',
            'WlbTot': '487 words in well-being domain.',
            'EnlGain': 'Enlightenment gain, 146 words likely to reflect a gain in enlightenment through thought, education, etc.',
            'EnlLoss': 'Enlightenment loss, 27 words reflecting misunderstanding, being misguided, or oversimplified.',
            'EnlEnds': 'Enlightenment ends, 18 words "denoting pursuit of intrinsic enlightenment ideas."',
            'EnlPt': 'Enlightenment participant, 61 words referring to roles in the secular enlightenment sphere.',
            'EnlOth': '585 other enlightenment words',
            'EnlTot': 'total of about 835 words',
            'SklAsth': 'Skill aesthetic, 35 words mostly of the arts',
            'SklPt': 'Skill participant, 64 words mainly about trades and professions.',
            'SklOth': '158 other skill-related words',
            'SklTot': '257 skill words in all.',
            'TrnGain': 'Transaction gain, 129 general words of accomplishment',
            'TrnLoss': 'Transaction loss, 113 general words of not accomplishing, but having setbacks instead.',
            'TranLw': '334 words of transaction or exchange in a broad sense, but not necessarily of gain or loss.',
            'MeansLw': 'The Lasswell Means category, 78 general words referring to means and utility or lack of same. Overlaps little with Means category.',
            'EndsLw': '270 words of desired or undesired ends or goals.',
            'ArenaLw': '34 words for settings, other than power related arenas in PowAren.',
            'PtLw': 'A list of 68 actors not otherwise defined by the dictionary.',
            'Nation': 'A list of 169 nations, which needs updating.',
            'Anomie': '30 words that usually show "a negation of value preference", nihilism, disappointment and futility.',
            'NegAff': '193 words of negative affect "denoting negative feelings and emotional rejection.',
            'PosAff': '126 words of positive affect "denoting positive feelings, acceptance, appreciation and emotional support."',
            'SureLw': '175 words indicating "a feeling of sureness, certainty and firmness."',
            'If': '132 words "denoting feelings of uncertainty, doubt and vagueness."',
            'NotLw': '25 words "that show the denial of one sort or another. "'}
            #'TimeSpc': '"a general space-time category" with 428 words,',
            #'FormLw': '368 words referring to formats, standards, tools and conventions of communication. almost entirely a subset of the 895 words in ConForm category'}

    def get_doc_metadata(self, doc, prefix=''):
        topic_counter = Counter()
        if version_info[0] >= 3:
            doc = str(doc)
        for topic_category, score in self._analyze(doc).to_dict()[0].items():
            topic_counter[prefix + topic_category] = int(score)
        return topic_counter

    def has_metadata_term_list(self):
        return True

    def get_top_model_term_lists(self):
        return self._lexicon_df.reset_index().groupby('cat')['term'].apply(list).to_dict()
