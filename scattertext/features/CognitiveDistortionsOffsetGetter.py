'''
All data from
Johan Bollen, Marijn ten Thij, Fritz Breithaupt, Alexander T. J. Barron, Lauren A. Rutter, Lorenzo Lorenzo-Luaces,
Marten Scheffer. Historical language records reveal a surge of cognitive distortions in recent decades.
Proceedings of the National Academy of Sciences Jul 2021, 118 (30) e2102061118; DOI: 10.1073/pnas.210206111
'''
from typing import Dict, List, Optional

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter


import flashtext

COGNITIVE_DISTORTIONS_DEFINITIONS = {
    'Catastrophizing': 'Exaggerating the importance of negative events',
    'Dichotomous Reasoning': 'Thinking that an inherently continuous situation can only fall into two categories',
    'Disqualifying the Positive': 'Unreasonably discounting positive experiences',
    'Emotional Reasoning': 'Thinking that something is true based on how one feels, '
                           'ignoring the evidence to the contrary',
    'Fortune-telling': 'Making predictions, usually negative ones, about the future',
    'Labeling and mislabeling': 'Labeling yourself or others while discounting evidence that '
                                'could lead to less disastrous conclusions',
    'Magnification and Minimization': 'Magnifying negative aspects or minimizing positive aspects',
    'Mental Filtering': 'Paying too much attention to negative details instead of the whole picture',
    'Mindreading': 'Believing you know what others are thinking',
    'Overgeneralizing': 'Making sweeping negative conclusions based on a few examples',
    'Personalizing': 'Believing others are behaving negatively because of oneself, '
                     'without considering more plausible or external explanations for behavior',
    'Should statements': 'Having a fixed idea on how you and/or others should behave'}

