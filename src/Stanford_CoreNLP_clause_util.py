#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 15:16:10 2019

@author: chenjian
"""

import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_Python_packages(GUI_util.window,"Stanford_CoreNLP_clause_util",['tkinter','nltk']):
    sys.exit(0)

from nltk.tree import Tree
import tkinter.messagebox as mb

"""
param:
    @flist: full token list
    @sublist: a subset of the full list, returned by NLTK parsetree.leaves() function

output:
    @ind_f: position of the sublist in the full_token_list
"""
def sublist_match(flist,sublist):
    comp_len = len(sublist)
    for ind, tok in enumerate(sublist):
        for ind_f,tok_f in enumerate(flist):
            if sublist == flist[ind_f:ind_f+comp_len]:
                return ind_f
            

"""
param:
@parsetree: NLTK parsetree of a sentence
output:
@full_list: list of token-clausal TAG pair for that sentence
"""
def clausal_info_extract(parsetree):
    full_list = parsetree.leaves()
    # print("IN clausal_info_extract full_list 1",full_list)
    dict_ind = dict()
    for subtree in parsetree.subtrees():
        if subtree.label() in ['SBAR', 'SQ', 'SBARQ','SINV','S','VP','NP']:
            ind = sublist_match(full_list,subtree.leaves())
            dict_ind[ind] = subtree.label()
    for i, tok in enumerate(full_list):
        if i in dict_ind:
            full_list[i] = [dict_ind[i]]
        else:
            full_list[i] = [0]
    try:
        # print("IN clausal_info_extract full_list 2",full_list)
        return full_list
    except:
        print("\nERROR IN PARSE-TREE\n",parsetree)
        mb.showwarning(title='ERROR IN PARSE-TREE', message="There was an error in parsing the tree of a sentence for the full_list displayed in command line.")

"""

"""
# parse_tree_str: NLTK parsetree of a single sentence

def clausal_info_extract_from_string(parse_tree_str):
    try:
        parse_tree = Tree.fromstring(parse_tree_str)
        return clausal_info_extract(parse_tree)
    except:
        print("\nERROR IN NLTK PARSE-TREE\n",parse_tree_str,parse_tree.flatten())
        mb.showwarning(title='ERROR IN PARSE-TREE', message="There was an error in NLTK parsing of the sentence tree displayed in command line.\n\nSearch in your document for the words displayed in command line, edit your document for characters that may lead to this error, and try again.")
        return

# ______________________________________________________________________________________________________________________
# none of the following functions are used
"""
ID
parse
basicDependencies
enhancedDependencies
enhancedPlusPlusDependencies
entitymentions
tokens
"""
def extract_sent_info(sent_info):
    list_tokens = []
    for token in sent_info:
        token_deps = [token[key] for key in token]
        list_tokens.append(token_deps)
    return list_tokens

def extract_tok_info(sent_info):
    list_tokens = []
    for token in sent_info:
        token_info = [token[key] for key in ['index','word','lemma','pos','ner']]
        list_tokens.append(token_info)
    return list_tokens

def extract_dep_info(sent_info):
    list_tokens = []
    for token in sent_info:
        token_info = [token[key] for key in ['governor','dep']]
        list_tokens.append(token_info)
    return list_tokens


def merge_token_infos(first,second,third,forth):
    list_tokens = []
    for a,b,c,d in zip(first,second,third,forth):
        list_tokens.append(a+b+c+d)
    return list_tokens
#             0        1        2           3           4                       5              6      7      8       9
#key_toks = ['index','word','originalText','lemma','characterOffsetBegin','characterOffsetEnd','pos','ner','before','after']
#            10        11       12              13          14
#key_deps = ['dep','governor','governorGloss','dependent','dependentGloss']
#                15        16
#key_clausetree = ['word','ClausalTag']

key_toks = ['index','word','lemma','pos','ner']
key_deps = ['governor','dep']
key_clausetree = ['ClausalTag']
