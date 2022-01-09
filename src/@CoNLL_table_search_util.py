# The Python 3 routine was written by Jian Chen, 12.12.2018
# modified by Jian Chen (January 2019)
# modified by Jack Hester (February 2019) and Roberto Franzosi (June and December 2019)
# ALL SEARCHES OCCUR WITHIN SENTENCES.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoNLL table_search_util", ['os', 'tkinter','enum','typing']) == False:
    sys.exit(0)

from enum import Enum
from typing import List
import tkinter as tk
import tkinter.messagebox as mb

import Stanford_CoreNLP_tags_util
import CoNLL_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

noResults = "No results found matching your search criteria for your input CoNLL file. Please, try different search criteria.\n\nTypical reasons for this warning are:\n   1.  You are searching for a token/word not found in the FORM or LEMMA fields (e.g., 'child' in FORM when in fact FORM contains 'children', or 'children' in LEMMA when in fact LEMMA contains 'child'; the same would be true for the verbs 'running' in LEMMA instead of 'run');\n   2. you are searching for a token that is a noun (e.g., 'children'), but you select the POS value 'VB', i.e., verb, for the POSTAG of searched token."

filesToOpen = []  # Store all files that are to be opened once finished


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


def search_deps(token_id_in_sentence, sentence, searchedCoNLLField):
    '''
    break the enhanced dependencies column to search each dependencies.

    Parameters
    ----------
    token_id_in_sentence
    sentence
    searchedCoNLLField

    Returns
        []: empty list when no head or error

    -------

    '''
    try:
        token = sentence[int(token_id_in_sentence) - 1]
    except:
        mb.showwarning(title='CoNLL table error',
                       message="The records in the CoNLL table appear to be out of sequence, leading to computing errors. Please, make sure that you haven't tinkered with the file sorting the data by any columns other than RecordID.\n\nSort the data by RecordID (col. 9) and try again.")
        # sys.exit(0)
        return []
    if len(token[7]) == 0:
        return []

    res = []
    #split deps string "5:nsubj|8:nsubj"
    deps_str = token[7].split("|")
    deps_list = []
    for dep in deps_str:
        deps_list.append(dep.split(":"))

    #TODO: check the edge case when return None, is it possible to have one of the head pointing to self
    for dep in deps_list:
        head_num = int(dep[0])
        if head_num != token[0] and head_num != 0:
            if searchedCoNLLField == "FORM":
                head_form = sentence[head_num - 1][1]  # form
            else:
                head_form = sentence[head_num - 1][2]  # lemma
            head_postag = sentence[head_num - 1][3]  # postag
            head_deprel = sentence[head_num - 1][6]  # deprel
            res.append(((head_form, head_postag, head_deprel), head_num))
        elif head_num == 0:
            continue
        else:
            return res

    return res







def search_head(token_id_in_sentence, sentence, searchedCoNLLField):
    try:
        token = sentence[int(token_id_in_sentence) - 1]
    except:
        mb.showwarning(title='CoNLL table error',
                       message="The records in the CoNLL table appear to be out of sequence, leading to computing errors. Please, make sure that you haven't tinkered with the file sorting the data by any columns other than RecordID.\n\nSort the data by RecordID (col. 9) and try again.")
        #sys.exit(0)
        return "NO_HEAD", "NO_HEAD"
    head_num = int(token[5])
    if head_num != token[0] and head_num != 0:
        if searchedCoNLLField == "FORM":
            head_form = sentence[head_num - 1][1]  # form
        else:
            head_form = sentence[head_num - 1][2]  # lemma
        head_postag = sentence[head_num - 1][3]  # postag
        head_deprel = sentence[head_num - 1][6]  # deprel
    elif head_num == 0:
        return "NO_HEAD", "NO_HEAD"
    else:
        return "NO_HEAD", "NO_HEAD"
    return (head_form, head_postag, head_deprel), head_num


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

# NEVER CALLED
# def search_token_form(desired_form,sentence):
# 		#return a list of indices in the sentence related to the desired word
# 		list_indices = []
# 		for item in sentence:
# 			if desired_form == '*':
# 				list_indices.append(item[0])
# 			else:
# 					token_form = item[1]
# 					token_index_in_sent = int(item[0])
# 					if token_form == desired_form:
# 							list_indices.append(token_index_in_sent)
# 		return list_indices


# #return all indices of the co-occuring word

# 		list_indices_related_word = []
# 		#compare term: form or lemma
# 		if __field__ == 'FORM':
# 				compare_term = 1 #field poistion of FORM in CoNLL
# 		else:
# 				compare_term = 2 #field poistion of LEMMA in CoNLL

# 		if desired_form == '*':
# 				keyword_list = sentence
# 		#in each sentence, obtain the keyword tokens
# 		else:
# 				keyword_list = [keyword for keyword in sentence if keyword[compare_term] == desired_form]
# 		#select remaining tokens

