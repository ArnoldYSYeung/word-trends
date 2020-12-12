"""
Pipeline help functions.

Name:   Arnold YS Yeung
Date:   2020-12-11
"""

import re


def get_words_from_file(file):
    """
    Get words from a file where each line is a word.
    """
    words = []
    f = open(file, 'r')
    for line in f.readlines():
        words.append(line[:-1])         #  [:-1] removes '.\n' and add '\.' (. is a special character)
    f.close()
    
    return words

def replace_punctuations(text, replacement=" "):
    """
    Replace punctuations in string with replacement.
    """
    return re.sub(r'[^0-9a-zA-Z]+', replacement, text)
    
def tokenize(text, sep=None, lower=True):
    """
    Tokenize a string.
    """    
    if sep is not None:    
        return [token.lower() for token in text.strip().split(sep)]
    return [token.lower() for token in text.strip().split()]

def remove_stop_words(tokens, stop_words=set()):
    """
    Remove all stop words (and tokens containing digits) from a list of tokens.
    """
    digits = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
    
    return [token for token in tokens if token not in stop_words 
            and not any(digit in token for digit in digits)]

def lemmatize(tokens):
    raise NotImplementedError()
    