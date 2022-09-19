# The Python 3 routine was written by Jian Chen, 12.12.2018
# modified by Jian Chen (January 2019)
# modified by Jack Hester (February 2019) and Roberto Franzosi (June and December 2019)
# ALL SEARCHES OCCUR WITHIN SENTENCES.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoNLL table_search_util",
                                          ['os', 'tkinter', 'enum', 'typing']) == False:
    sys.exit(0)

from enum import Enum
from typing import List
import tkinter as tk
import tkinter.messagebox as mb

import Stanford_CoreNLP_tags_util
import CoNLL_util
import IO_csv_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

noResults = "No results found matching your search criteria for your input CoNLL file. Please, try different search criteria.\n\nTypical reasons for this warning are:\n   1.  You are searching for a token/word not found in the FORM or LEMMA fields (e.g., 'child' in FORM when in fact FORM contains 'children', or 'children' in LEMMA when in fact LEMMA contains 'child'; the same would be true for the verbs 'running' in LEMMA instead of 'run');\n   2. you are searching for a token that is a noun (e.g., 'children'), but you select the POS value 'VB', i.e., verb, for the POSTAG of searched token."

filesToOpen = []  # Store all files that are to be opened once finished


# deep search
def find_children(sentence_children, ind_keyword, searchedCoNLLField):
    list_children = []
    list_children_index = []
    for ind, tok in enumerate(sentence_children):
        head_num = int(tok[5])
        if head_num == ind_keyword:
            token_index = int(tok[0])

            if searchedCoNLLField == "FORM":
                token_form = tok[1]
            else:
                token_form = tok[2]
            token_postag = tok[3]
            token_deprel = tok[6]
            list_children.append((token_form, token_postag, token_deprel))
            list_children_index.append(token_index)
    return list_children, list_children_index


# Chen
def deps_index(deps):
    """
    break the deps string and return indexes

    Parameters
    ----------
    deps: a string contains all dependencies "7:conj:and|11:conj:and"

    Returns
    -------
    deps_list: all the index in the deps
    """
    deps_str = deps.split("|")
    deps_list = []
    for dep in deps_str:
        deps_list.append(int(dep.split(":")[0]))
    return deps_list


# Chen
def search_deps(token_id_in_sentence, sentence, searchedCoNLLField):
    """
    search into enhanced dependency column

    Parameters
    ----------
    token_id_in_sentence
    sentence
    searchedCoNLLField

    Returns
    -------
    res: a list of ((head_form, head_postag, head_deprel), index)
    """
    try:
        token = sentence[int(token_id_in_sentence) - 1]
    except:
        mb.showwarning(title='CoNLL table error',
                       message="The records in the CoNLL table appear to be out of sequence, leading to computing errors. Please, make sure that you haven't tinkered with the file sorting the data by any columns other than RecordID.\n\nSort the data by RecordID (col. 9) and try again.")
        # sys.exit(0)
        return []
    if len(token[SearchField.DEPS.value]) == 0:
        return []

    res = []
    deps_list = deps_index(token[SearchField.DEPS.value])
    for index in deps_list:
        if index != token[SearchField.ID.value] and index != 0:
            if searchedCoNLLField == "FORM":
                head_form = sentence[index - 1][SearchField.FORM.value]  # form
            else:
                head_form = sentence[index - 1][SearchField.LEMMA.value]  # lemma
            head_postag = sentence[index - 1][SearchField.POSTAG.value]  # postag
            head_deprel = sentence[index - 1][SearchField.DEPREL.value]  # deprel
            res.append(((head_form, head_postag, head_deprel), index))
        elif index == 0:
            continue
        else:
            return res

    return res


# Chen
def search_governors(sentence, searchedCoNLLField, target, target_index_list):
    """
    find all words whose head is the target word

    Parameters
    ----------
    sentence
    searchedCoNLLField
    target
    target_index_list: a list of index, containing all target word

    Returns
    -------

    res [(('ate', 'VBD', 'conj:and'), 17))]
    """

    res = []
    for token in sentence:
        if token[SearchField.FORM.value] == target or token[SearchField.LEMMA.value] == target:  # skip the target word
            continue

        deps_list = deps_index(token[SearchField.DEPS.value])
        for index in deps_list:
            if index in target_index_list:
                target_index = index
                governor_index = token[SearchField.ID.value]
                governor_word = token[SearchField.FORM.value]
                res.append((governor_index, governor_word, target_index))
    return res