# 		if kw_desired_postag == '*':
# 				keyword_list = keyword_list
# 		elif kw_desired_postag == 'NN*':
# 				keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['NN','NNS','NNP','NNPS']]
# 		elif kw_desired_postag == 'JJ*':
# 				keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['JJ','JJR','JJS']]
# 		elif kw_desired_postag == 'RB*':
# 				keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['RB','RBR','RBS',]]
# 		elif kw_desired_postag == 'VB*':
# 				keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['VB','VBN','VBG','VBZ','VBP','VBD']]
# 		else:
# 				keyword_list = [keyword for keyword in keyword_list if keyword[3] == kw_desired_postag]
# 		if kw_desired_deprel == '*':
# 				keyword_list = keyword_list
# 		else:
# 				keyword_list = [keyword for keyword in keyword_list if keyword[6] == kw_desired_deprel]
# 		#search 
# 		for keyword in keyword_list:
# 				token_id = keyword[0]
# 				#search head
# 				head, head_num = search_head(token_id,sentence)
# 				if head != "NO_HEAD":
# 					 list_indices_related_word.append((head_num,1,keyword))
# 				#search_children (the tokens whose head is the searched word)
# 				for child in find_children(sentence,int(token_id))[1]:
# 						list_indices_related_word.append((child,0,keyword))

# 		for keyword in keyword_list:
# 				token_id = int(keyword[0])
# 				a, b = search_parsetree_loop_all_related(token_id, sentence,__field__)
# 				for ind in b:
# 						if (ind,0,keyword) not in list_indices_related_word and (ind,1,keyword) not in list_indices_related_word:
# 								list_indices_related_word.append((ind,2,keyword))


# 		return list_indices_related_word

# """
# NEVER CALLED

# This funtion search deeper relations on the parse tree to find consecutive tokens related to the same keyword.
# 1. It reads the list of the tokens that are directly linked to the keyword. 
# 2. It finds the grand-children of the keyword (as in a tree) that share the same POSTAG and deprel and add them into the list
# 3. return the list
# """
# def search_consecutive_relations(list_related,sentence):
# 		list_secondary_relations = []
# 		for related_token_tup in list_related:
# 				#print(related_token_tup)
# 				related_token = sentence[related_token_tup[0]-1]
# 				#print(related_token)
# 				is_HEAD = related_token_tup[1]
# 				if is_HEAD:
# 						continue
# 				token_id = related_token[0]
# 				for child_index in find_children(sentence, int(token_id))[1]:
# 						child = sentence[child_index-1]
# 						if child[3] == related_token[3] and child[6]== related_token[6]:
# 								list_secondary_relations.append((child[0],2,related_token_tup[2]))
# 		return list_secondary_relations

# # NEVER CALLED
# def search_related_words(desired_form, sentence, __field__ = 'FORM', kw_desired_postag = '*',kw_desired_deprel='*'):
# 		list_indices_related_word = []
# 		for token in sentence:
# 				token_form = token[1]
# 				token_lemma = token[2]
# 				token_id = token[0]
# 				token_postag = token[3]
# 				token_deprel = token[6]
# 				if __field__ == 'FORM':
# 						compare_term = token_form
# 				else:
# 						compare_term = token_lemma
# 				skip_flag = 0
# 				#filter the keywords
# 				if compare_term == desired_form:
# 						#print (kw_desired_postag)
# 						if kw_desired_postag != '*':
# 								if '*' not in kw_desired_postag:
# 										if token_postag != kw_desired_postag:
# 												skip_flag = 1
# 								else:
# 										if kw_desired_postag == "NN*":
# 												if token_postag in ['NN','NNS','NNP','NNPS']:
# 														skip_flag = 1
# 						if kw_desired_deprel != "*":
# 							 # print ("#######",token_deprel,kw_desired_deprel)
# 								if token_deprel != kw_desired_deprel:
# 										skip_flag = 1
# 						if skip_flag == 0:
# 							#find its head
# 							head, head_num = search_head(token_id,sentence,__field__)
# 							if head != "NO_HEAD":
# 								 list_indices_related_word.append((head_num,1))
# 							#find its children
# 							for child in find_children(sentence,int(token_id))[1]:
# 									list_indices_related_word.append((child,0))
# 		return list_indices_related_word

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


