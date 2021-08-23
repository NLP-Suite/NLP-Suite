#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 22:35:13 2021

@author: claude
"""
import GUI_IO_util
import json
import os

def OpenIE_sent_data_reorg(sentence):#reorganize the dependencies output of stanford corenlp
    result = {}#store each token's information
    tokens = sentence['tokens']
    dependencies = sentence["enhancedDependencies"]
    # openie = sentence['openie']
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

def conj_string(subjectives, sent_data): # connect multiple conjugates into a single string
    subj = subjectives[0]
    result = sent_data[subj]['word']
    subj_gov = sent_data[subj]["govern_dict"]
    for key in subj_gov.keys():
        if "conj" in key:
            conj = key[5:]#extract the conjunction word (and, or, etc.)
            if isinstance(subj_gov[key], list):
                if subj_gov[key] == subjectives[1:]:
                    for i in range(1, len(subjectives) - 1):
                        result = result +  ", " + sent_data[subjectives[i]]['word']
                    result = result + ", " + conj + " " + sent_data[subjectives[-1]]['word']
                    break
            else:
                if len(subjectives) == 2 and subjectives[-1] == subj_gov[key]:
                    result = result +  " " + conj + " " + sent_data[subjectives[-1]]['word']
                    break
    return result

def token_connect(keys, sent_data):#build a link verb 
    if isinstance(keys, list):
        tokens = []
        for k in keys:
            tokens.append(sent_data[k]['word'])
        return " ".join(tokens)
    else:
        return sent_data[keys]['word']



def verb_index_conj(key, token, gov_dict, sent_data):
    verb_list = []
    conj_word = ""
    verb_list.append(key)
    dep = ""
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
    return verb_list, conj_word
    


def verb_obj_obl(token, sent_data, v_obj_obl_json):#check if one verb is a part of an LVC
    gov_dict = token["govern_dict"]
    verb_lemma = token["lemma"]
    if verb_lemma not in v_obj_obl_json.keys():# the case when that verb has no list of preposition collocation stored in lib file
        return "", "", ""
    obj = s_o_formation(gov_dict["obj"], sent_data)[0]#extract the sudo objective 
    for conb in v_obj_obl_json[verb_lemma]:# traverse the current LVCs stored in the file
        if conb["obj"] == obj.lower():
            obl_prep = "obl:" + conb["obl"]
            if obl_prep in gov_dict.keys():
                start_index = token["index"]
                if isinstance(gov_dict["obj"], list):
                    end_index = gov_dict["obj"][0]
                else:
                    end_index = gov_dict["obj"]
                new_v = ""
                for i in range(start_index, end_index + 1):
                    new_v += sent_data[i]["word"] + " "
                # new_v = token["word"] + " " + obj + " " + conb["obl"]
                new_v += conb["obl"]
                new_o  = s_o_formation(gov_dict[obl_prep], sent_data)[0]
                return new_v, new_o, obl_prep
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
        if "VB" not in advcl_token["pos"]:#only look for verb modifier
            continue
        
        s, v, o, negation,o_idx = verb_root_svo_building(idx, sent_data, v_obj_obl_json, v_prep_json)
        if advcl_token["pos"] == "VBN" and o == "":# if the modifier is in passive voice
            o = p_s#the subject of the verb it modifies will be its default object
        else:
            if s == "Someone?":
                s = p_s#the subject of the verb it modifies will be its default subject
        result.append([s, v, o])
        negation_result.append(negation)
    return result, negation_result
        

def advcl_extraction(token, sent_data, p_s, p_o, v_obj_obl_json, v_prep_json): 
    result = []
    negation_result = []
    gov_dict = token["govern_dict"]
    for dep in gov_dict.keys():
        if "advcl" in dep or "xcomp" in dep:# find clausal modifers of a verb
            # print("dep: ", dep)
            advcl_svo, advcl_negation = advcl_building(token, sent_data, dep, p_s, p_o, v_obj_obl_json, v_prep_json)
            result.extend(advcl_svo)
            negation_result.extend(advcl_negation)
            
    return result, negation_result
        
def verb_root_svo_building(verb, sent_data, v_obj_obl_json, v_prep_json):#extract the subject and object of a single verb (as well as processing modifiers of that verb)
    s = 'Someone?'
    # v = ''
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
    try:
        if 'compound:prt' in vgd.keys():
            v_string = v_string + " "  +sent_data[vgd['compound:prt']]['word']
    except:
        print('   ERROR in vgd.keys: ' + str(vgd.keys()))
        
    
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
        if isinstance(vgd[s_dep], list):
            s_list = vgd[s_dep]
        else:
            s_list = [vgd[s_dep]]
        for s_id in s_list: 
            negation = negation or negation_detect(sent_data[s_id], sent_data)
    
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
        new_v, new_o, new_o_dep = verb_obj_obl(verb_token, sent_data, v_obj_obl_json)
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
            v_string = v_string + " " + obl_preps[0][4:]
        elif len(obl_preps) > 1:#multiple potential objects that needs selecting
            for oblp in obl_preps:
                prep = oblp[4:]
                if prep in v_prep_json.keys():
                    if v_lemma.lower() in v_prep_json[prep]:
                        o_dep = oblp
                        o, o_idx = s_o_formation(vgd[oblp], sent_data)
                        v_string = v_string + " " + prep
                        break

    if o == '':
        if 'obl:tmod' in vgd.keys():
            tmod_idx = vgd["obl:tmod"]
            try:
                if tmod_idx in sent_data.keys():
                    tmod_token = sent_data[tmod_idx]
                    tmod_gd = tmod_token["govern_dict"]
                    if "nmod:poss" in tmod_gd.keys():
                        o, o_idx = s_o_formation(tmod_gd["nmod:poss"], sent_data)

                        if isinstance(tmod_gd["nmod:poss"], list):
                            o_list = tmod_gd["nmod:poss"]
                        else:
                            o_list = [tmod_gd["nmod:poss"]]
                        for o_id in o_list:
                            negation = negation or negation_detect(sent_data[o_id], sent_data)
            except:
                print('   ERROR in sent_data.keys: ' + str(sent_data.keys()))
    if o_dep != '':
        if isinstance(vgd[o_dep], list):
            o_list = vgd[o_dep]
        else:
            o_list = [vgd[o_dep]]
        for o_id in o_list: 
            negation = negation or negation_detect(sent_data[o_id], sent_data)
    return s, v_string, o, negation, o_idx

       
def verb_root(verb_list, token, sent_data):#extract subject, object, and negation of a single verb or multiple verbs that are conjuncts
    v_prep_text = GUI_IO_util.OpenIE_libPath + os.sep + "verb_prep_json.txt"#json that help with extracting object that follows a preposition
    v_obj_obl_text = GUI_IO_util.OpenIE_libPath + os.sep + "verb_obj_obl_json.txt" #json that help with extracting certain light verb constructions as a whole verb
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
        if True in negation_list:
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
    if "nsubj" in gov_dict.keys():
        s = s_o_formation(gov_dict["nsubj"], sent_data)[0]
        
    
    if "cop" in gov_dict.keys():
        # v = sent_data[gov_dict["cop"]]['word']
        v = token_connect(gov_dict["cop"], sent_data) + " " +v 
    if "aux" in gov_dict.keys():
        v = token_connect(gov_dict["aux"], sent_data) + " " +v 
    o = token["word"]
    try:
        if "case" in gov_dict.keys():
            v = v + " " + sent_data[gov_dict["case"]]['word']
    except:
        print('   ERROR in gov_dict.keys: ' + str(gov_dict.keys()))
    return s, v, o







def negation_detect(token, sent_data):#detect if there's negation associated with a verb
    gov_dict = token["govern_dict"]
    result = False
    dep_list = ["advmod", "det", 'cc:preconj', 'cc']#the common dep of tokens tokens in negation_tokens
    negation_tokens = ["no", "not", "n't", "seldom", "never", "hardly", "neither", "nor"]
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
                        if ntk in word.lower():
                            return True
                        
                        result = result or negation_detect(sent_data[idx], sent_data)
            else:
                idx = gov_dict[dep]
                word = sent_data[idx]["word"]
                for ntk in negation_tokens:
                    if ntk in word.lower():
                        return True
                    result = result or negation_detect(sent_data[idx],  sent_data)

    return result
                    
        
        
        
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
        if ("VB" in token["pos"]) and ("advcl" not in token['deprel']) and ("xcomp" not in token['deprel']) and (token['deprel'] != "acl"):#if the verb has not been processed and its dep is not a special dep that will be processed independently
            # If the current token is a verb
            # it will possibly contains its subject and object in its govern dictionary
            if key not in CollectedVs:
                verb_list, conj_word = verb_index_conj(key, token, gov_dict, sent_data)
                #verb_list will contain the other verbs in this sentence that are the current verb's conjunct
                #verb_index_conj is the conjunct token (and, or, nor, etc.)
                CollectedVs.extend(verb_list)
                svo_verb, negation_verb = verb_root(verb_list, token, sent_data)#processing
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
               
        elif (token["deprel"] == "ROOT" or token["deprel"] == "parataxis") and "NN" in token["pos"]:#Subject -> Verb(be) -> predicative nominative
            s, v, o = pred_root(token, gov_dict, sent_data)
            negation = negation_detect(token, sent_data)
            
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
        if acl_key != "":
        
            if isinstance(gov_dict[acl_key], list):
                id_list = gov_dict[acl_key]
                
            else:
                id_list = [gov_dict[acl_key]]
            for v_id in id_list:
                v_token = sent_data[v_id]
                if "VB" in v_token["pos"]:
                    CollectedVs.append(v_id)
                    svo_acl, negation_acl = verb_root([v_id], v_token, sent_data)
                    if len(svo_acl) != 0:
                        if svo_acl[0][0] == "Someone?":
                            #if the subject is missing in the dependency, the subject of the clausal modifier is the token that it modifies (syntactical head)
                            svo_acl[0][0] = token["word"]
                    SVO.extend(svo_acl)
                    N.extend(negation_acl)
 
    return SVO, L, T, T_S, P, N
            
                        
# Dec. 21
