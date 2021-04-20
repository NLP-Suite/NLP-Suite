import codecs # must be installed
import csv
import os
from tkinter import messagebox
import numpy as np
from sklearn.decomposition import PCA
import pandas as pd #Angel
import IO_csv_util #Angel

"""
Name of variables should follow python notation: 
i.e. class names: CamelNotation, variable names: like_this

if possible have a look at google python coding guidelines: http://google.github.io/styleguide/pyguide.html
"""


class Vectorizer:
    def __init__(self, input_folder, window_size=5):
        self.data_folder = input_folder
        self.window_size = window_size
        self.narrative_file_paths = self.parse_input_data()
        self.sentiment_vector_size = 10
        self.min_doc_len, self.max_doc_len, self.avg_doc_len, self.doc_len = self.compute_min_max_doc_len()

        if self.window_size >= self.min_doc_len:
            self.window_size = self.min_doc_len - 1
        if self.sentiment_vector_size > self.min_doc_len:
            self.sentiment_vector_size = self.min_doc_len
        self.ideal_sent_v_size = int(self.avg_doc_len / self.window_size)
        if self.ideal_sent_v_size > self.sentiment_vector_size:
            self.ideal_sent_v_size = self.sentiment_vector_size


    def compute_min_max_doc_len(self):
        doclengths = []
        doNotRepeat=False
        filesToDelete = []
        addedFiles = []

        for narrativeNum, narrativeFile in enumerate(self.narrative_file_paths):
            with codecs.open(narrativeFile, mode='r', encoding='utf-8', errors='ignore') as csv_file:
                reader = csv.DictReader(csv_file)
                readerList = list(reader)
                df = pd.read_csv(narrativeFile, encoding='utf-8') #ANGEL
                if len(readerList) == 0 or "Sentiment score" not in df.columns:
                    messagebox.showwarning(title='Sentiment Analysis Score Error',
                                   message= "The file " + narrativeFile + " doesn't have any sentiment score.\n\n"
                                   + "The file will be dropped from the analyses.")
                    filesToDelete.append(narrativeFile)
                    continue
                #==============A================= added additional checks for merged file
                elif 'Document' in df.columns or 'Document Name' in df.columns: # a merged file
                    print(len(self.narrative_file_paths))
                    if 'Document Name' in df.columns:  # sometimes "Document" sometimes "Document Name"
                        df["Document"] = df["Document Name"]
                    doc_ls = [y for y,x in df.groupby(df["Document"])]
                    splitted = [x for _, x in df.groupby(df["Document"])]
                    for index,sub_df in enumerate(splitted):
                        if len(sub_df) == 1:
                            messagebox.showwarning(title='Sentiment Analysis Score Error',
                                               message="Document:" + doc_ls[index] + " only contains one sentiment score.\n\n"
                                                       + "This document will be dropped from the analyses.")
                            doNotRepeat = messagebox.askyesno("Python","Please, do NOT show this message again for any similar subsequent warning?")
                            splitted.pop(index)
                            continue #won't add to doclengths list
                        elif len(sub_df) < 10:
                            if doNotRepeat == False:
                                # TODO should export csv file with culprit files
                                result = messagebox.askyesno("Sentiment Analysis Score Error",
                                                             "Document " + doc_ls[index] +
                                                             " contains less than 10 sentiment scores.\n\n" +
                                                             "The document is too short compared to others in the corpus. It might influence the analysis of shape of stories.\n\n" +
                                                             "Would you like to drop this document from the analyses?")
                                doNotRepeat = messagebox.askyesno("Python","Please, do NOT show this message again for any similar subsequent warning?")
                            if result:
                                splitted.pop(index)
                                continue
                        doclengths.append(len(sub_df))
                    re_merged=pd.concat(splitted, ignore_index=True)
                    addedFiles.append((str(IO_csv_util.undressFilenameForCSVHyperlink(narrativeFile))[:-4]+".csv",re_merged))#save to regenerate later
                    filesToDelete.append(narrativeFile) #delete original merged file
                #==============end of A===============
                else: #not a merged file
                    if len(readerList) == 1:
                    # IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Sentiment Analysis Score Error',
                    #                                    message="The file " + narrativeFile + " only contains one sentiment score.\n\n"
                    #                                            + "The file will be dropped from the analyses.")
                        if doNotRepeat==False:
                        # TODO should export csv file with culprit files
                            messagebox.showwarning(title='Sentiment Analysis Score Error',
                                       message="The file " + narrativeFile + " only contains one sentiment score.\n\n"
                                               + "The file will be dropped from the analyses.")
                            doNotRepeat = messagebox.askyesno("Python","Please, do NOT show this message again for any similar subsequent warning?")
                        filesToDelete.append(narrativeFile)
                        continue
                    elif len(readerList) < 10:
                        if doNotRepeat==False:
                            # TODO should export csv file with culprit files
                            result = messagebox.askyesno("Sentiment Analysis Score Error", "The file " + narrativeFile +
                                                     " contains less than 10 sentiment scores.\n\n" +
                                                     "The file is too short compared to others in the corpus. It might influence the analysis of shape of stories.\n\n" +
                                                     "Would you like to drop this file from the analyses?")
                            doNotRepeat = messagebox.askyesno("Python",
                                                      "Please, do NOT show this message again for any similar subsequent warning?")
                        if result:
                            filesToDelete.append(narrativeFile)
                            continue
                # elif len(readerList) > 75:
                #     result = messagebox.askyesno("Sentiment Analysis Score Error", "The file " + narrativeFile +
                #                                  " contains more than 75 sentiment scores.\n" +
                #                                  "This text is too long compared to others. " +
                #                                  "It might influence the analysis of shape of stories.\n" +
                #                                  "Would you like to drop this file from the analyses?")
                #     if result:
                #         self.narrative_file_paths.remove(narrativeFile)
                #         continue
                    doclengths.append(len(readerList))

        # Remove the files that did not match specified criteria
        for f in filesToDelete:
            self.narrative_file_paths.remove(f)
        for a in addedFiles:#A
            a[1].to_csv(a[0],index=False)#A
            self.narrative_file_paths.append(a[0])#A
        return min(doclengths), max(doclengths), np.mean(np.array(doclengths)), len(doclengths)

    def parse_input_data(self):

        if os.path.isfile(self.data_folder):
            narrative_fps = [self.data_folder]
        else:
            narrative_fps = [os.path.join(self.data_folder, f) for f in os.listdir(self.data_folder) if
                             os.path.isfile(os.path.join(self.data_folder, f)) and not f.startswith(r'.')]
        return narrative_fps

    def vectorize(self):
        files_lengths = []
        narratives = []
        sentimentVectors = []
        file_list = []

        #===========================A====================================================
        scoresFile_list = {}
        #Create a list of input dataframes to standardize inputDir and inputFile
        with codecs.open(self.narrative_file_paths[0], mode='r', encoding='utf-8', errors='ignore') as nF1:
            merged_df = pd.read_csv(nF1,encoding='utf-8')
        #Add sentimentscores Filenames as a column
        merged_df["scoresFilename"] = [self.narrative_file_paths[0]]*merged_df.shape[0]
        if 'Document' not in merged_df.columns and 'Document Name' in merged_df.columns:# sometimes "Document" sometimes "Document Name"
            merged_df["Document"]=merged_df["Document Name"]
        if("Document" in merged_df): #a merged file
            df_list=[x for _,x in merged_df.groupby(merged_df['Document ID'])]
        else:
            df_list=[merged_df]
            for narrativeNum, narrativeFile in enumerate(self.narrative_file_paths, start=1):
                if narrativeNum>1:
                    with codecs.open(narrativeFile, mode='r', encoding='utf-8', errors='ignore') as narrativeFile1:
                        dfff=pd.read_csv(narrativeFile1,encoding='utf-8')
                        dfff["scoresFilename"] =[narrativeFile]*dfff.shape[0]
                        if 'Document' not in dfff.columns:  #sometimes "Document" sometimes "Document Name"
                            dfff["Document"] = dfff["Document Name"]
                        df_list.append(dfff)

        for df in df_list:
                if len(df)<self.sentiment_vector_size:
                    continue
                df.reset_index(inplace=True)
                # =================================End of A===============================================
                sentimentVector = []
                addIndex = int(len(df) / self.sentiment_vector_size) #number of rows per bucket
                files_lengths.append(len(df))
                bucket = self.sentiment_vector_size # always 10 buckets
                window = [float(row["Sentiment score"]) for i, row in df.iterrows() if
                            i < self.window_size]  # take the first [window_size] records and get the sentiment score
                for i, row in df.iterrows():
                    if i >= (self.window_size - 1):
                        # if get out of window_size: slide the window to next bucket
                        if i + 1 < len(df):
                            window.append(float(df.iloc[i + 1]['Sentiment score']))
                            del window[0]
                    try:
                        # Divides left hand operand by right hand operand and returns remainder
                        mod = i % addIndex #decides which bucket the row goes into
                    except:
                        pass
                    if mod == 0 and bucket > 0:
                        bucket -= 1 #go to the next bucket
                        sentimentVector.append((sum(window) / len(window)))
                sentimentVectors.append(sentimentVector)  # hold representative of each file
                file_list.append(df.iloc[0]['Document']) # append document name
                scoresFile_list.update({str(df.iloc[0]['Document']):str(df.iloc[0]['scoresFilename'])})#ANGEL
        sentimentVectors = np.array(sentimentVectors)
        # print('Minumum number of sentences in a document: %d' % min(files_lengths))
        # print('shortest doc: %d' % np.argmin(np.array(files_lengths)))
        print(sentimentVectors)
        return sentimentVectors, file_list,scoresFile_list


    @staticmethod
    def compute_suggested_n_clusters(sentiment_vectors, expl_var_thr=0.9):
        n_features = len(sentiment_vectors[0])
        pca = PCA(n_components=n_features)

        if len(sentiment_vectors)<n_features:
            messagebox.showwarning(title='Corpus size error',
                           message='The corpus you have selected is too small for data reduction algorithms. These algorithms require a LARGE number of files.\n\nPlease, select a different corpus directory and try again.')
            return None
        pca.fit(sentiment_vectors)
        expl_vars = -np.sort(-pca.explained_variance_ratio_)
        sum = 0
        for i in range(len(expl_vars)):
            sum += expl_vars[i]
            if sum >= expl_var_thr:
                return i
        print(n_features)
        return n_features


def test():
    sentiment_scores_folder = 'C:\\Users\\angel\\NLP\\New_SAscores_folder'


    vectz = Vectorizer(sentiment_scores_folder)
    sentiment_vectors = vectz.vectorize()
    rec_n_clusters = vectz.compute_suggested_n_clusters(sentiment_vectors, )
    print('The recommended number of clusters is: %d' % rec_n_clusters)
    print('ok')


if __name__ == '__main__':
    # sentiment_scores_folder = sys.argv[1]
    test()