# Deprecated
def search_related_words2(desired_form, sentence, __field__='FORM', kw_desired_postag='*', kw_desired_deprel='*'):
    list_indices_related_word = []
    # compare term: form or lemma
    # print(sentence)
    if __field__ == 'FORM':
        compare_term = 1  # field poistion of FORM in CoNLL
    else:
        compare_term = 2  # field poistion of LEMMA in CoNLL

    if desired_form == '*':
        keyword_list = sentence
    # in each sentence, obtain the keyword tokens
    else:
        keyword_list = [keyword for keyword in sentence if keyword[compare_term] == desired_form]
    # select remaining tokens

    if kw_desired_postag == '*':
        keyword_list = keyword_list
    elif kw_desired_postag == 'NN*':
        keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['NN', 'NNS', 'NNP', 'NNPS']]
    elif kw_desired_postag == 'JJ*':
        keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['JJ', 'JJR', 'JJS']]
    elif kw_desired_postag == 'RB*':
        keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['RB', 'RBR', 'RBS', ]]
    elif kw_desired_postag == 'VB*':
        keyword_list = [keyword for keyword in keyword_list if keyword[3] in ['VB', 'VBN', 'VBG', 'VBZ', 'VBP', 'VBD']]
    else:
        keyword_list = [keyword for keyword in keyword_list if keyword[3] == kw_desired_postag]
    if kw_desired_deprel == '*':
        keyword_list = keyword_list
    else:
        keyword_list = [keyword for keyword in keyword_list if keyword[6] == kw_desired_deprel]
    # search
    for keyword in keyword_list:
        token_id = keyword[0]
        # search head
        #head, head_num = search_head(token_id, sentence, __field__)
        #search deps
        head_list = search_deps(token_id, sentence, __field__)
        if len(head_list) != 0:
            for head in head_list:
                list_indices_related_word.append((head[1], 1, keyword))

    #     if head != "NO_HEAD":
    #         list_indices_related_word.append((head_num, 1, keyword))
    #     # search_children (the tokens whose head is the searched word)
    #     for child in find_children(sentence, int(token_id), __field__)[1]:
    #         list_indices_related_word.append((child, 0, keyword))
    #
    # for keyword in keyword_list:
    #     token_id = int(keyword[0])
    #     a, b = search_parsetree_loop_all_related(token_id, sentence, __field__)
    #     for ind in b:
    #         if (ind, 0, keyword) not in list_indices_related_word and (
    #                 ind, 1, keyword) not in list_indices_related_word:
    #             list_indices_related_word.append((ind, 2, keyword))

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
    CLAUSAL_TAG = 7
    RECORD_ID = 8
    Sentence_ID = 9
    Document_ID = 10
    DOCUMENT = 11

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


def search_CoNLL_table(list_sentences, form_of_token, _field_='FORM', related_token_POSTAG="*",
                       related_token_DEPREL="*",
                       Sentence_ID="*", _tok_postag_='*', _tok_deprel_='*'):
    list_queried = []
    deprel_list_queried = []
    for sent in list_sentences:
        try:
            list_word_indices = search_related_words2(form_of_token, sent, _field_, _tok_postag_, _tok_deprel_)
        except:
            mb.showwarning(title='CoNLL table error',
                           message="The records in the CoNLL table appear to be out of sequence, leading to computing "
                                   "errors. Please, make sure that you haven't tinkered with the file sorting the data "
                                   "by any columns other than RecordID.\n\nSort the data by RecordID (col. 9) and try "
                                   "again.")
            # sys.exit(0)
            return deprel_list_queried
        # obtain the full sentence
        whole_sent = ""
        for token in sent:
            whole_sent += token[1] + " "
        whole_sent = whole_sent.strip()
        for node in list_word_indices:
            ind = node[0]
            is_head = node[1]
            keyword = node[2]
            row = sent[int(ind) - 1]
            if _field_ == 'FORM':
                tok_form = row[1]
            else:
                tok_form = row[2]
            tok_postag = row[3]
            tok_deprel = row[6]
            tok_Sentence_ID = row[10]
            tok_Document_ID = row[11]
            tok_Document = row[12]
            token_id = str(tok_Document_ID)[:-2] + str("-" + tok_Sentence_ID)
            # item[8] keyword[1]/SEARCHED TOKEN
            # item[9] keyword[3]/SEARCHED TOKEN POSTAG,
            # item[10] keyword[6]/'SEARCHED TOKEN DEPREL')
            if _field_ == "FORM":
                searched_keyword = keyword[1]
            else:
                searched_keyword = keyword[2]
            list_queried.append((tok_form, tok_postag, tok_deprel, is_head, tok_Document_ID,
                                 tok_Sentence_ID, tok_Document,
                                 whole_sent, searched_keyword, keyword[3], keyword[6]))
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
                        'Sentence ID', 'Document ID', 'Document', 'Sentence']]
        for item in list_queried:
            output_list.append([item[8], item[9], CoNLL_util.find_full_postag(item[8], item[9]), item[10],
                                CoNLL_util.find_full_deprel(item[8],
                                                               item[10]), item[0], item[1],
                                CoNLL_util.find_full_postag(item[0], item[1]), item[2],
                                CoNLL_util.find_full_deprel(item[0], item[2]),
                                item[3], item[5], item[4], item[6], item[7]])
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
