from typing import List, Dict, Tuple, Optional
import spacy
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class LanguagePattern:
    pattern_text: str
    pattern_type: str  # 'grammar', 'idiom', 'collocation'
    pos_sequence: List[str]  # Part of speech sequence
    morphology: Dict[str, str]  # Morphological features
    frequency: int = 1
    confidence: float = 0.5

class PatternRecognizer:
    def __init__(self):
        # Load language models for supported languages
        self.nlp_models = {
            'en': spacy.load('en_core_web_sm'),
            'xho': spacy.load('xx_ent_wiki_sm'),  # Multilingual model for Xhosa
            'zul': spacy.load('xx_ent_wiki_sm'),  # Multilingual model for Zulu
            'afr': spacy.load('xx_ent_wiki_sm'),  # Multilingual model for Afrikaans
        }
        
        self.min_pattern_freq = 3
        self.pattern_cache = defaultdict(int)

    def extract_patterns(self, text: str, lang: str) -> List[LanguagePattern]:
        """Extract linguistic patterns from text"""
        nlp = self.nlp_models.get(lang)
        if not nlp:
            raise ValueError(f"Language model not available for {lang}")

        doc = nlp(text)
        patterns = []

        # Extract grammatical patterns
        grammar_patterns = self._extract_grammar_patterns(doc)
        patterns.extend(grammar_patterns)

        # Extract collocations
        collocations = self._extract_collocations(doc)
        patterns.extend(collocations)

        # Extract potential idioms
        idioms = self._extract_idiom_candidates(doc)
        patterns.extend(idioms)

        return patterns

    def _extract_grammar_patterns(self, doc) -> List[LanguagePattern]:
        """Extract grammatical patterns from parsed text"""
        patterns = []
        
        # Extract POS tag sequences
        for sent in doc.sents:
            # Get POS sequence for sentence
            pos_seq = [token.pos_ for token in sent]
            
            # Look for verb phrases
            verb_phrases = self._find_verb_phrases(sent)
            for phrase in verb_phrases:
                pattern = LanguagePattern(
                    pattern_text=phrase.text,
                    pattern_type='grammar',
                    pos_sequence=[token.pos_ for token in phrase],
                    morphology=self._get_morphological_features(phrase)
                )
                patterns.append(pattern)

            # Look for noun phrases
            noun_phrases = self._find_noun_phrases(sent) 
            for phrase in noun_phrases:
                pattern = LanguagePattern(
                    pattern_text=phrase.text,
                    pattern_type='grammar',
                    pos_sequence=[token.pos_ for token in phrase],
                    morphology=self._get_morphological_features(phrase)
                )
                patterns.append(pattern)

        return patterns

    def _extract_collocations(self, doc) -> List[LanguagePattern]:
        """Extract word collocations that frequently appear together"""
        patterns = []
        
        # Look for adjacent word pairs
        for i in range(len(doc) - 1):
            if doc[i].is_alpha and doc[i+1].is_alpha:  # Only consider word pairs
                collocation = f"{doc[i].text} {doc[i+1].text}"
                
                # Track frequency in cache
                self.pattern_cache[collocation] += 1
                
                if self.pattern_cache[collocation] >= self.min_pattern_freq:
                    pattern = LanguagePattern(
                        pattern_text=collocation,
                        pattern_type='collocation',
                        pos_sequence=[doc[i].pos_, doc[i+1].pos_],
                        morphology={},
                        frequency=self.pattern_cache[collocation]
                    )
                    patterns.append(pattern)

        return patterns

    def _extract_idiom_candidates(self, doc) -> List[LanguagePattern]:
        """Extract potential idiomatic expressions"""
        patterns = []
        
        for sent in doc.sents:
            # Look for sequences that might be idioms
            # (e.g., figurative language, metaphors)
            for chunk in sent.noun_chunks:
                if self._is_potential_idiom(chunk):
                    pattern = LanguagePattern(
                        pattern_text=chunk.text,
                        pattern_type='idiom',
                        pos_sequence=[token.pos_ for token in chunk],
                        morphology={}
                    )
                    patterns.append(pattern)

        return patterns

    def _find_verb_phrases(self, sent) -> List:
        """Find verb phrases in a sentence"""
        verb_phrases = []
        for token in sent:
            if token.pos_ == 'VERB':
                # Get the full verb phrase including auxiliaries and particles
                phrase = [token]
                # Look for auxiliary verbs before the main verb
                head = token.head
                while head.pos_ == 'AUX' and head.dep_ == 'aux':
                    phrase.insert(0, head)
                    head = head.head
                # Look for particles after the verb
                for child in token.children:
                    if child.dep_ == 'prt':
                        phrase.append(child)
                verb_phrases.append(phrase)
        return verb_phrases

    def _find_noun_phrases(self, sent) -> List:
        """Find noun phrases in a sentence"""
        return list(sent.noun_chunks)

    def _get_morphological_features(self, tokens) -> Dict[str, str]:
        """Extract morphological features from tokens"""
        features = {}
        for token in tokens:
            for feature, value in token.morph.items():
                features[f"{token.pos_}_{feature}"] = value
        return features

    def _is_potential_idiom(self, chunk) -> bool:
        """Check if a chunk might be an idiomatic expression"""
        # Heuristics for identifying potential idioms:
        # 1. Contains metaphorical language
        # 2. Fixed expression that appears frequently
        # 3. Meaning can't be derived from individual words
        
        # Simple heuristic: check if the chunk appears frequently
        # and contains interesting word combinations
        text = chunk.text.lower()
        self.pattern_cache[text] += 1
        
        has_frequent_pattern = self.pattern_cache[text] >= self.min_pattern_freq
        has_interesting_combo = any(
            token.pos_ in ['VERB', 'NOUN', 'ADJ']
            for token in chunk
        )
        
        return has_frequent_pattern and has_interesting_combo