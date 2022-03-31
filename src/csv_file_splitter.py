# Tony Mar 24 2022

import pandas as pd
import os
import shutil
import IO_csv_util

# split the csv file by document ID
# should at least contain a colmun called 'Document ID'
# the script would group by it and then save them seperately
def split_NLP_Suite_csv_output_by_document_id(file_name):
    df = pd.read_csv(file_name)
    base_name = file_name[:-4] + "_Document_"
    grouped = df.groupby(['Document ID'])
    for name, group in grouped:
        group.to_csv(base_name + str(name) + '.csv', index=False)
    return


# split the corpus by document ID, should have a csv file output already, containing a column called 'Document ID'
# table: path to the NLP Suite output csv file
# id_list: a list of document ID  eg: '1,2,3'  split by ','
# corpus_location: the location of the corpus
# folder_name: the name of the folder to save the sub corpus
def split_corpus_by_document_id(table, id_list, corpus_location, folder_name):
    id_list = [int(s) for s in id_list.split(',')]
    data,header = IO_csv_util.get_csv_data(table, True)
    id_index = header.index('Document ID')
    doc_index = header.index('Document')
    target_dir = os.path.join(corpus_location, folder_name)
    for x in os.walk(corpus_location): # see if the folder exists
        if x[0] == target_dir:
            shutil.rmtree(target_dir) # remove the folder if already exists
    os.mkdir(target_dir) # create a folder for sub corpus
    for i in data:  # find the document id wanted
        if int(i[id_index]) in id_list:
            #copy the file, remove the hyperlink content from the document column
            shutil.copy2(os.path.join(corpus_location, i[doc_index][12:-2]), target_dir)
            #print(i[doc_index][14:-4])
            id_list.remove(int(i[id_index])) # no longer find for it
        if len(id_list) == 0:
            break
    return

#===============================================DEBUG USE=====================================================
# def main():
#     split_corpus_by_document_id("C:/Users/Tony Chen/Desktop/NLP_working/Test Input/conll_chn1.csv",'1,3', 
#     "C:/Users/Tony Chen/Desktop/NLP_working/Test Input/Chinese_Martens_stories_sections", "sub_corpus")

# if __name__ == "__main__":
#     main()