# Chen
def deep_search(related_list):
    #TODO: implement search for "conj".
    #      prevent infinite loop by adding a list.
    pass

def search_parsetree_loop_all_related(token_id_in_sentence, sentence, searchedCoNLLField):
    visited = []
    list_governor = []
    list_headnum = []
    token = sentence[int(token_id_in_sentence) - 1]
    head_num = int(token[5])

    while head_num != int(token[0]) and head_num != 0 and head_num not in visited:
        head_token = sentence[head_num - 1]
        if searchedCoNLLField == "FORM":
            head_form = head_token[1]
        else:
            head_form = head_token[2]
        head_postag = head_token[3]
        head_deprel = head_token[6]

        list_governor.append((head_form, head_postag, head_deprel))
        list_headnum.append(head_num)
        visited.append(head_num)

        head_num = int(head_token[5])

    # find children -- loop to end
    no_new_token = 0
    list_children, list_children_index = find_children(sentence, token_id_in_sentence, searchedCoNLLField)
    # print(list_children_index)
    while not no_new_token and len(list_children_index) != 0:

        list_temp_children = []
        list_temp_children_index = []

        for index in list_children_index:
            children, inds = find_children(sentence, index, searchedCoNLLField)
            list_temp_children += children
            list_temp_children_index += inds

        if len(list_temp_children_index) == 0:
            no_new_token = 1

        curr_visited = len(visited)

        for i, j in zip(list_temp_children, list_temp_children_index):

            if int(j) not in visited:
                visited.append(int(j))
                list_children.append(i)
                list_children_index.append(j)

        if len(visited) == curr_visited:
            no_new_token = 1

    return list_governor + list_children, list_headnum + list_children_index


# return all indices of the input word

"""

1. return the list of tokens related to the keyword

2. filter out all the co-occuring words with undesired postag, deprel

"""

"""
The 11 indexed items are created in the function search_CoNLL_table:
	item[0] form/lemma, item[1] postag, item[2] deprel, item[3] is_head, item[4] Document_ID, 
	item[5] Sentence_ID, item[6] Document, item[7] whole_sent, 
	item[8] keyword[1]/SEARCHED TOKEN, 
	item[9] keyword[3]/SEARCHED TOKEN POSTAG, 
	item[10] keyword[6]/'SEARCHED TOKEN DEPREL'))
"""


# Chen
def filter_list_by_pstage(keyword_list, kw_desired_postag='*'):
    if kw_desired_postag == '*':
        keyword_list = keyword_list
    elif kw_desired_postag == 'NN*':
        keyword_list = [keyword for keyword in keyword_list if
                        keyword[SearchField.POSTAG] in ['NN', 'NNS', 'NNP', 'NNPS']]
    elif kw_desired_postag == 'JJ*':
        keyword_list = [keyword for keyword in keyword_list if keyword[SearchField.POSTAG.value] in ['JJ', 'JJR', 'JJS']]
    elif kw_desired_postag == 'RB*':
        keyword_list = [keyword for keyword in keyword_list if keyword[SearchField.POSTAG.value] in ['RB', 'RBR', 'RBS', ]]
    elif kw_desired_postag == 'VB*':
        keyword_list = [keyword for keyword in keyword_list if
                        keyword[SearchField.POSTAG.value] in ['VB', 'VBN', 'VBG', 'VBZ', 'VBP', 'VBD']]
    else:
        keyword_list = [keyword for keyword in keyword_list if keyword[SearchField.POSTAG.value] == kw_desired_postag]

    return keyword_list


# Chen
def filter_list_by_deprel(keyword_list, kw_desired_deprel='*'):
    if kw_desired_deprel == '*':
        keyword_list = keyword_list
    else:
        keyword_list = [keyword for keyword in keyword_list if keyword[SearchField.DEPREL.value] == kw_desired_deprel]
    return keyword_list


