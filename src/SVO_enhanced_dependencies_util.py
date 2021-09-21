#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 22:35:13 2021

@author: claude
"""
import GUI_IO_util
import json
import os
import difflib
import pprint
import sys


def SVO_enhanced_dependencies_sent_data_reorg(sentence):#reorganize the dependencies output of stanford corenlp
    result = {}#store each token's information
    tokens = sentence['tokens']
    # dependencies = sentence["enhancedDependencies"]
    dependencies = sentence["enhancedPlusPlusDependencies"]
    for token in tokens:
        idx = token["index"]
        result[idx] = {}#the key of each token's information is their index in the sentence
        # type of information will be keys
        result[idx]["index"] = idx
        result[idx]["word"] = token["word"]
        result[idx]["pos"] = token["pos"]
        result[idx]["lemma"] = token["lemma"]
        result[idx]["ner"] = token["ner"]
        if result[idx]["ner"] == 'TIME' or result[idx]["ner"] == 'DATE':
            try:
                result[idx]['normalizedNER'] = token['normalizedNER']
            except:
                 result[idx]['normalizedNER'] = "N/A"
        #reshape the dependencies to generate a dictionary whose syntactical head (governor) is the corrent token
        # the form: {dep: index}
        dep_rel, dep_govern = dep_dict(idx, dependencies)
        result[idx]["deprel"] = dep_rel
        result[idx]["govern_dict"] = dep_govern
    return result

def dep_dict(idx, dependencies):
    #idx: index of the target token
    dep_rel = ""
    dep_govern = {}
    for dep in dependencies:
        if dep['dependent'] == idx:
            dep_rel = dep['dep']# find the target token's dep
        if dep['governor'] == idx:# find token whose syntactical head is target token
            #add index of the token whose syntactical head (governor) is the target token
            if dep['dep'] in dep_govern.keys():
                if isinstance(dep_govern[dep['dep']], list):
                    dep_govern[dep['dep']].append(dep['dependent'])
                else: 
                    nodes_ = [dep_govern[dep['dep']]]
                    nodes_.append(dep['dependent'])
                    dep_govern[dep['dep']] = nodes_
            else:
                dep_govern[dep['dep']] = dep['dependent']
    return dep_rel, dep_govern

#processing multiple tokens (conjuncts) that are subjects/objects of one verb into a string
def s_o_formation (subjects, sent_data):
    if isinstance(subjects, list):#multiple tokens found
        return conj_string(subjects, sent_data), subjects[0]
    else:
        return sent_data[subjects]['word'], subjects


def conj_string(subjects, sent_data): # connect multiple conjugates into a single string
    subj = subjects[0]
    result = sent_data[subj]['word']
    start_result = result
    subj_gov = sent_data[subj]["govern_dict"]
    for key in subj_gov.keys():
        if "conj" in key:
            conj = key[5:]#extract the conjunction word (and, or, etc.)
            if isinstance(subj_gov[key], list):
                if subj_gov[key] == subjects[1:]:
                    for i in range(1, len(subjects) - 1):
                        result = result +  ", " + sent_data[subjects[i]]['word']
                    result = result + ", " + conj + " " + sent_data[subjects[-1]]['word']
                    break
            else: 
                if len(subjects) == 2 and subjects[-1] == subj_gov[key]:
                    result = result +  " " + conj + " " + sent_data[subjects[-1]]['word']
                    break
    if result != start_result:
        return result
    else:
        return token_connect(subjects, sent_data)

def token_connect(keys, sent_data):
    #if there are multiple tokens with the same dep uner a governor
    #this function process the content to that key (the dep) in the governor dictionary
    #if it's a list, this functino returns a string that connect each word with " "
    if isinstance(keys, list):
        tokens = []
        for k in keys:
            tokens.append(sent_data[k]['word'])
        return " ".join(tokens)
    else:
        return sent_data[keys]['word']



def verb_index_conj(key, token, gov_dict, sent_data):
    #for multiple verbs that are conjuncts of each other
    #
    verb_list = []
    conj_word = ""
    verb_list.append(key)
    dep = ""
    #extract the conjunct word (and, or, nor) from the dep
    if 'conj:or' in gov_dict.keys():
        dep = "conj:or"
        conj_word = "or"
    elif 'conj:and' in gov_dict.keys():
        dep = "conj:and"
        conj_word = "and"
    elif 'conj:nor' in gov_dict.keys():
        dep = "conj:nor"
        conj_word = "nor"
    if dep != "" and isinstance(gov_dict[dep], list):
        for i in gov_dict[dep]:
            verb_list.append(i)
    if dep != "" and not isinstance(gov_dict[dep], list):
        verb_list.append(gov_dict[dep])
    #return a list containing the each verb's index
    return verb_list, conj_word
    


def verb_obj_obl(token, sent_data, v_obj_obl_json):#check if one verb is a part of an LVC
    gov_dict = token["govern_dict"]
    verb_lemma = token["lemma"]
    if verb_lemma not in v_obj_obl_json.keys():# the case when that verb has no list of preposition collocation stored in lib file
        return "", "", ""
    obj = s_o_formation(gov_dict["obj"], sent_data)[0]#extract the sudo objective 
    for conb in v_obj_obl_json[verb_lemma]:# traverse the current LVCs stored in the file
        if conb["obj"] == obj.lower():
            if "obl" in conb.keys():
                obl_key = "obl"
            #sometimes the dep of the object start with "nmod"
            elif "nmod" in conb.keys():
                obl_key = "nmod"
            obl_prep = obl_key+":" + conb[obl_key]
            start_index = token["index"]
            if isinstance(gov_dict["obj"], list):
                end_index = gov_dict["obj"][0]
            else:
                end_index = gov_dict["obj"]
            new_v = ""
            for i in range(start_index, end_index + 1):
                new_v += sent_data[i]["word"] + " "
            new_v += conb[obl_key]
            if obl_prep in gov_dict.keys():
                new_o  = s_o_formation(gov_dict[obl_prep], sent_data)[0]
                return new_v, new_o, obl_prep
            elif "downwards" in conb.keys():
                #sometimes the syntactical head of the real object is not the verb
                # but a token that's governed by the verb
                # if "downwards" is in the key
                #the syntactical head of the real object will be the token governed by the verb with same dep as what's stored in the dictionary with the key "downwards"
                downwards_key = conb["downwards"]
                downwards_token = sent_data[gov_dict[downwards_key]]
                new_gov_dict = downwards_token["govern_dict"]
                if obl_prep in new_gov_dict.keys():
                    new_o  = s_o_formation(new_gov_dict[obl_prep], sent_data)[0]
                    return new_v, new_o, downwards_key
    return "", "", ""

def advcl_building(token, sent_data, ner, p_s, p_o, v_obj_obl_json, v_prep_json):
    result = []
    negation_result = []
    gov_dict = token["govern_dict"]
    advcl = gov_dict[ner]
    if not isinstance(advcl, list):
        advcl = [advcl]
    for idx in advcl:
        advcl_token = sent_data[idx]
        if "VB" not in advcl_token["pos"]:#only look for modifiers that are verbs
            continue
        
        s, v, o, negation,o_idx = verb_root_svo_building(idx, sent_data, v_obj_obl_json, v_prep_json)
        if advcl_token["pos"] == "VBN" and o == "":# if the modifier is in passive voice
            o = p_s#the subject of the verb it modifies will be its default object
        else:
            if s == "Someone?":
                s = p_s#the subject of the verb it modifies will be its default subject
        result.append([s, v, o])
        negation_result.append(negation)
        #extract the modifer's modifier by recursion
        second_result, second_negation_result = advcl_extraction(advcl_token, sent_data, s, o, v_obj_obl_json, v_prep_json)
        result.extend(second_result)
        negation_result.extend(second_negation_result)
    return result, negation_result
        

def advcl_extraction(token, sent_data, p_s, p_o, v_obj_obl_json, v_prep_json): 
    result = []
    negation_result = []
    gov_dict = token["govern_dict"]
    for dep in gov_dict.keys():
        if "advcl" in dep or "xcomp" in dep or dep == "dep":# find clausal modifers of a verb
            advcl_svo, advcl_negation = advcl_building(token, sent_data, dep, p_s, p_o, v_obj_obl_json, v_prep_json)
            result.extend(advcl_svo)
            negation_result.extend(advcl_negation)

    return result, negation_result
        
def verb_root_svo_building(verb, sent_data, v_obj_obl_json, v_prep_json):#extract the subject and object of a single verb (as well as processing modifiers of that verb)
    s = 'Someone?'
    o = ''
    s_idx = -1
    o_idx = -1
    verb_token = sent_data[verb]
    v_string = verb_token["word"]
    v_lemma = verb_token["lemma"]
    vgd = verb_token["govern_dict"]

    
    negation = negation_detect(verb_token, sent_data)
    #form the verb
    #'compound:prt' is the compound part of the verb, usually a preposition that follows the the verb
    if 'compound:prt' in vgd.keys():
        # v_string = v_string + " "  +sent_data[vgd['compound:prt']]['word']
        v_string = v_string + " " + token_connect(vgd["compound:prt"], sent_data)
    
        
    
    #extract subject    
    s_dep = ''
    if "nsubj" in vgd.keys():
        s, s_idx = s_o_formation(vgd["nsubj"], sent_data)
        s_dep = "nsubj"
        

        
    elif 'obl:agent' in vgd.keys():#subject in passive sentence
        s, s_idx = s_o_formation(vgd['obl:agent'], sent_data)
        s_dep = 'obl:agent'
    
    elif 'nsubj:xsubj' in vgd.keys():
        s, s_idx = s_o_formation(vgd['nsubj:xsubj'], sent_data)
        s_dep = 'nsubj:xsubj'
        
    if s_dep != '':
        negation = negation or content_negation(vgd[s_dep], sent_data)
    
    #extract object
    o_dep = ''
    if 'nsubj:pass' in vgd.keys():#object in passive sentence (example: "He" in "He was hit by a car")
        o_dep = 'nsubj:pass'
        o, o_idx = s_o_formation(vgd['nsubj:pass'], sent_data)#sent_data[gov_dict['nsubj:pass']]['word']
    
        
    elif "iobj" in vgd.keys():#indirect objects (example: He asked me a question; me)
        o_dep = "iobj"
        o, o_idx = s_o_formation(vgd["iobj"], sent_data)
    elif "obj" in vgd.keys(): #direct object
        #extract LVCs (take care of, take advantage of, etc.)
        new_v, new_o, new_o_dep= verb_obj_obl(verb_token, sent_data, v_obj_obl_json)
        if new_v != '':# the verb is a part of a LVC
            
            v_string = new_v
            o = new_o
            o_dep = new_o_dep 
        else:
            o_dep = "obj"
            o, o_idx = s_o_formation(vgd["obj"], sent_data)
    
    
    else:     #object follows a preposition
        obl_preps = []
        for gov_key in vgd.keys():#collecting potential objects
            if "obl" in gov_key :
                if gov_key[4:] != "tmod" and gov_key[4:] != "agent":
                    obl_preps.append(gov_key)
                    
                   
        if len(obl_preps) == 1:
            o_dep = obl_preps[0]
            o, o_idx  = s_o_formation(vgd[obl_preps[0]], sent_data)
            v_string = v_string + " " + obl_preps[0][4:].replace("_", " ")
        elif len(obl_preps) > 1:#multiple potential objects that needs selecting
            for oblp in obl_preps:
                prep = oblp[4:]
                if prep in v_prep_json.keys():
                    if v_lemma.lower() in v_prep_json[prep]:
                        o_dep = oblp
                        o, o_idx = s_o_formation(vgd[oblp], sent_data)
                        v_string = v_string + " " + prep
                        break
        # check for double prepositions, 
        #example: "people who sit next to each other" (the dep of "other" is "obl:next_to")
            for oblp in obl_preps:
                prep = oblp[4:]
                if "_" in prep:
                    o_dep = oblp
                    o, o_idx = s_o_formation(vgd[oblp], sent_data)
                    v_string = v_string + " " + obl_preps[0][4:].replace("_", " ")
                    break
            


    if o_dep != '':
        negation = negation or content_negation(vgd[o_dep], sent_data)
    return s, v_string, o, negation, o_idx

       
def verb_root(verb_list, conj_word, token, sent_data):#extract subject, object, and negation of a single verb or multiple verbs that are conjuncts
    v_prep_text = GUI_IO_util.CoreNLP_enhanced_dependencies_libPath + os.sep + "verb_prep_json.txt"#json that help with extracting object that follows a preposition
    v_obj_obl_text = GUI_IO_util.CoreNLP_enhanced_dependencies_libPath + os.sep + "verb_obj_obl_json.txt" #json that help with extracting certain light verb constructions as a whole verb
    with open(v_prep_text) as v_prep_doc:
        v_prep_json = json.load(v_prep_doc)
    with open(v_obj_obl_text) as v_obj_obl_doc:
        v_obj_obl_json = json.load(v_obj_obl_doc)

    
    gov_dict = token["govern_dict"]
    s_list = []
    verb_strings_list = []
    o_list = []
    svo = []
    negation_list = []
    s_set = False #booleans indicating if setting a default subject is needed (T:neede; F: already set)
    o_set = False#booleans indicating if setting default object is needed (T:neede; F: already set)
    o_share_idx = -1
    s_share = 'Someone?'# a potential default subject for multiple conjunct verbs
    o_share = ""# a potential default object for multiple conjunct verbs
    for verb in verb_list:
        s, v, o, negation, o_idx = verb_root_svo_building(verb, sent_data, v_obj_obl_json, v_prep_json)
        if verb > o_share_idx:#default object needs resetting if it's not following the verb.
            o_set = False
        if len(negation_list) > 0:
            if negation_list[0] == True and conj_word == "or":
                negation = True
            
            
        
        if s_set == False and s != 'Someone?':#setting potential subject
            s_set = True
            s_share = s
        if o_set == False and o != '':#setting potential object
            o_set = True
            o_share = o
            o_share_idx = o_idx
        if s == 'Someone?':
            s = s_share
        if o == '' and verb < o_share_idx: #object has to locate behind the verb in the sentence.
            o = o_share  
       
        negation_list.append(negation)
        svo.append([s, v, o])
            
        verb_token = sent_data[verb]
        #extracting the subject and object of the modifier of verbs
        advcl_svo, advcl_negation = advcl_extraction(verb_token, sent_data, s, o, v_obj_obl_json, v_prep_json)
        svo.extend(advcl_svo)
        negation_list.extend(advcl_negation)
        
    return svo, negation_list


def pred_root(token, gov_dict, sent_data):# returns one triplet of subject-link verb-predicative nominate
    #predicative nominate
    #https://www.thesaurus.com/e/grammar/predicate-nominative-vs-predicate-adjectives/
    # the predicative nominate would be the synactical head of the subject and the link verb (usually is "be")
    s = 'Someone?'
    v = ''
    o = ''
    negation = negation_detect(token, sent_data)
    if "nsubj" in gov_dict.keys():
        s = s_o_formation(gov_dict["nsubj"], sent_data)[0]
        negation = negation or content_negation(gov_dict["nsubj"], sent_data)
    if "cop" in gov_dict.keys():
        # v = sent_data[gov_dict["cop"]]['word']
        # if v != "":
        v = token_connect(gov_dict["cop"], sent_data) + " " +v 
        # else:
        #     v = token_connect(gov_dict["cop"], sent_data)
        negation = negation or content_negation(gov_dict["cop"], sent_data)
    if "aux" in gov_dict.keys() and v != "":
        v = token_connect(gov_dict["aux"], sent_data) + " " +v 
        negation = negation or content_negation(gov_dict["aux"], sent_data)
    o = token["word"]
    if "case" in gov_dict.keys() and v != "":
        # v = v + " " + sent_data[gov_dict["case"]]['word']
        v = v + " " + token_connect(gov_dict["case"], sent_data)

    return s, v, o, negation



def content_negation(content, sent_data):
    if isinstance(content, list):
        for index in content:
            negation =  negation_detect(sent_data[index], sent_data)
    else:
        negation = negation_detect(sent_data[content], sent_data)
    return negation



def negation_detect(token, sent_data):#detect if there's negation associated with a verb
    gov_dict = token["govern_dict"]
    result = False
    if len(gov_dict.keys()) == 0:
        return result
    dep_list = ["advmod", "det", 'cc:preconj', 'cc', 'mark', 'aux']#the common dep of tokens tokens in negation_tokens
    negation_tokens = ["no", "not", "n't", "seldom", "without","never", "hardly", "neither", "nor"]
    for dep in dep_list:
        #seek for negation recursively
        # 1.: check if the dep of any token governed by the garget token is in the list
        # 2. check if they are negation words, if yes return
        # 3. if not, go through their govern dictionary, repeat 1
        if dep in gov_dict.keys():
            if isinstance(gov_dict[dep], list):
                
                for idx in gov_dict[dep]:
                    word = sent_data[idx]["word"]
                    for ntk in negation_tokens:
                        if ntk == word.lower():
                            return True
                        
                    result = result or negation_detect(sent_data[idx], sent_data)
            else:
                idx = gov_dict[dep]
                word = sent_data[idx]["word"]
                for ntk in negation_tokens:
                    if ntk == word.lower():
                        return True
                result = result or negation_detect(sent_data[idx],  sent_data)

    return result
                    
        
def link_verb_LVC_extraction(token, gov_dict, sent_data):
    s = 'Someone?'
    v = ''
    o = ''
    negation = negation_detect(token, sent_data)
    #load the json from the txt file
    link_verb_LVC_text = GUI_IO_util.CoreNLP_enhanced_dependencies_libPath + os.sep + "link_verb_LVC_json.txt"#json that help with extracting object that follows a preposition
    with open(link_verb_LVC_text) as link_verb_LVC_doc:
        link_verb_LVC_json = json.load(link_verb_LVC_doc)
    
    if token["lemma"] in link_verb_LVC_json.keys():#that token is the dependency ROOT (the syntactical head of other tokens in that LVC) of that LVC 
        for conb in link_verb_LVC_json[token["lemma"]]:
            start_index= token["index"]
            end_index= token["index"]
            for key in conb.keys():
                if key != "prep":#check that token is the syntactical head of other tokens in the LVC
                    dep = conb[key]
                    if dep not in gov_dict:
                        break
                    if isinstance(gov_dict[dep], list):
                        break
                    negation = negation or content_negation(gov_dict[dep], sent_data)
                    current_token = sent_data[gov_dict[dep]]
                    if current_token["lemma"] != key:
                        break
                    if start_index > current_token["index"]:
                        start_index = current_token["index"]
                    if end_index < current_token["index"]:
                        end_index = current_token["index"]
                else:#check if that ROOT token is the syntactical head of the real object
                    for prep_dep in conb["prep"]:
                        if prep_dep in gov_dict.keys():# LVC extracted
                            for i in range(start_index, end_index + 1):
                                v += sent_data[i]["word"] + " "
                            v += prep_dep.split(':')[1]
                            o = s_o_formation(gov_dict[prep_dep], sent_data)[0]
                            negation = negation or content_negation(gov_dict[prep_dep], sent_data)
                            if "nsubj" in gov_dict.keys():
                                s = s_o_formation(gov_dict["nsubj"], sent_data)[0]
                                negation = negation or content_negation(gov_dict["nsubj"], sent_data)
                            return s, v, o, negation
    return "", "", "", negation
                            
                            
                            
                            
                    
                    
                    
                        
            
    
    
        
def SVO_extraction (sent_data): #returns columns of the final output

    CollectedVs = []#list of processed verbs
    SVO = []#list that store the subject-verb-object triplets
    L = []#list that stores the location information appear in sentences
    T = []#list that stores the time information appear in sentences
    T_S = []#list that stores normalized form of the time information appear in sentences
    P = []#list that stores person names appear in sentences
    N = []#list that stores negation booleans (T=negation; F= without negation)
    acl = []#list that stores modifier
    s = "Someone?"#default subject
    v = ""
    o = ""
    
    link_verb_LVC_text = GUI_IO_util.CoreNLP_enhanced_dependencies_libPath + os.sep + "verb_obj_obl_json.txt"
    for key in sent_data.keys():#traverse each token token in that sentence
        negation = False 
        token = sent_data[key]

        #collect token if it contains information of location/time/name
        if token["ner"] == "TIME" or token["ner"] == "DATE":
            T.append(token["word"])
            
            T_S.append(token['normalizedNER'])

        if token["ner"] == "PERSON": 
            P.append(token["word"])
        if token["ner"] == "CITY" or  token["ner"] == 'STATE_OR_PROVINCE' or token["ner"] == 'COUNTRY': 
            L.append(token["word"])
        
        
        
        gov_dict = token["govern_dict"]#the dictionary that contains information of the dep and index of tokens whose syntactical head is the corrent token
        if ("VB" in token["pos"]) and ("advcl" not in token['deprel']) and ("xcomp" not in token['deprel'])and (token['deprel'] != "dep") and (token['deprel'] != "acl"):#if the verb has not been processed and its dep is not a special dep that will be processed independently
            # If the current token is a verb
            # it will possibly contains its subject and object in its govern dictionary
            if key not in CollectedVs:
                verb_list, conj_word = verb_index_conj(key, token, gov_dict, sent_data)
                #verb_list will contain the other verbs in this sentence that are the current verb's conjunct
                #verb_index_conj is the conjunct token (and, or, nor, etc.)
                CollectedVs.extend(verb_list)
                svo_verb, negation_verb = verb_root(verb_list, conj_word, token, sent_data)#processing
                for i in range(len(svo_verb)):
                    s = svo_verb[i][0]
                    v = svo_verb[i][1]
                    o = svo_verb[i][2]
                    n = negation_verb[i]
                    #a verb will be collected into the outpt if it:
                    # i. has associated subject
                    # ii. OR has associated object
                    if s != 'Someone?' or o != '':
                        SVO.append([s, v, o])
                        N.append(n)
               
        
        
        else:#if that token is not a verb 
            #check if that token is a part of an LVC that starts with a link verb (like "be responsible for")
            s,v,o, negation = link_verb_LVC_extraction(token, gov_dict, sent_data)
            if v != "" and ( s != "Someone?" or o != ''):
                if [s, v, o] not in SVO:#avoid repetition
                    SVO.append([s, v, o])
                    N.append(negation)
            #check if the token is a predicative modifier
            elif (token["deprel"] == "ROOT" or token["deprel"] == "parataxis") and ("NN" in token["pos"] or token["pos"] == "PRP"):#Subject -> Verb(be) -> predicative nominative
                s, v, o, negation = pred_root(token, gov_dict, sent_data)
                
                if v != "" and ( s != "Someone?" or o != ''):
                    if [s, v, o] not in SVO:#avoid repetition
                        SVO.append([s, v, o])
                        N.append(negation)
            
        
        acl_key = ""#detect if there's clausal modifier whose syntactical head is the current token
        #find the dep of the clausal modifier (acl or acl:relcl)
        if "acl" in gov_dict.keys():
            acl_key = "acl"
        elif "acl:relcl" in gov_dict.keys():
             acl_key = "acl:relcl"
        elif "dep" in gov_dict.keys():
             acl_key = "dep"
        if acl_key != "":
        
            if isinstance(gov_dict[acl_key], list):
                id_list = gov_dict[acl_key]
                
            else:
                id_list = [gov_dict[acl_key]]
            for v_id in id_list:
                v_token = sent_data[v_id]
                if "VB" in v_token["pos"]:
                    CollectedVs.append(v_id)
                    svo_acl, negation_acl = verb_root([v_id], "",v_token, sent_data)
                    if len(svo_acl) != 0:
                        if svo_acl[0][0] == "Someone?":
                            #if the subject is missing in the dependency, the subject of the clausal modifier is the token that it modifies (syntactical head)
                            svo_acl[0][0] = token["word"]
                    SVO.extend(svo_acl)
                    N.extend(negation_acl)
 
    return SVO, L, T, T_S, P, N
            
                        
# Dec. 21
