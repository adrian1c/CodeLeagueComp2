# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:20:26 2021

@author: Adrian
"""


# Extract rejected train data
# Append long form words into raw_address of rejected data
# Train model with long form address

needle = 'karyawan novotel hotel batam (kopkar novo)'
hay = 'duy, kary novo hotel batam (kop novo), lubuk baja'

from difflib import SequenceMatcher as SM
from nltk.util import ngrams
import codecs
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def fuzzy_find(needle, hay):
    needle_length  = len(needle.split())
    max_sim_val    = 0
    max_sim_string = u""
    
    for ngram in ngrams(hay.split(), needle_length + int(.2*needle_length)):
        hay_ngram = u" ".join(ngram)
        #similarity = SM(None, hay_ngram, needle).ratio() 
        similarity = fuzz.token_set_ratio(hay_ngram, needle)
        
        if similarity > max_sim_val:
            max_sim_val = similarity
            max_sim_string = hay_ngram
    
    return max_sim_string

# replace = fuzzy_find(needle, hay)
# print(replace)

# # hay = hay.replace(replace, needle)
# # print(hay)

# testing = '214 Hello street 435 gif'

# testing = testing.lstrip('0123456789 ')
# print(testing)


def correcting_incomplete_words(df, rejected_word_list):
    
    OUTPUT_DATA = []
    
    split_list = df['POI/street'].str.split('/', n=1).to_list()
    
    for split in split_list:
        for i in split:
            str1 = i
            for e in rejected_word_list:
                str2 = e
                newWord = compare_words(str1, str2)
                print(newWord)
                OUTPUT_DATA.append(newWord)
                
    return OUTPUT_DATA
                
    
def compare_words(str1, str2):
    
    if str1 != '':
        hi = str1.split()
        initials1 = [word[0] for word in hi]
        initials1 = ''.join(initials1)
        
        hi2 = str2.split()
        initials2 = [word[0] for word in hi2]
        initials2 = ''.join(initials2)
        
        test = fuzz.ratio(initials1, initials2)
        print(test)
        print(len(initials1))
        
        if test >= 75:
            if len(initials1) > len(initials2):
                testing = fuzzy_find(str2, str1)
                try:
                    hi = testing.split()
                    initials3 = [word[1:3] for word in hi]
                    initials3 = ''.join(initials3)
                    print(initials3)
                    hi2 = str2.split()
                    initials4 = [word[1:3] for word in hi2]
                    initials4 = ''.join(initials4)
                    print(initials4)
                    test3 = fuzz.ratio(initials3, initials4)
                    print(test3)
                    if test3 > 85:
                        str1 = str2
                        print(str1)
                except:
                    pass
            else:
                testing = fuzzy_find(str1, str2)
                try:
                    hi = testing.split()
                    initials3 = [word[1:3] for word in hi]
                    initials3 = ''.join(initials3)
                    print(initials3)
                    hi2 = str2.split()
                    initials4 = [word[1:3] for word in hi2]
                    initials4 = ''.join(initials4)
                    print(initials4)
                    test3 = fuzz.ratio(initials3, initials4)
                    print(test3)
                    if test3 > 85:
                        str1 = str2
                        print(str1)
                except:
                    pass
                
    return str1


# str1 = 'hello nice'
# list1 = ['gtds ', 'asdf dsafke', 'fjdi fj', 'gde lfdsa']

# test = process.extractOne(str1, list1)
# print(test)

str1 = 'r.'
str1.split
print(len(str1.split()))