COGNITIVE_DISTORTIONS_LEXICON = {
    'Catastrophizing': [['will', 'fail'], ['will', 'go', 'wrong'], ['will', 'end'], ['will', 'be', 'impossible'],
                        ['will', 'not', 'happen'], ['will', 'be', 'terrible'], ['will', 'be', 'horrible'],
                        ['will', 'be', 'a', 'catastrophe,'], ['will', 'be', 'a', 'disaster'], ['will', 'never', 'end'],
                        ['will', 'not', 'end']],
    'Dichotomous Reasoning': [['only'], ['every'], ['everyone'], ['everybody'], ['everything'], ['everywhere'],
                              ['always'], ['perfect'], ['the', 'best'], ['all'], ['not', 'a', 'single'], ['no', 'one'],
                              ['nobody,'], ['nothing'], ['nowhere'], ['never'], ['worthless'], ['the', 'worst'],
                              ['neither'], ['nor'], ['either', 'or'], ['black', 'or', 'white'], ['ever']],
    'Disqualifying the Positive': [['great', 'but'], ['good', 'but'], ['OK', 'but'], ['not', 'that', 'great'],
                                   ['not', 'that', 'good'], ['it', 'was', 'not'], ['not', 'all', 'that'],
                                   ['fine', 'but'], ['acceptable', 'but'], ['great', 'yet,'], ['good', 'yet'],
                                   ['OK', 'yet'], ['fine', 'yet'], ['acceptable', 'yet']],
    'Emotional Reasoning': [['but', 'I', 'feel'], ['since', 'I', 'feel'], ['because', 'I', 'feel'],
                            ['but', 'it', 'feels'], ['since', 'it', 'feels'], ['because', 'it', 'feels'],
                            ['still', 'feels']],
    'Fortune-telling': [['I', 'will', 'not'], ['we', 'will', 'not'], ['you', 'will', 'not'], ['they', 'will', 'not'],
                        ['it', 'will', 'not'], ['that', 'will', 'not'], ['he', 'will', 'not'], ['she', 'will', 'not']],
    'Labeling and mislabeling': [['I', 'am', 'a'], ['he', 'is', 'a'], ['she', 'is', 'a'], ['they', 'are', 'a'],
                                 ['it', 'is', 'a'], ['that', 'is', 'a'], ['sucks', 'at'], ['suck', 'at'],
                                 ['I', 'never'], ['he', 'never'], ['she', 'never'], ['you', 'never'], ['we', 'never,'],
                                 ['they', 'never'], ['I', 'am', 'an'], ['he', 'is', 'an'], ['she', 'is', 'an'],
                                 ['they', 'are', 'an'], ['it', 'is', 'an'], ['that', 'is', 'an'], ['a', 'burden'],
                                 ['a', 'complete'], ['a', 'completely'], ['a', 'huge,'], ['a', 'loser'], ['a', 'major'],
                                 ['a', 'total'], ['a', 'totally'], ['a', 'weak'], ['an', 'absolute'], ['an', 'utter'],
                                 ['a', 'bad'], ['a', 'broken'], ['a', 'damaged'], ['a', 'helpless'], ['a', 'hopeless'],
                                 ['an', 'incompetent'], ['a', 'toxic'], ['an', 'ugly'], ['an', 'undesirable'],
                                 ['an', 'unlovable'], ['a', 'worthless'], ['a', 'horrible'], ['a', 'terrible']],
    'Magnification and Minimization': [['worst'], ['best'], ['not', 'important'], ['not', 'count'], ['not', 'matter'],
                                       ['no', 'matter'], ['the', 'only', 'thing'], ['the', 'one', 'thing']],
    'Mental Filtering': [['I', 'see', 'only'], ['all', 'I', 'see'], ['all', 'I', 'can', 'see'],
                         ['can', 'only', 'think'], ['nothing', 'good'], ['nothing', 'right'], ['completely', 'bad'],
                         ['completely', 'wrong'], ['only', 'the', 'bad'], ['only', 'the', 'worst'], ['if', 'I', 'just'],
                         ['if', 'I', 'only'], ['if', 'it', 'just'], ['if', 'it', 'only']],
    'Mindreading': [['everyone', 'believes'], ['everyone', 'knows'], ['everyone', 'thinks'],
                    ['everyone', 'will', 'believe'], ['everyone', 'will', 'know'], ['everyone', 'will', 'think,'],
                    ['nobody', 'believes'], ['nobody', 'knows'], ['nobody', 'thinks'], ['nobody', 'will', 'believe'],
                    ['nobody', 'will', 'know'], ['nobody', 'will', 'think'], ['he', 'believes,'], ['he', 'knows'],
                    ['he', 'thinks'], ['he', 'does', 'not', 'believe'], ['he', 'does', 'not', 'know'],
                    ['he', 'does', 'not', 'think'], ['he', 'will', 'believe'], ['he', 'will', 'know'],
                    ['he', 'will', 'think'], ['he', 'will', 'not', 'believe'], ['he', 'will', 'not', 'know'],
                    ['he', 'will', 'not', 'think'], ['she', 'believes'], ['she', 'knows'], ['she', 'thinks'],
                    ['she', 'does', 'not', 'believe,'], ['she', 'does', 'not', 'know'], ['she', 'does', 'not', 'think'],
                    ['she', 'will', 'believe'], ['she', 'will', 'know'], ['she', 'will', 'think'],
                    ['she', 'will', 'not', 'believe'], ['she', 'will', 'not', 'know'], ['she', 'will', 'not', 'think'],
                    ['they', 'believe'], ['they', 'know'], ['they', 'think'], ['they', 'do', 'not', 'believe'],
                    ['they', 'do', 'not', 'know'], ['they', 'do', 'not', 'think,'], ['they', 'will', 'believe'],
                    ['they', 'will', 'know'], ['they', 'will', 'think'], ['they', 'will', 'not', 'believe'],
                    ['they', 'will', 'not', 'know'], ['they', 'will', 'not', 'think'], ['we', 'believe'],
                    ['we', 'know'], ['we', 'think'], ['we', 'do', 'not', 'believe'], ['we', 'do', 'not', 'know'],
                    ['we', 'do', 'not', 'think'], ['we', 'will', 'believe'], ['we', 'will', 'know'],
                    ['we', 'will', 'think'], ['we', 'will', 'not', 'believe'], ['we', 'will', 'not', 'know'],
                    ['we', 'will', 'not', 'think'], ['you', 'believe'], ['you', 'know'], ['you', 'think'],
                    ['you', 'do', 'not', 'believe'], ['you', 'do', 'not', 'know,'], ['you', 'do', 'not', 'think'],
                    ['you', 'will', 'believe'], ['you', 'will', 'know'], ['you', 'will', 'think'],
                    ['you', 'will', 'not', 'believe'], ['you', 'will', 'not', 'know'], ['you', 'will', 'not', 'think']],
    'Overgeneralizing': [['all', 'of', 'the', 'time'], ['all', 'of', 'them'], ['all', 'the', 'time'],
                         ['always', 'happens'], ['always', 'like'], ['happens', 'every', 'time'], ['completely'],
                         ['no', 'one', 'ever,'], ['nobody', 'ever'], ['every', 'single', 'one', 'of', 'them'],
                         ['every', 'single', 'one', 'of', 'you'], ['I', 'always'], ['you', 'always'], ['he', 'always'],
                         ['she', 'always'], ['they', 'always'], ['I', 'am', 'always'], ['you', 'are', 'always'],
                         ['he', 'is', 'always'], ['she', 'is', 'always'], ['they', 'are', 'always']],
    'Personalizing': [['all', 'me'], ['all', 'my'], ['because', 'I'], ['because', 'my'], ['because', 'of', 'my'],
                      ['because', 'of', 'me'], ['I', 'am', 'responsible'], ['blame', 'me'], ['I', 'caused,'],
                      ['I', 'feel', 'responsible'], ['all', 'my', 'doing'], ['all', 'my', 'fault'], ['my', 'bad'],
                      ['my', 'responsibility']],
    'Should statements': [['should'], ['ought'], ['must'], ['have', 'to'], ['has', 'to']]}


class LexiconFeatAndOffsetGetter(FeatAndOffsetGetter):
    def __init__(
            self,
            lexicons: Dict[str, List[List[str]]],
            definitions: Optional[Dict[str, str]] = None,
            case_sensitive: bool = False
    ):
        '''
        :param lexicons: Dict[str, List[List[str]]], maps a topic name to its list of word sequences
        :param definitions, Optional[Dict[str, str]], maps topic name to an explanation.
        :param case_sensitive: bool, are word sequences case sensitive?
        '''
        self.definitions = definitions
        self.keyword_processor = flashtext.KeywordProcessor(case_sensitive)
        self.keyword_processor.add_keywords_from_dict({
            topic: [' '.join(term_sequence) for term_sequence in term_sequences]
            for topic, term_sequences in lexicons.items()
        })

    def get_term_offsets(self, doc):
        return []

    def get_metadata_offsets(self, doc):
        text = str(doc)
        offset_tokens = {}
        for topic, start_index, end_index in self.keyword_processor.extract_keywords(text, span_info=True):
            token_stats = offset_tokens.setdefault(topic, [0, []])
            token_stats[0] += 1
            token_stats[1].append((start_index, end_index))
        return list(offset_tokens.items())

    def get_definitions(self):
        return self.definitions


