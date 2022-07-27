import pandas as pd
import stanza

# extract SVO from regular Stanza Document
# input: Stanza Document
def extractSVO(doc):
    # output: svo_df
    svo_df = pd.DataFrame(columns={'Subject (S)','VERB (V)','Object (O)'})
    
    # object and subject constants
    OBJECT_DEPS = {"obj", "iobj", "dobj", "dative", "attr", "oprd"}
    SUBJECT_DEPS = {"nsubj", "nsubj:pass", "csubj", "agent", "expl"}

    # extraction of SVOs
    c = 0
    for sentence in doc.sentences:
        for word in sentence.words:
            tmp_head = sentence.words[word.head-1].deprel if word.head > 0 else "root"
            if word.deprel in SUBJECT_DEPS or tmp_head in SUBJECT_DEPS:
                svo_df.at[c, 'Subject (S)'] = word.text
            if word.pos=='VERB':
                svo_df.at[c, 'VERB (V)'] = word.text
            if word.deprel in OBJECT_DEPS or tmp_head in OBJECT_DEPS:
                svo_df.at[c, 'Object (O)'] = word.text
        c+=1
    
    return svo_df

# extract SVO from multilingual doc
# input: Stanza Document
def extractSVOMultilingual(doc):
    out_df = pd.DataFrame()
    dicts = []

    # stanza doc to dict
    for doc in stanza_doc:
        temp_svo = extractSVO(doc) # call extractSVO() function
        out_df = out_df.append(temp_svo)
    
    return out_df