# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 16:15:43 2022

@author: sujith
"""

import re
import nltk
import string

from reserved_words import contraction_map as cm
from reserved_words import stopword_list as sl
from html.parser import HTMLParser
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

"""
# Main function that normalizes the text for feature study
# Only English text considered
"""


def normalize_text(texts: list, lemmatize=True, is_text_only=False):
    cleaned_txt = []
    html_parser = HTMLParser()

    for txt in texts:
        txt = html_parser.unescape(txt)
        txt = translate_contraction(txt)

        txt = text_lemmatize(txt) if lemmatize else txt.lower()

        # cleaning noise texts
        words = nltk.word_tokenize(txt)
        pattern = re.compile('[{}]'.format(re.escape(string.punctuation)))

        for w in words:
            # check if text only
            is_valid_text = not is_text_only or (is_text_only and re.search('[a-zA-Z]', w))
            # has any punctuation character
            has_punctuation = pattern.sub('', w) == ''
            # stop word list
            word_in_stopword_list = w not in sl
            if not has_punctuation and word_in_stopword_list and is_valid_text:
                cleaned_txt.append(pattern.sub('', w))

        return cleaned_txt


"""
# Remove all contractions, contraction words taken from reserved words
# Only English text considered
"""


def translate_contraction(text: str):
    str_pattern = '({})'.format('|'.join(cm.keys()))
    regex_pattern = re.compile(str_pattern, flags=re.IGNORECASE | re.DOTALL)

    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded = cm.get(match) \
            if cm.get(match) \
            else cm.get(match.lower())
        expanded = first_char + expanded[1:]
        return expanded

    txt = regex_pattern.sub(expand_match, text)
    txt = re.sub("'", "", txt)
    return txt


"""
# Pos tag texts
# English pos tagging
"""


def postag_text(text: str):
    words = nltk.word_tokenize(text)
    tagged_words = nltk.pos_tag(words)

    def to_tags(tag):
        if tag.startswith('J'):
            return wn.ADJ
        elif tag.startswith('V'):
            return wn.VERB
        elif tag.startswith('N'):
            return wn.NOUN
        elif tag.startswith('R'):
            return wn.ADV
        else:
            return None

    tagged_text = [(word.lower(), to_tags(pos_tag)) for word, pos_tag in tagged_words]
    return tagged_text


"""
# Text Lemmatizing
# English texts
"""


def text_lemmatize(text: str):
    wnl = WordNetLemmatizer()
    pos_tagged_text = postag_text(text)
    words = [wnl.lemmatize(word, pos_tag) if pos_tag else word for word, pos_tag in pos_tagged_text]

    return ' '.join(words)


"""
# Remove all unwanted words, chars
# English texts
"""


def remove_noise_text(text: str):
    words = nltk.word_tokenize(text)
    pattern = re.compile('[{}]'.format(re.escape(string.punctuation)))
    tokens = []

    for w in words:
        if not pattern.sub('', w) == '' and w not in sl:
            tokens.append(pattern.sub('', w))

    return tokens