# Chen
def filter_output_list(list_queried, related_token_DEPREL="*", Sentence_ID="*", related_token_POSTAG="*"):
    """
    filter the output list by related_token_DEPREL, Sentence_ID, and related_token_POSTAG
    Parameters
    ----------
    list_queried : [('the', 'DT', 'det', 2, '1', '1', file_path, whole_sentence, 'pig', 'NN', 'obj')]
    related_token_DEPREL
    Sentence_ID
    related_token_POSTAG

    Returns
    -------
    deprel_list_queried: a list of filtered output [('the', 'DT', 'det', 2, '1', '1', file_path, whole_sentence, 'pig', 'NN', 'obj')]
    """
    # filter the output list
    # print ("related_token_POSTAG " + related_token_POSTAG)
    if related_token_POSTAG == "*" and related_token_DEPREL == "*" and Sentence_ID == "*":
        return list_queried
    if "*" not in related_token_POSTAG:
        postag_list_queried = list(filter(lambda tok: tok[1] == related_token_POSTAG, list_queried))
    elif related_token_POSTAG == "NN*":
        postag_list_queried = [token for token in list_queried if token[1] in ['NN', 'NNS', 'NNP', 'NNPS']]
    elif related_token_POSTAG == 'JJ*':
        postag_list_queried = [token for token in list_queried if token[1] in ['JJ', 'JJR', 'JJS']]
    elif related_token_POSTAG == 'RB*':
        postag_list_queried = [token for token in list_queried if token[1] in ['RB', 'RBR', 'RBS']]
    # postag_list_queried = list(filter(lambda tok:tok[1] in ['RB','RBR','RBS'],list_queried))
    elif related_token_POSTAG == 'VB*':
        postag_list_queried = [token for token in list_queried if token[1] in ['VB', 'VBN', 'VBG', 'VBZ', 'VBP', 'VBD']]
    # postag_list_queried = list(filter(lambda tok:tok[1] in ['VB','VBN','VBG','VBZ','VBP','VBD'],list_queried))
    else:
        postag_list_queried = list_queried
    if "*" not in related_token_DEPREL:
        deprel_list_queried = list(filter(lambda tok: tok[2] == related_token_DEPREL, postag_list_queried))
    else:
        deprel_list_queried = postag_list_queried
    return deprel_list_queried


# Chen
def search_in_sentence(desired_form, sentence, __field__='FORM', kw_desired_postag='*', kw_desired_deprel='*'):
    """
    Search related words in the input sentence

    Parameters
    ----------
    desired_form: "pig"
    sentence: a list of all word token in the sentence
    __field__: SearchField , "FORM" "LEMMA"
    kw_desired_postag: postag for searched word
    kw_desired_deprel: postage for related word

    Returns
    -------
    list_indices_related_word: a list of (related word's index, is_head, target word token)
    """

    list_indices_related_word = []
    # compare term: form or lemma
    if __field__ == 'FORM':
        compare_term = 1  # field poistion of FORM in CoNLL
    else:
        compare_term = 2  # field poistion of LEMMA in CoNLL

    if desired_form == '*':
        keyword_list = sentence
        # in each sentence, obtain the keyword tokens
        keyword_list = filter_list_by_pstage(keyword_list, kw_desired_postag)
    else:
        # if desired form is not *, need to search governor word
        keyword_list = [keyword for keyword in sentence if keyword[compare_term] == desired_form]
        keyword_list = filter_list_by_pstage(keyword_list, kw_desired_postag)
        keyword_index_list = [int(word[0]) for word in keyword_list]
        targets_governors = search_governors(sentence, __field__, desired_form, keyword_index_list)

        for governor in targets_governors:
            # Return form of search governors: [(governor_index, governor_word, target_index)]
            list_indices_related_word.append((governor[0], 2, sentence[governor[2] - 1]))

    # TODO: confirm is_head
    for keyword in keyword_list:
        token_id = keyword[0]
        # search head
        # head, head_num = search_head(token_id, sentence, __field__)
        # search deps
        head_list = search_deps(token_id, sentence, __field__)
        if len(head_list) != 0:
            for head in head_list:
                list_indices_related_word.append((head[1], 1, keyword))

    return list_indices_related_word


class SearchType(Enum):
    match = 1
    starts_with = 2
    ends_with = 3
    contains = 4

    # Returns a list of types
    @staticmethod
    def list():
        return list(map(lambda c: c.name, SearchType))

    def satisfies(self, word: List[str], index, searched_term):
        return (self.value == 1 and word[index] == searched_term) or \
               (self.value == 2 and word[index].startswith(searched_term)) or \
               (self.value == 3 and word[index].endswith(searched_term)) or \
               (self.value == 4 and searched_term in word[index])


