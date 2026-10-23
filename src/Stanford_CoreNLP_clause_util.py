#!/usr/bin/env Python
"""
Created on Fri Apr 26 15:16:10 2019

@author: chenjian
"""
# Edited by Julian Lucio Paredes 2025

import sys

import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_Python_packages(
    GUI_util.window, "Stanford_CoreNLP_clause_util", ["tkinter", "nltk"]
):
    sys.exit(0)

import tkinter.messagebox as mb

from nltk.tree import Tree


def constituent_spans(parsetree):
    """Return (spans, leaves) for one sentence's parse tree. spans holds (subtree, first leaf index, last leaf
    index) for every subtree, in the preorder of Tree.subtrees(); leaves is the sentence's tokens in order."""
    leaves = []
    spans = []

    def walk(node):
        entry = len(spans)
        spans.append(None)
        start = len(leaves)
        for child in node:
            if isinstance(child, str):
                leaves.append(child)
            else:
                walk(child)
        spans[entry] = (node, start, len(leaves) - 1)

    walk(parsetree)
    return spans, leaves


"""
param:
@parsetree: NLTK parsetree of a sentence
output:
@full_list: list of token-clausal TAG pair for that sentence
"""


# processing the parsetree of one sentence at a time
def clausal_info_extract(parsetree):
    # print("IN clausal_info_extract full_list 1",full_list)
    dict_ind = dict()
    clausal_tags = []
    # each constituent's span comes from its position in the tree; matching its words against the sentence put a
    # repeated phrase ('a dog ... a dog') at its first occurrence, and rescanned the sentence for every constituent
    spans, full_list = constituent_spans(parsetree)
    for subtree, start_idx, end_idx in spans:
        # should use dict_CLAUSALTAG from Stanford_CoreNLP_tags_util
        # Stanford_CoreNLP_tags_util.dict_CLAUSALTAG
        #     clause_list = ['S','SBAR', 'SBARQ', 'SQ', 'SINV', 'NP', 'VP', 'ADJP', 'ADVP', 'PP']
        if subtree.label() in [
            "ADJP",
            "ADVP",
            "CC",
            "PP",
            "PRP",
            "RB",
            "SBAR",
            "SQ",
            "SBARQ",
            "SINV",
            "S",
            "VP",
            "NP",
            "NNP",
        ]:
            # Save the label at the starting index for later use
            dict_ind[start_idx] = subtree.label()

            # Convert the subtree to a string and perform clean-up
            example = " ".join(full_list[start_idx : end_idx + 1])
            example = example.replace(" ,", ",")
            example = example.replace(" ;", ";")
            example = example.replace(" .", ".")
            example = example.replace(" ?", "?")
            example = example.replace(" !", "!")
            example = example.replace(" -RRB- ", " ")
            example = example.replace(" -LRB- ", " ")
            example = example.replace("  ", " ")

            # Append a tuple containing (the label, the string itself, (start infex, end index))
            clausal_tags.append((subtree.label(), example, (start_idx, end_idx)))

    # full_list is a double list
    for i, tok in enumerate(full_list):
        if i in dict_ind:
            # clausal_tags.append(dict_ind[i])
            full_list[i] = [dict_ind[i]]
        else:
            # full_list[i] = [0]
            full_list[i] = [""]
        # clausal_tags.append(tok)
    try:
        # print("IN clausal_info_extract full_list 2",full_list)
        # print('\n\nclausal_tags\n\n',str(clausal_tags))
        return full_list, clausal_tags
        # return full_list
    except:
        print("\nERROR IN PARSE-TREE\n", parsetree)
        mb.showwarning(
            title="ERROR IN PARSE-TREE",
            message="There was an error in parsing the tree of a sentence for the full_list displayed in command line.",
        )


"""

"""


# parse_tree_str: NLTK parsetree of a single sentence


def clausal_info_extract_from_string(parse_tree_str):
    try:
        parse_tree = Tree.fromstring(parse_tree_str)
        full_list, clausal_tags = clausal_info_extract(parse_tree)
        return full_list, clausal_tags
        # full_list = clausal_info_extract(parse_tree)
        # return full_list
    except:
        print("\nERROR IN NLTK PARSE-TREE\n", parse_tree_str, parse_tree.flatten())
        mb.showwarning(
            title="ERROR IN PARSE-TREE",
            message="There was an error in NLTK parsing of the sentence tree displayed in command line.\n\nSearch in your document for the words displayed in command line, edit your document for characters that may lead to this error, and try again.",
        )
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
        token_info = [token[key] for key in ["index", "word", "lemma", "pos", "ner"]]
        list_tokens.append(token_info)
    return list_tokens


def extract_dep_info(sent_info):
    list_tokens = []
    for token in sent_info:
        token_info = [token[key] for key in ["governor", "dep"]]
        list_tokens.append(token_info)
    return list_tokens


def merge_token_infos(first, second, third, forth):
    list_tokens = []
    for a, b, c, d in zip(first, second, third, forth):
        list_tokens.append(a + b + c + d)
    return list_tokens


#             0        1        2           3           4                       5              6      7      8       9
# key_toks = ['index','word','originalText','lemma','characterOffsetBegin','characterOffsetEnd','pos','ner','before','after']
#            10        11       12              13          14
# key_deps = ['dep','governor','governorGloss','dependent','dependentGloss']
#                15        16
# key_clausetree = ['word','ClausalTag']

key_toks = ["index", "word", "lemma", "pos", "ner"]
key_deps = ["governor", "dep"]
key_clausetree = ["ClausalTag"]
