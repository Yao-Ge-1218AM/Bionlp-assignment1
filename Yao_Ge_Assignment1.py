import json
import string

import nltk
from fuzzywuzzy import fuzz
from nltk.stem import *
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import operator
from collections import defaultdict
import os
import numpy as np

import re
import xlrd

import xlwt

import pandas as pd

def load_dict_from_file(filepath):
    symptom_dict = {}
    with open(filepath, 'r') as dict_file:
            for line in dict_file:
                #print(line)
                (key1, value, key) = line.strip().split('\t')
                symptom_dict[key] = value

    return symptom_dict

def get_key (dict, value):
    return [v for k, v in dict.items() if k == value]

#symptom_dict = load_dict_from_file('E:/phd in emory/BioNLP/COVID-Twitter-Symptom-Lexicon.txt')
symptom_dict = load_dict_from_file('./COVID-Twitter-Symptom-Lexicon.txt')

import pandas as pd
def xlsx_to_csv_pd():
    #data_xls = pd.read_excel('E:/phd in emory/BioNLP/Assignment1GoldStandardSet.xlsx', index_col=0)
    #data_xls.to_csv('E:/phd in emory/BioNLP/Assignment1GoldStandardSet.csv', encoding='utf-8')
    #data_xls = pd.read_excel('E:/phd in emory/BioNLP/s6_annotaion.xlsx', index_col=0)
    #data_xls.to_csv('E:/phd in emory/BioNLP/s6_annotaion.csv', encoding='utf-8')
    data_xls = pd.read_excel('./s6_annotaion.xlsx', index_col=0)
    data_xls.to_csv('./s6_annotaion.csv', encoding='utf-8')

xlsx_to_csv_pd()

#infile = open('E:/phd in emory/BioNLP/Assignment1GoldStandardSet.csv','r',encoding='utf8')
#neg_file = open('E:/phd in emory/BioNLP/neg_trigs.txt','r',encoding='utf8')
infile = open('./Assignment1GoldStandardSet.csv','r',encoding='utf8')
neg_file = open('./neg_trigs.txt','r',encoding='utf8')
#text = infile.read()
neg_text = neg_file.read()
#sentences = sent_tokenize(text)
import csv
reader = csv.reader(infile)

column = [row[1] for row in reader]
print(column)
infile.seek(0)
id = [row[0] for row in reader]
print(id)


expressions = []
for key,value in symptom_dict.items():
    #print(key)
    expressions.append(key)

#print(expressions)

"""for i in range(1,len(column)):
    #print(column[i])
    text = column[i]

    for exp in expressions:
        if re.search(exp,text):
            #print ('i: ', i, 'found!! -> ', exp)
            print(exp, len(exp.split()))"""

import itertools


def run_sliding_window_through_text(words, window_size):
    # Generate a window sliding through a sequence of words

    word_iterator = iter(words)  # creates an object which can be iterated one element at a time
    word_window = tuple(itertools.islice(word_iterator,
                                         window_size))  # islice() makes an iterator that returns selected elements from the the word_iterator
    yield word_window
    # now to move the window forward, one word at a time
    for w in word_iterator:
        word_window = word_window[1:] + (w,)
        yield word_window

def match_dict_similarity(text, expressions,CUI_list):
    '''
    :param text:
    :param expressions:
    :return:
    '''
    threshold = 85
    max_similarity_obtained = -1
    best_match = ''
    #go through each expression
    for exp in expressions:
        #create the window size equal to the number of word in the expression in the lexicon
        size_of_window = len(exp.split())
        tokenized_text = list(nltk.word_tokenize(text))
        #print(tokenized_text)
        #print(tokenized_text[0+size_of_window])
        index = 0
        neg_flag = 0
        for window in run_sliding_window_through_text(tokenized_text, size_of_window):
            window_string = ' '.join(window)
            index += 1

            similarity_score = fuzz.ratio(window_string, exp)

            if similarity_score >= threshold:
                #index = i
                #print(index,tokenized_text[index-1])
                #print(sent)
                if(index >=4):
                    for w in neg_list:
                        if(tokenized_text[index-2]==w or tokenized_text[index-3]==w or tokenized_text[index-4]==w):
                            print(tokenized_text[index-2],tokenized_text[index-3],tokenized_text[index-4])
                            if(tokenized_text[index-1]!=',' and tokenized_text[index-1]!='.'):
                                print(index, text, get_key(symptom_dict, exp), exp, '-neg')
                                CUI_list.append([get_key(symptom_dict, exp)[0],1])
                                neg_flag =1
                               #continue
                if(index==2):
                    for w in neg_list:
                        if(tokenized_text[index-1]==w):
                            print(text, get_key(symptom_dict, exp), exp, '-neg')
                            CUI_list.append([get_key(symptom_dict, exp)[0],1])
                            neg_flag =1
                            #continue

                if(index==3):
                    for w in neg_list:
                        if(tokenized_text[index-1]==w or tokenized_text[index-2]==w):
                            if (tokenized_text[index - 1] != ',' and tokenized_text[index - 1] != '.'):
                                print(text, get_key(symptom_dict, exp), exp, '-neg')
                                CUI_list.append([get_key(symptom_dict, exp)[0],1])
                                neg_flag = 1
                                #continue
                if(neg_flag==0):
                    print(text, get_key(symptom_dict, exp)[0], exp)
                    CUI_list.append([get_key(symptom_dict, exp)[0],0])
    #print (text, max_similarity_obtained)

neg_list = neg_text.split('\n')
#print(neg_list)
neg_flag = 0
workbook = xlwt.Workbook(encoding='utf-8')
booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
booksheet.write(0, 0, 'ID')
booksheet.write(0, 1, 'Symptom CUIs')
booksheet.write(0, 2, 'Negation Flag')
for i in range(1,len(column)):  #len(column)
    #print(id[i])
    #print(column[i])
    text = column[i]
    sentences = sent_tokenize(text.lower())
    CUI_list = []
    for sent in sentences:
        match_dict_similarity(sent,expressions,CUI_list)
    print(CUI_list)
    df = pd.DataFrame(CUI_list,
                      columns=['cui', 'neg'])
    #print(df)
    df = df.drop_duplicates(['cui','neg'],keep="first")
    df = df.reset_index(drop=True)
    #print(df)
    booksheet.write(i, 0, id[i])
    #booksheet.write(i-1, 1, 38)
    #booksheet.write(i-1, 2, 38)
    str_cui = '$$$'
    for j in range(len(df)):
        str_cui += str(df['cui'][j]) + '$$$'
    #print(str_cui)
    str_neg = '$$$'
    for k in range(len(df)):
        str_neg += str(df['neg'][k]) + '$$$'
    #print(str_neg)
    #print(df['cui'][0])
    booksheet.write(i, 1, str_cui)
    booksheet.write(i, 2, str_neg)

#workbook.save('E:/phd in emory/BioNLP/submission4.xlsx')
workbook.save('./Submission.xlsx')