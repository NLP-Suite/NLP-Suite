# Tony Mar 24 2022

import os
import shutil
import tkinter.messagebox as mb

import IO_files_util
import IO_csv_util

# sample the corpus by document ID, should have a csv file output already, containing a column called 'Document ID'
# table: path to the NLP Suite output csv file
# corpus_location: the location of the corpus
# folder_name: the name of the folder to save the sub corpus
def sample_corpus_by_document_id(table, corpus_location, folder_name):
    data,header = IO_csv_util.get_csv_data(table, True)
    target_dir = os.path.join(corpus_location, folder_name)
    IO_files_util.make_directory(target_dir)
    doc_loc = set(data['Document'])
    not_found = []
    for i in doc_loc:
        try:
            shutil.copy2(os.path.join(corpus_location, i['Document'][12:-2]), target_dir)
        except FileNotFoundError:
            not_found.append(i['Document'][12:-2])
    return

#===============================================DEBUG USE=====================================================
# def main():
#     split_corpus_by_document_id("C:/Users/Tony Chen/Desktop/NLP_working/Test Input/conll_chn1.csv",'1,3', 
#     "C:/Users/Tony Chen/Desktop/NLP_working/Test Input/Chinese_Martens_stories_sections", "sub_corpus")

# if __name__ == "__main__":
#     main()