class SearchField(Enum):
    ID = 0
    FORM = 1
    LEMMA = 2
    POSTAG = 3
    NER = 4
    HEAD = 5
    DEPREL = 6
    DEPS = 7
    CLAUSAL_TAG = 8
    RECORD_ID = 9
    Sentence_ID = 10
    Document_ID = 11
    DOCUMENT = 12

    def get_index(self) -> int:
        return self.value

    # Returns a list of Fields
    @staticmethod
    def list():
        return list(map(lambda c: c.name, SearchField))


class CoNLLFilter:
    searched_term: str
    search_type: SearchType
    search_field: SearchField
    should_be_false: bool = False
    is_and: bool


def do_include_word(word: List[str], filters: List[CoNLLFilter]) -> bool:
    # Note: if the filter relationship is "AND", then the flag is true at start,
    # and changes to false whenever the condition does not meet. On the other hand,
    # if the filter relationship is "OR," then the flag is false at start, and changes
    # to true whenever the condition meets.
    do_include = filters[0].is_and
    is_and = do_include
    search_filter: CoNLLFilter
    for search_filter in filters:
        if search_filter.search_type.satisfies(word,
                                               search_filter.search_field.get_index(),
                                               search_filter.searched_term) ^ search_filter.should_be_false:
            # The condition is met.
            if not is_and:
                do_include = True
        else:
            # The condition is not met
            if is_and:
                do_include = False

    return do_include


def search_related_words3(sentence: dict, filters: List[CoNLLFilter]):
    list_indices_related_word = []
    # compare term: form or lemma
    search_filter: CoNLLFilter
    for word in sentence:
        if do_include_word(word, filters):
            list_indices_related_word.append(word)
    return list_indices_related_word


# Chen
def search_CoNLL_table(list_sentences, form_of_token, _field_='FORM', related_token_POSTAG="*",
                       related_token_DEPREL="*",
                       Sentence_ID="*", _tok_postag_='*', _tok_deprel_='*'):
    header = ["Searched Token/Word", "IF of Searched Token/Word", "POS Tag of Searched Token/Word", "DepRel of Searched Token/Word" , "Co-occurring Token/Word", " ID of Co-occurring Token/Word", "POS Tag of Co-occurring Token/Word", "DepRel of Co-occurring Token/Word", "Head ID", "Sentence ID", "Sentence", "Document ID", "Document"]
    list_queried = []
    deprel_list_queried = []
    for sent in list_sentences:
        # test
        whole_sent = ""
        for token in sent:
            whole_sent += token[1] + " "
        print(whole_sent)
        # test
        try:
            list_word_indices = search_in_sentence(form_of_token, sent, _field_, _tok_postag_, _tok_deprel_)
        except:
            mb.showwarning(title='CoNLL table error',
                           message="The records in the CoNLL table appear to be out of sequence, leading to computing "
                                   "errors. Please, make sure that you haven't tinkered with the file sorting the data "
                                   "by any columns other than RecordID.\n\nSort the data by RecordID (col. 9) and try "
                                   "again.")
            # sys.exit(0)
            return deprel_list_queried
        # if return is null, continue
        if not list_word_indices:
            continue
        # obtain the full sentence
        whole_sent = ""
        for token in sent:
            whole_sent += token[1] + " "
        whole_sent = whole_sent.strip()
        for node in list_word_indices:
            co_token_ID = node[0]
            is_head = node[1]
            keyword = node[2]
            searched_token_ID = keyword[0]
            row = sent[int(co_token_ID) - 1]
            if _field_ == 'FORM':
                tok_form = row[1]
            else: # LEMMA
                tok_form = row[2]
            tok_postag = row[3]
            tok_deprel = row[6]
            tok_Sentence_ID = row[10]
            tok_Document_ID = row[11]
            tok_Document = row[12]
            # TODO what is token_id?
            token_id = str(tok_Document_ID)[:-2] + str("-" + tok_Sentence_ID)

            if _field_ == "FORM":
                searched_keyword = keyword[1]
            else:
                searched_keyword = keyword[2]
            list_queried.append((searched_keyword, searched_token_ID, keyword[3], keyword[6], tok_form, co_token_ID, tok_postag,
                                 tok_deprel, is_head,
                                 tok_Sentence_ID, whole_sent, tok_Document_ID,
                                 tok_Document
                                 ))
    list_queried.insert(0,header)

    # filter the output list
    deprel_list_queried = filter_output_list(list_queried, related_token_DEPREL, Sentence_ID, related_token_POSTAG)

    return deprel_list_queried


