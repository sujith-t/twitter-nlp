# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 16:15:43 2022

@author: sujith
"""

from reserved_words import contraction_map as cm
import re

from html.parser import HTMLParser


"""
# Main function that normalizes the text for feature study
# Only English text considered
"""

def normalize_text(texts: list):
    
    cleaned_txt = []
    html_parser = HTMLParser()
    
    for txt in texts:
        txt = html_parser.unescape(txt)
        txt = translate_contraction(txt)

"""
# Remove all contractions, contraction words taken from reserved words
# Only English text considered
"""

def translate_contraction(text: str):
    
    str_pattern = '({})'.format('|'.join(cm.keys()))
    regex_pattern = re.compile(str_pattern, flags = re.IGNORECASE | re.DOTALL)
    
    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded = cm.get(match)\
                                if cm.get(match)\
                                else cm.get(match.lower())                       
        expanded = first_char+expanded[1:]
        return expanded
        
    txt = regex_pattern.sub(expand_match, text)
    txt = re.sub("'", "", txt)
    return txt