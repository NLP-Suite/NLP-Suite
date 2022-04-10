# Tony Mar 24 2022

import pandas as pd
import os
import shutil
import IO_csv_util
import IO_files_util

# split the csv file by document ID
# should at least contain a colmun called 'Document ID'
# the script would group by it and then save them seperately
def sample_corpus_by_document_id(table, corpus_location, folder_name):
    data = pd.read_csv(table)
    target_dir = os.path.join(corpus_location, folder_name)
    IO_files_util.make_directory(target_dir)
    #data = pd.DataFrame(data, columns=header)
    print(data['Document'])
    doc_loc = set(data['Document'])
    not_found = []
    for i in doc_loc:
        try:
            shutil.copy2(os.path.join(corpus_location, i), target_dir)
        except FileNotFoundError:
            not_found.append(i)
    pd.DataFrame(not_found).to_csv(os.path.join(target_dir, "unmatched files.csv"), index=False)
    return


# split the corpus by document ID, should have a csv file output already, containing a column called 'Document ID'
# table: path to the NLP Suite output csv file
# id_list: a list of document ID  eg: '1,2,3'  split by ','
# corpus_location: the location of the corpus
# folder_name: the name of the folder to save the sub corpus
def split_NLP_Suite_csv_output_by_document_id(file_name,outputDir):
    df = pd.read_csv(file_name)
    head, tail = os.path.split(file_name)
    base_name = tail[:-4] + "_Document_"
    grouped = df.groupby(['Document ID'])
    # create a subfolder in the output directory
    outputDir = os.path.join(outputDir, "splitted csv")
    IO_files_util.make_directory(outputDir)
    for name, group in grouped:
        outFilename = os.path.join(outputDir, base_name + str(name) + '.csv')
        group.to_csv(outFilename, index=False)
    mb.showwarning(title='Warning',
                   message="The 'split by Document ID' function created " + str(grouped.ngroups) + ' split csv files in the output directory ' + outputDir)
    return

#===============================================DEBUG USE=====================================================
def main():
    split_NLP_Suite_csv_output_by_document_id("C:/Users/Tony Chen/Desktop/NLP_working/Test Input/conll_chn1.csv", 
    "C:/Users/Tony Chen/Desktop/NLP_working/Test Input/Chinese_Martens_stories_sections")

if __name__ == "__main__":
    main()