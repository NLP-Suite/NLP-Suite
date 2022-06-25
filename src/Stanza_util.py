import stanza
import pandas as pd
import tkinter.messagebox as mb
import os

import IO_files_util
import IO_csv_util
import file_splitter_merged_txt_util
import file_splitter_ByLength_util
import GUI_util
import IO_user_interface_util

# Stanza annotate functions
def Stanza_annotate(config_filename, inputFilename, inputDir,
                    outputDir,
                    openOutputFiles, createCharts, chartPackage,
                    annotator_params,
                    DoCleanXML,
                    language,
                    memory_var,
                    document_length=90000,
                    sentence_length=1000,
                    print_json = True,
                    **kwargs):

    language_encoding = 'utf-8'
    filesToOpen = []

    output_format_option = {
        'DepRel': ["ID", "Form", "Head", "DepRel", "Record ID", "Sentence ID", "Document ID", "Document"]
    }
    for annotator in annotator_params:
        # TODO MINO must expand the check for the allowed combinations of annotator and language
        if language=='Latin' and annotator=='NER':
            mb.showinfo("Warning",
                        "Stanza does not currently support the " + annotator + " annotator for " + language + ".\n\nPlease, select a different annotator or a different language.")
            return filesToOpen
        # routine = routine_option.get(annotator)
        output_format = output_format_option.get(annotator)

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Stanza at',
                                                 True, '', True, '', True)


    # decide on directory or single file
    if inputDir != '':
        inputFilename = inputDir


    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    if nDocs==0:
        return filesToOpen

    # annotating each input file
    docID=0
    recordID = 0
    filesError=[]
    # json = True
    errorFound=False
    total_length = 0
    # record the time consumption before annotating text in each file
    processing_doc = ''

    if "Lemma"  in annotator_params:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,lemma', verbose=False)
    elif "NER" in annotator_params:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,ner',  verbose=False)
    elif "All POS" in annotator_params:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,pos', verbose=False)
    # elif "sentiment" in annotator_params:
    #     nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')
    elif "depparse" in annotator_params:
        nlp = stanza.Pipeline('en', processors='tokenize,ner,mwt,pos,lemma,depparse', verbose=False)

    df = pd.DataFrame()
    for docName in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(docName)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        docTitle = os.path.basename(docName)
        sentenceID = 0
        # if ("SVO" in annotator_params or "OpenIE" in annotator_params) and "coref" in docName.split("_"):
        #     split_file = file_splitter_merged_txt_util.run(docName, "<@#", "#@>", outputDir)
        #     if len(split_file)>1:
        #         split_file = IO_files_util.getFileList("", split_file[0], fileType=".txt")
        if "Sentence" in annotator_params:
            split_file = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,config_filename,docName,'',document_length)
        else:
            split_file = []
            split_file.append(docName)

        nSplitDocs = len(split_file)
        split_docID = 0
        
        for doc in split_file:
            split_docID = split_docID + 1
            head, tail = os.path.split(doc)
            
            if docName != doc:
                print("   Processing split file " + str(split_docID) + "/" + str(nSplitDocs) + ' ' + tail)
            # else:
            #     print("   Processing a file " + str(split_docID) + "/" + str(nSplitDocs) + ' ' + tail)

            text = open(doc, 'r', encoding=language_encoding, errors='ignore').read().replace("\n", " ")
            
            if "%" in text:
                text=text.replace("%","percent")

            Stanza_output = nlp(text)

            outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,'.csv',
                                                                              'Stanza_'+'DepRel'+'_'+annotator_params)
            filesToOpen.append(outputFilename)

            temp_df = convertStanzaDoctoDf(Stanza_output, inputFilename, annotator_params)
            df = pd.concat([df, temp_df], ignore_index=True, axis=0)
            # df = df.reset_index(drop=True)
            if len(inputDocs) == docID:
                df.to_csv(outputFilename, index=False, encoding = language_encoding)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Stanza ' + str(annotator_params) + ' annotator at', True, '', True, startTime, True)

    return filesToOpen

# Convert Stanza doc to pandas Dataframe
def convertStanzaDoctoDf(stanza_doc, inputFilename, annotator_params):
    dicts = stanza_doc.to_dict()
    out_df = pd.DataFrame()
    
    for i in range(len(dicts)):
        temp_df = pd.DataFrame.from_dict(dicts[i])
        out_df = out_df.append(temp_df)

    out_df = out_df.drop(
        ['xpos', 'start_char', 'end_char', 'multi_ner', 'feats'],
        axis=1,
        errors='ignore'
        )
    out_df = out_df.reset_index(drop=True)
    
    if annotator_params == 'depparse':
        out_df.columns = [ 
            "ID",
            "Form",
            "Lemma",
            "POStag",
            "Head",
            "DepRel",
            "NER",
                        ]
    elif annotator_params == 'Lemma':
        out_df.columns = [ 
            "ID",
            "Form",
            "Lemma",
                        ]
    elif annotator_params == 'NER':
        out_df.columns = [ 
            "ID",
            "Form",
            "NER",
                        ]
    elif annotator_params == 'All POS':
        out_df.columns = [ 
            "ID",
            "Form",
            "POStag",
                        ]
    out_df['Record ID'] = None
    out_df['Sentence ID'] = None
    out_df['Document ID'] = 1
    out_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

    i = 0
    sidx = 1
    for row in out_df.iterrows():
        if i != 0 and row[1]['ID'] == 1 :
            sidx+=1
        
        out_df.at[i, 'Record ID'] = row[1]['ID']
        out_df.at[i, 'Sentence ID'] = sidx
        
        i+=1

    return out_df