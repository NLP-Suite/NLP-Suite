# Tony Mar 24 2022

import os
import re
import shutil
import tkinter.messagebox as mb
import pandas as pd

import IO_files_util

# sample the corpus by document ID, should have a csv file output already, containing a column called 'Document ID'
# table: path to the NLP Suite output csv file
# corpus_location: the location of the corpus
# folder_name: the name of the folder to save the sub corpus

import pandas as pd
import numpy as np
import os
import shutil
import IO_files_util

def sample_corpus_by_search_words_inFileName(window, inputDir, configFileName, keywords_inFilename):
    keywords_inFilename_list = [word.lstrip().rstrip() for word in keywords_inFilename.split(",")]
    SubSampleDir=IO_files_util.make_directory(inputDir+os.sep+'subcorpus_sample')
    inputDocs = IO_files_util.getFileList('', inputDir, fileType='.txt', silent=False, configFileName=configFileName)
    Ndocs = len(inputDocs)
    if Ndocs == 0:
        mb.showwarning(title='Warning',message='The selected input directory\n' + inputDir + '\ncontains no file of txt type. Routine aborted.')
        return
    else:
        docID=0
        Ncopies = 0
        for docName in inputDocs:
            docID = docID + 1
            head, tail = os.path.split(docName)
            print("Processing file " + str(docID) + "/" + str(Ndocs) + ' ' + tail)
            if any(substring in docName for substring in keywords_inFilename_list):
                Ncopies=Ncopies+1
                shutil.copy(docName,SubSampleDir)
        mb.showwarning(title='Warning',message=str(Ncopies) + ' files out of ' + str(Ndocs) + ' containing any of the keywords "' + keywords_inFilename + '" in the filename were copied from the input directory\n\n' + inputDir + ' \n\nto a subdirectory of the same directory labeled corpus_subsample.')
        # always open outputDir
        IO_files_util.openExplorer(window, inputDir)


def sample_corpus_by_document_id(table, inputDir, outputDir):
    data = pd.read_csv(table)
    try:
        print(data['Document'])
    except:
        mb.showwarning(title='Warning',
                       message="The selected csv INPUT file\n\n" + table + "\n\ndoes not contain the expected field header 'Document.'\n\nPlease, select the appropriate csv file and try again.")
        return
    # create a subdirectory of the output directory
    inputFilename = ''
    target_dir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='sampleDir', silent=True)
    if target_dir == '':
        return
    doc_loc = set(data['Document'])
    not_found = []
    for doc in doc_loc:
        try:
            shutil.copy2(os.path.join(inputDir, doc), target_dir)
        except FileNotFoundError:
            not_found.append(doc)
    if len(not_found)>0:
        pd.DataFrame(not_found).to_csv(os.path.join(target_dir, "unmatched files.csv"), encoding='utf-8', index=False)
        extra_msg = "\n\n" + str(len(not_found)) + " files were not found in the input directory and were not copied."
    else:
        extra_msg = ""
    mb.showwarning(title='Warning',
                   message="The sample function successfully copied " + str(len(doc_loc)) + " files to the sub-folder " + target_dir + extra_msg)
    return

#===============================================DEBUG USE=====================================================
# def main():
#     split_corpus_by_document_id("C:/Users/Tony Chen/Desktop/NLP_working/Test Input/conll_chn1.csv",'1,3',
#     "C:/Users/Tony Chen/Desktop/NLP_working/Test Input/Chinese_Martens_stories_sections", "sub_corpus")

# if __name__ == "__main__":
#     main()
