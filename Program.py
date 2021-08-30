# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 08:51:32 2021

@author: Adrian
"""

import pandas as pd
import re
import spacy
from spacy.training import Example
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from difflib import SequenceMatcher as SM
from nltk.util import ngrams
import codecs


#---------- FUNCTIONS ----------

#Converts csv dataframe into Spacy training format
def spacy_training_format(df):
    
    TRAIN_DATA = []    
    
    raw_address_list = df['raw_address'].to_list()
    split_list = df['POI/street'].str.split('/', n=1).to_list()
    
    
    for raw, split in zip(raw_address_list, split_list):
        
        #Temporary dict to be combined with raw address
        tempDict = {'entities': None}
        
        #Values for the 'entities' key in dict
        tempListOfTuple = []
        
        
        for index, element in enumerate(split):
            
            string = raw
            pattern = element
            if index == 0:
                label = 'POI'
            elif index == 1:
                label = 'STREET'
                
            if pattern == '':
                pass
            else:
                try:
                    
                    match = (re.search(pattern, string))
                    tempTuple = (match.start(), match.end(), label)
                    tempListOfTuple.append(tempTuple)
                except:
                    pass
        
        if len(tempListOfTuple) != 0:
            #Assign the list of tuple to the temporary dict    
            tempDict['entities'] = tempListOfTuple
            
            #Temporary tuple to be appended into the TRAIN_DATA list
            tempTuple = (raw, tempDict)
            
            #Appending the tuple to the train data list
            TRAIN_DATA.append(tempTuple)
        else:
            pass
    
    return TRAIN_DATA


#Saves the rejected words into a list
def incomplete_words_data(df):
    
    TRAIN_DATA = []
    
    raw_address_list = df['raw_address'].to_list()
    split_list = df['POI/street'].str.split('/', n=1).to_list()
    
    
    for raw, split in zip(raw_address_list, split_list):
        
        
        for index, element in enumerate(split):
            
            string = raw
            pattern = element
                
            if pattern == '':
                pass
            else:
                try:
                    match = (re.search(pattern, string))
                    match.start()
                    match.end()
                except:
                    tempList = (raw, split)
                    TRAIN_DATA.append(tempList)
                    continue
                
    return TRAIN_DATA    


#Create an output dataframe
def extract_poi_street(df, nlp):
    
    TEST_DATA = df['raw_address'].to_list()
    OUTPUT_DATA = []
    
    
    for i in TEST_DATA:
        test_text = i
        doc = nlp(test_text)
        poiFlag = False
        streetFlag = False
        tempString = '/'
        for ent in doc.ents:
            if ent.label_ == 'POI' and poiFlag == False:
                poiFlag = True
                tempString = ent.text + tempString
            elif ent.label_ == 'STREET' and streetFlag == False:
                streetFlag = True
                tempString = tempString + ent.text
            else:
                tempString = '/'
        OUTPUT_DATA.append(tempString.lower())
            
    output_df = pd.DataFrame(list(OUTPUT_DATA), columns=['POI/street'])
    output_df['id'] = output_df.index
    output_df = output_df[['id', 'POI/street']]
    
    return output_df

#Fuzzy string matching to return highest similarity substring
def fuzzy_find(needle, hay):
    needle_length  = len(needle.split())
    max_sim_val    = 0
    max_sim_string = u""
    
    for ngram in ngrams(hay.split(), needle_length + int(.2*needle_length)):
        hay_ngram = u" ".join(ngram)
        #similarity = SM(None, hay_ngram, needle).ratio() 
        similarity = fuzz.token_set_ratio(needle, hay_ngram)
        if similarity > max_sim_val:
            max_sim_val = similarity
            max_sim_string = hay_ngram
    
    max_sim_string = max_sim_string.lstrip('0123456789 ')
    
    return max_sim_string, max_sim_val


#Handle rejected words
def extract_rejected_word(rejected_list):
    
    raw_list = []
    poi_street_list = []
    
    for i in rejected_list:
        raw = i[0]
        
        poi = i[1][0]
        street = i[1][1]
        
        if poi != '' and street != '':
            
            matched = fuzzy_find(poi, raw)
            poi = matched
            matched = fuzzy_find(street, raw)
            street = matched
            if poi.endswith(','):
                poi = poi[:-1]
            if street.endswith(','):
                street = street[:-1]
            raw_list.append(raw)
            poi_street_list.append(poi + '/' + street)
            
        elif poi != '':
            matched = fuzzy_find(poi, raw)
            poi = matched
            if poi.endswith(','):
                poi = poi[:-1]
            raw_list.append(raw)
            poi_street_list.append(poi + '/' + street)
            
        elif street != '':
            matched = fuzzy_find(street, raw)
            street = matched
            if street.endswith(','):
                street = street[:-1]
            raw_list.append(raw)
            poi_street_list.append(poi + '/' + street)
    
    REJECTED_DF = pd.DataFrame(list(zip(raw_list, poi_street_list)), columns=['raw_address', 'POI/street'])
    return REJECTED_DF

#Make list of rejected poi and street
def rejected_poi_street(rejected_list):

    rejected_poi = []
    rejected_street = []
    rejected_poi_initials = []
    rejected_street_initials = []
    
    for i in rejected_list:
        if i[1][0] != '':
            split = i[1][0].split()
            if len(split) > 1:
                rejected_poi.append(i[1][0])
        if i[1][1] != '':
            split = i[1][1].split()
            if len(split) > 1:
                rejected_street.append(i[1][1])
            
    for i in rejected_poi:
        split = i.split()
        initials = [word[0] for word in split]
        initials = ''.join(initials)
        rejected_poi_initials.append(initials)
        
    for i in rejected_street:
        split = i.split()
        initials = [word[0] for word in split]
        initials = ''.join(initials)
        rejected_street_initials.append(initials)
                
    REJECTED_DF = pd.DataFrame(list(zip(rejected_poi, rejected_street, rejected_poi_initials, rejected_street_initials)), columns=['POI', 'STREET', 'poiIn', 'strIn'])
    
    return REJECTED_DF
                
    
def compare_words(str1, str2):
    
    if str1 != '':
        hi = str1.split()
        initials1 = [word[0] for word in hi]
        initials1 = ''.join(initials1)
        
        hi2 = str2.split()
        initials2 = [word[0] for word in hi2]
        initials2 = ''.join(initials2)
        
        test = fuzz.ratio(initials1, initials2)
        
        if test == 100:
            if len(initials1) == 1:
                val = 0
                try:
                    initials3 = str1[0:6]
                    initials4 = str2[0:6]
                    test2 = fuzz.ratio(initials3, initials4)
                    if test2 > 99:
                        str1 = str2
                except:
                    pass
            elif len(initials1) > len(initials2):
                word, val = fuzzy_find(str2, str1)
            else:
                word, val = fuzzy_find(str1, str2)
                
            if val > 60:
                try:
                    hi = word.split()
                    initials3 = [word[1:3] for word in hi]
                    initials3 = ''.join(initials3)
                    hi2 = str2.split()
                    initials4 = [word[1:3] for word in hi2]
                    initials4 = ''.join(initials4)
                    test3 = fuzz.ratio(initials3, initials4)
                    if test3 == 100:
                        str1 = str2
                except:
                    pass

    return str1


def correcting_incomplete_words(df, poi_list, street_list):
    
    OUTPUT_DATA = []
    
    split_list = df['POI/street'].str.split('/', n=1).to_list()
    
    for split in split_list:
        if split != '':
            if split[0] != '':
                for e in poi_list:
                    newWord = compare_words(split[0], e)
                    if split[0] != newWord:
                        poi_string = newWord
                        break
                    else:
                        poi_string = split[0]
            else:
                poi_string = ''
                
                
            if split[1] != '':
                for e in street_list:
                    newWord = compare_words(split[1], e)
                    if split[1] != newWord:
                        street_string = newWord
                        break
                    else:
                        street_string = split[1]
            else:
                street_string = ''
                        
        final_string = poi_string + '/' + street_string   
        OUTPUT_DATA.append(final_string.lower())
        
    output_df = pd.DataFrame(list(OUTPUT_DATA), columns=['POI/street'])
    output_df['id'] = output_df.index
    output_df = output_df[['id', 'POI/street']]
    
    return output_df

def correcting_test_data(df, poi_list, street_list):
    
    OUTPUT_DATA = []
    raw_list = df['raw_address'].to_list()
    
    for i in raw_list:
        
        newRaw = i
        rejected_list = poi_list + street_list
        
        for e in rejected_list:
            
            replacement, val = fuzzy_find(e, i)
            if val > 60:
                compare = compare_words(replacement, e)
                if replacement != compare:
                    newRaw = newRaw.replace(replacement, compare)
        
        for f in poi_list:
            
            replacement, val = fuzzy_find(f, i)
            if val > 60:
                compare = compare_words(replacement, f)
                if replacement != compare:
                    newRaw = newRaw.replace(replacement, compare)
            
        OUTPUT_DATA.append(newRaw)
        
    output_df = pd.DataFrame(list(OUTPUT_DATA), columns=['raw_address'])
    output_df['id'] = output_df.index
    output_df = output_df[['id', 'raw_address']]
    
    return output_df
            
            



#-------------------------------
#---------- NLP STUFF ----------
#-------------------------------

nlp = spacy.blank('en')
nlp.add_pipe('ner')
nlp.begin_training()

ner = nlp.get_pipe('ner')

LABEL1 = 'POI'
LABEL2 = 'STREET'
ner.add_label(LABEL1)
ner.add_label(LABEL2)

optimizer = nlp.resume_training()
move_names = list(ner.move_names)

pipe_exceptions = ['ner', 'trf_wordpiecer', 'trf_tok2vec']
other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]



#------------------------------
#---------- TRAINING ----------
#------------------------------
#(only needed when wanting to train the data,
# not needed to execute after training is complete.)

#df = pd.read_csv('train.csv')
#data = spacy_training_format(df)

# with nlp.disable_pipes(*other_pipes) :

#   sizes = compounding(1.0, 4.0, 1.001)
#   # Training for (1) iterations     
#   for itn in range(1):
#     # batch up the examples using spaCy's minibatch
#     batches = minibatch(data, size=sizes)
#     # dictionary to store losses
#     losses = {}
#     for batch in batches:
#         try:
#             examples = []
#             for text, annots in batch:
#                 examples.append(Example.from_dict(nlp.make_doc(text), annots))
#                 # Calling update() over the iteration
#             nlp.update(examples, sgd=optimizer, drop=0.35, losses=losses)
#             print("Losses", losses)
#         except:
#             pass





#--------------------------------------------------
#---------- LOADING MODEL FROM DIRECTORY ----------
#--------------------------------------------------

output_dir = 'MODEL1'

print("Loading from", output_dir)
nlp2 = spacy.load(output_dir)
assert nlp2.get_pipe("ner").move_names == move_names
ner2 = nlp2.get_pipe('ner')






#--------------------------------------------------
#------------------ MAIN CODE ---------------------
#--------------------------------------------------

test_df = pd.read_csv('cleaned_test.csv')
testing123 = test_df

#train_df = pd.read_csv('train.csv')
#train = train_df
#rejected_df = incomplete_words_data(train)

#testing1 = rejected_poi_street(rejected_df)

#duplicated_poi = testing1.groupby(['POI'], as_index=False).count()
#duplicated_street = testing1.groupby(['STREET'], as_index=False).count()

#poi_sorted = duplicated_poi.sort_values(by=['poiIn'], ascending=False)
#street_sorted = duplicated_street.sort_values(by=['strIn'], ascending=False)

#complete_poi = poi_sorted[0:100]
#complete_street = street_sorted[0:100]

#complete_poi_list = complete_poi['POI'].to_list()
#complete_street_list = complete_street['STREET'].to_list()

#new_test = correcting_incomplete_words(testing123, complete_poi_list, complete_street_list)

#new_test = correcting_test_data(testing123, complete_poi_list, complete_street_list)
output_df = extract_poi_street(test_df, nlp2)

print('Saving to csv...')
output_df.to_csv('output8.csv', index=False)
print('Successfully saved!')








