import gzip
import json
import re
import pkgutil
import warnings
from typing import Optional, List, Dict, Callable

import spacy
from spacy.strings import StringStore

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter


class USASOffsetGetter(FeatAndOffsetGetter):
    def __init__(self,
                 nlp: Callable = None,
                 tier: Optional[int] = None):
        '''
        :param nlp: Optional[spacy.Language]
            spaCy model. By default, loads en_core_web_sm without ner. Model should be loaded without NER.
        :param tier: Optional[int]
            Subdivision according to https://ucrel.lancs.ac.uk/usas/Lancaster_visual/Frames_Lancaster.htm. By default,
            most detailed level. Range should be [1,3]
        '''
        warnings.warn(
            "Using this functionality triggers an Attribution-NonCommercial-ShareAlike 4.0 International "
            "(CC BY-NC-SA 4.0) license. Cite USAS as:\n"
            "Scott Piao, Paul Rayson, Dawn Archer, Francesca Bianchi, Carmen Dayrell, Mahmoud El-Haj, "
            "Ricardo-María Jiménez, Dawn Knight, Michal Kren, Laura Löfberg, Rao Muhammad Adeel Nawab, "
            "Jawad Shafi, Phoey Lee Teh and Olga Mudraya. 2016. Lexical Coverage Evaluation of Large-scale "
            "Multilingual Semantic Lexicons for Twelve Languages. In LREC."
        )
        """
        if patterns is None:
            patterns = self.__load_patterns()
        labels = set(pat['label'] for pat in patterns)
        label_to_name = {}
        for label in labels:
            label_str = label
            while label_str not in pattern_names and label_str:
                label_str = label_str[:-1]
            if level is not None:
                matches = [x for x in re.finditer(r'\d', label_str)]
                if len(matches) > level:
                    label_str = label_str[:matches[level].span()[0]]
                    while label_str not in pattern_names and label_str:
                        label_str = label_str[:-1]
            if not label_str or label_str not in pattern_names:
                print(label, label_str, 'not found')
            else:
                label_to_name[label] = pattern_names[label_str]
        self.stringstore = StringStore()

        for i in range(len(patterns)):
            maybe_label_to_use = label_to_name.get(patterns[i]['label'], None)
            if maybe_label_to_use is not None:
                patterns[i]['label'] = maybe_label_to_use
                self.stringstore.add(maybe_label_to_use)
                self.nlp.vocab.strings.add(maybe_label_to_use)
        self.ruler = self.nlp.add_pipe("entity_ruler")
        self.ruler.add_patterns(patterns)
        """
        if nlp is None:
            nlp = spacy.load('en_core_web_sm', disable=['ner'])
        self.nlp = nlp
        self.stringstore = StringStore()
        pattern_names = self.__load_pattern_names()
        patterns = json.loads(gzip.decompress(pkgutil.get_data('scattertext', 'data/enusaspats.json.gz')))
        labeled_patterns = []
        for pattern in patterns:
            display_label = self.__get_display_label_from_internal_label(pattern['label'], tier, pattern_names)
            if display_label is not None:
                self.stringstore.add(display_label)
                self.nlp.vocab.strings.add(display_label)
                labeled_patterns.append({'label': display_label, 'pattern': pattern['pattern']})

        self.ruler = self.nlp.add_pipe("entity_ruler")
        self.ruler.add_patterns(labeled_patterns)

    def __get_display_label_from_internal_label(self,
                                                label: str,
                                                level: Optional[int],
                                                pattern_names: Dict[str, str]) -> Optional[str]:
        while label not in pattern_names and label:
            label = label[:-1]
        if label:
            if level is not None:
                matches = [x for x in re.finditer(r'\d', label)]
                if len(matches) > level:
                    label = label[:matches[level].span()[0]]
                    while label not in pattern_names and label:
                        label = label[:-1]
            return pattern_names[label]


    def __load_pattern_names(self) -> Dict[str, str]:
        raw = gzip.decompress(
            pkgutil.get_data('scattertext', 'data/en_usas_subcategories.tsv.gz')
        ).decode('utf8')
        return {line.split('\t')[0].strip(): line.split('\t')[1]
                for line in raw.split('\n')[1:]
                if line.strip()}

    def __load_patterns(self) -> List[Dict]:
        return [
            json.loads(line.strip())
            for line in set(
                line.strip()
                for line in gzip.decompress(
                    pkgutil.get_data('scattertext', 'data/en_usas.jsonl.gz')
                ).decode('utf-8').split('\n')
            )
            if line.strip()
        ]

    def get_term_offsets(self, doc):
        return []

    def get_metadata_offsets(self, inputdoc: spacy.tokens.doc.Doc):
        newdoc = self.nlp(str(inputdoc))
        offset_tokens = {}
        for ent in newdoc.ents:
            token_stats = offset_tokens.setdefault(ent.label_, [0, []])
            token_stats[0] += 1
            start = ent[0].idx
            end = start + len(str(ent))
            token_stats[1].append((start, end))
        return list(offset_tokens.items())
