import logging

#!/usr/bin/env Python
"""
Created on Fri Apr 26 15:16:10 2019

@author: chenjian
"""

from nltk.tree import Tree

logger = logging.getLogger(__name__)

"""
param:
    @flist: full token list
    @sublist: a subset of the full list, returned by NLTK parsetree.leaves() function

output:
    @ind_f: position of the sublist in the full_token_list
"""


def sublist_match(flist, sublist):
    comp_len = len(sublist)
    for _ind, _tok in enumerate(sublist):
        for ind_f, _tok_f in enumerate(flist):
            if sublist == flist[ind_f : ind_f + comp_len]:
                return ind_f


"""
param:
@parsetree: NLTK parsetree of a sentence
output:
@full_list: list of token-clausal TAG pair for that sentence
"""


def clausal_info_extract(parsetree):
    full_list = parsetree.leaves()
    dict_ind = dict()
    for subtree in parsetree.subtrees():
        if subtree.label() in ["SBAR", "SQ", "SBARQ", "SINV", "S", "VP", "NP"]:
            ind = sublist_match(full_list, subtree.leaves())
            dict_ind[ind] = subtree.label()
    for i, _tok in enumerate(full_list):
        if i in dict_ind:
            full_list[i] = [dict_ind[i]]
        else:
            full_list[i] = [0]
    try:
        return full_list
    except Exception:
        logger.info("\nERROR IN PARSE-TREE\n %s", parsetree)
        logger.info(
            "ERROR IN PARSE-TREE There was an error in parsing the tree of a sentence for the full_list displayed in command line."
        )


"""

"""
# parse_tree_str: NLTK parsetree of a single sentence


def clausal_info_extract_from_string(parse_tree_str):
    try:
        parse_tree = Tree.fromstring(parse_tree_str)
        return clausal_info_extract(parse_tree)
    except Exception:
        logger.info("\nERROR IN NLTK PARSE-TREE\n %s %s", parse_tree_str, parse_tree.flatten())
        logger.info(
            "ERROR IN PARSE-TREE There was an error in NLTK parsing of the sentence tree displayed in command line.\n\nSearch in your document for the words displayed in command line, edit your document for characters that may lead to this error, and try again."
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
#            10        11       12              13          14
#                15        16

key_toks = ["index", "word", "lemma", "pos", "ner"]
key_deps = ["governor", "dep"]
key_clausetree = ["ClausalTag"]