def search_conll_table2(list_sentences, filters: List[CoNLLFilter]):
    list_queried = []
    for sent in list_sentences:
        list_word_indices: List[List[str]] = search_related_words3(sent, filters)
        for node in list_word_indices:
            list_queried.append(node)
        # obtain the full sentence
        whole_sent = ""
        for token in sent:
            whole_sent += token[1] + " "
        whole_sent = whole_sent.strip()
    return list_queried


# %%

"""

Print all the output.

"""


def print_result(_list_queried_):
    if len(_list_queried_) == 0:
        print(noResults)
        tk.messagebox.showinfo("NO RESULTS", noResults)


# %%

"""

put all the output in a csv file.

"""

"""
The 11 indexed items are created in the function search_CoNLL_table:

			#item[8] keyword[1]/SEARCHED TOKEN 
			#item[9] keyword[3]/SEARCHED TOKEN POSTAG, 
			#item[10] keyword[6]/'SEARCHED TOKEN DEPREL')
			list_queried.append((tok_form,tok_postag,tok_deprel,is_head,str(tok_Document_ID)[:-2],
				tok_Sentence_ID,tok_Document,
				whole_sent,keyword[1],keyword[3],keyword[6]))

	item[0] form/lemma
	item[1] postag
	item[2] deprel
	item[3] is_head
	item[4] Document_ID 
	item[5] Sentence_ID
	item[6] Document
	item[7] whole_sent 
	item[8] keyword[1]/SEARCHED TOKEN 
	item[9] keyword[3]/SEARCHED TOKEN POSTAG 
	item[10] keyword[6]/'SEARCHED TOKEN DEPREL'
"""


def output_list(list_queried, searchedCoNLLField, documentId_position):
    if len(list_queried) != 0:
        # to the 11 fields 4 postag and deprel descriptions are headed
        output_list = [['SEARCHED TOKEN (' + searchedCoNLLField + ')', 'SEARCHED TOKEN POSTAG',
                        'SEARCHED TOKEN POSTAG-DESCRIPTION', 'SEARCHED TOKEN DEPREL',
                        'SEARCHED TOKEN DEPREL-DESCRIPTION', 'Co-occurring token (' + searchedCoNLLField + ')',
                        'Co-occurring token POSTAG', 'Co-occurring token POSTAG-DESCRIPTION',
                        'Co-occurring token DEPREL', 'Co-occurring token DEPREL-DESCRIPTION', 'is_HEAD',
                        'Sentence ID', 'Sentence', 'Document ID', 'Document']]
        for item in list_queried:
            output_list.append([item[8], item[9], CoNLL_util.find_full_postag(item[8], item[9]), item[10],
                                CoNLL_util.find_full_deprel(item[8],
                                                               item[10]), item[0], item[1],
                                CoNLL_util.find_full_postag(item[0], item[1]), item[2],
                                CoNLL_util.find_full_deprel(item[0], item[2]),
                                item[3], item[5], item[7], item[4], item[6]])
    return output_list


# %%

"""
def check_searchField(*args):
	select_output_file_button.configure(state='active')
	if searchField_kw.get()!='':
		outputfile=IO_util.generate_output_file_name(inputFilename.get(),'.csv',"QC",searchField_kw.get() + "_" + searchedCoNLLField.get())
		outputFilename.set(outputfile)
		setup_IO_configArray(window,input_output_options)
searchField_kw.trace("w", check_searchField)

def check_searchedCoNLLField(*args):
	outputfile=IO_util.generate_output_file_name(inputFilename.get(),'.csv',"QC",searchField_kw.get() + "_" + searchedCoNLLField.get())
	outputFilename.set(outputfile)
	setup_IO_configArray(window,input_output_options)
searchedCoNLLField.trace("w",check_searchedCoNLLField)
"""
