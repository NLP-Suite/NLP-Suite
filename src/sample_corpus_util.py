# Tony Mar 24 2022

import os
import shutil
import tkinter.messagebox as mb
import pandas as pd

import IO_files_util

# sample the corpus by document ID, should have a csv file output already, containing a column called 'Document ID'
# table: path to the NLP Suite output csv file
# corpus_location: the location of the corpus
# folder_name: the name of the folder to save the sub corpus
def sample_corpus_by_document_id(table, corpus_location):
    data = pd.read_csv(table)
    try:
        print(data['Document'])
    except:
        mb.showwarning(title='Warning',
                       message="The selected csv INPUT file\n\n" + table + "\n\ndoes not contain the expected field header 'Document.'\n\nPlease, select the appropriate csv file and try again.")
        return
    target_dir = os.path.join(corpus_location, 'sampleDir')
    createDir = IO_files_util.make_directory(target_dir,True)
    if not createDir:
        return
    doc_loc = set(data['Document'])
    not_found = []
    for doc in doc_loc:
        try:
            shutil.copy2(os.path.join(corpus_location, doc), target_dir)
        except FileNotFoundError:
            not_found.append(doc)
    if len(not_found)>0:
        pd.DataFrame(not_found).to_csv(os.path.join(target_dir, "unmatched files.csv"), index=False)
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