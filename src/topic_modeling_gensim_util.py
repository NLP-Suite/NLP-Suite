#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 18:16:43 2020

@author: claude; completed by Wei Dai Spring 2021
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"topic_modeling_gensim_util.py",['nltk','os','tkinter','pandas','gensim','spacy','pyLDAvis','matplotlib','logging','IPython'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import pandas as pd
from pprint import pprint

#Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# necessary to avoid having to do Ctrl+C to kill pyLDAvis to continue running the code
from _thread import start_new_thread

#spacy for lemmatization
import spacy

#plotting tools
import pyLDAvis
import pyLDAvis.gensim
import matplotlib
matplotlib.use('TkAgg') # may be necessary for your system
import matplotlib.pyplot as plt

#enable logging for gensim
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)
import warnings 
warnings.filterwarnings("ignore",category=DeprecationWarning)

import IO_files_util
import IO_user_interface_util
import Excel_util
import reminders_util

#whether stopwordst were already downloaded can be tested, see stackoverflow
#	https://stackoverflow.com/questions/23704510/how-do-i-test-whether-an-nltk-resource-is-already-installed-on-the-machine-runni
#	see also caveats
# check stopwords
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')

from nltk.corpus import stopwords

#https://spacy.io/usage/models OTHER LANGUAGES ARE AVAILABLE; CHECK WEBSITE!
try:
    spacy.load('en_core_web_sm')
except:
    mb.showerror(title='Library error', message='The Gensim Topic modeling tool could not find the English language spacy library. This needs to be installed. At command promp type:\npython -m spacy download en_core_web_sm\n\nYOU MAY HAVE TO RUN THE COMMAND AS ADMINISTRATOR.\n\nHOW DO YOU DO THAT?'
        '\n\nIn Mac, at terminal, type sudo python -m spacy download en_core_web_sm'
        '\n\nIn Windows, click on left-hand start icon in task bar'
        '\n  Scroll down to Anaconda' 
        '\n  Click on the dropdown arrow to display available options'
        '\n  Right click on Anaconda Prompt'
        '\n  Click on More'
        '\n  Click on Run as Administrator'
        '\n  At the command prompt, Enter "conda activate NLP" (if NLP is your environment)'
        '\n  Then enter: "python -m spacy download en_core_web_sm" and Return'
        '\n\nThis imports the package.')
    sys.exit(0)


# find the optimal number of topics for LDA
def compute_coherence_values(MalletDir, dictionary, corpus, texts, start, limit, step):
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started computing the coherence value for each topic')
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                           'Computing coherence value for topic number ' + str(num_topics))
        model = gensim.models.wrappers.LdaMallet(MalletDir,corpus=corpus, num_topics=num_topics, id2word=dictionary)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished computing the coherence value for each topic')
    return model_list, coherence_values

# Finding the Dominance Topic in each sentence
def format_topics_sentences(ldamodel, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # =>  topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant topic', '% contribution', 'Topic keywords']

    # Add original text to the end of the output
# 	    print("Type of texts: ",type(texts))
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return sent_topics_df

def malletModelling(MalletDir, outputDir, createExcelCharts, corpus,num_topics, id2word,data_lemmatized, lda_model, data):
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running Mallet LDA topic modeling at',True)
    config_filename='topic-modeling-gensim-config.txt'
    try:
        ldamallet = gensim.models.wrappers.LdaMallet(MalletDir, corpus=corpus, num_topics=num_topics, id2word=id2word)
    except:
        routine_options = reminders_util.getReminder_list(config_filename)
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_gensim_release,
                                     reminders_util.message_gensim_release,
                                     True)
        routine_options = reminders_util.getReminder_list(config_filename)
        return

    # Show Topics
    pprint(ldamallet.show_topics(formatted=False))

    if num_topics>40:
        limit=40
    else:
        limit = num_topics

    # Compute Coherence value
    coherence_model_ldamallet = CoherenceModel(model=ldamallet, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Compute Mallet LDA coherence values for each topic.\n\nPlease, be patient...')
    coherence_ldamallet = coherence_model_ldamallet.get_coherence()
    print('\nCoherence value: ', coherence_ldamallet)
    model_list, coherence_values = compute_coherence_values(MalletDir, dictionary=id2word, corpus=corpus, texts=data_lemmatized, start=2, limit=limit, step=6)
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Compute graph of optimal topics number.')
    limit=limit; start=2; step=6;
    x = range(start, limit, step)
    plt.plot(x, coherence_values)
    plt.xlabel("Number of topics")
    plt.ylabel("Coherence value")
    plt.legend(("coherence_values"), loc='best')
    # plt.show()
    fileName=os.path.join(outputDir, "NLP_Gensim_optimal_topics_number.jpg")
    plt.savefig(fileName)
    filesToOpen.append(fileName)


    # Print the coherence values
    optimal_coherence = float("-inf")
    index = 0
    optimal_index = -1
    for m, cv in zip(x, coherence_values):
        coherence_value = round(cv, 4)
        if coherence_value > optimal_coherence:
            optimal_index = index
        print("Topic number", m, "has coherence value ", coherence_value)
        index += 1
    # Select the model and print the topics

    optimal_model = model_list[optimal_index]
    model_topics = optimal_model.show_topics(formatted=False)
    pprint(optimal_model.print_topics(num_words=10))

    # When you include a corpus that has \n symbol, the \n symbol, as stated by the csv standard, is treated as a "start a new row" symbol.
    # As a result, the corpus text takes up many rows and corrupts the csv file.
    # Note that \n symbol does not correspond to a new sentence. It is just a line breaker that makes the text easier to read.
    text: str
    for index, text in enumerate(data):
        data[index] = text.replace('\n', ' ')

    df_topic_sents_keywords = format_topics_sentences(ldamodel=optimal_model, corpus=corpus, texts=data)

    # Format
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document ID','Dominant topic', 'Topic % contribution', 'Topic keywords', 'Text']

    # Save csv file
    fileName=os.path.join(outputDir, "NLP_Gensim_dominant_topic.csv")
    df_dominant_topic.to_csv(fileName, index=False)
    filesToOpen.append(fileName)

    # columns_to_be_plotted = [[1, 3]]
    # hover_label = 'Topic_Keywords'
    # inputFilename = fileName
    # Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
    #                                           outputFileLabel='TM_Gensim',
    #                                           chart_type_list=["bar"],
    #                                           chart_title='Number of Documents per Topic',
    #                                           column_xAxis_label_var='Topic number',
    #                                           hover_info_column_list=hover_label)
    #
    # if Excel_outputFilename != "":
    #     filesToOpen.append(Excel_outputFilename)

    # Find the most representative document for each topic
    # Group top 5 sentences under each topic
    sent_topics_sorteddf_mallet = pd.DataFrame()

    sent_topics_outdf_grpd = df_topic_sents_keywords.groupby('Dominant topic')

    for i, grp in sent_topics_outdf_grpd:
        sent_topics_sorteddf_mallet = pd.concat([sent_topics_sorteddf_mallet,
                                             grp.sort_values(['% contribution'], ascending=[0]).head(1)],
                                            axis=0)

    # Reset Index
    sent_topics_sorteddf_mallet.reset_index(drop=True, inplace=True)

    # Format
    sent_topics_sorteddf_mallet.columns = ['Topic number', "Topic % contribution", "Topic keywords", "Text"]

    # Save csv file
    fileName=os.path.join(outputDir, "NLP_Gensim_representative_document.csv")
    sent_topics_sorteddf_mallet.to_csv(fileName,index=False)
    filesToOpen.append(fileName)

    # columns_to_be_plotted = [[1, 2]]
    # hover_label = 'Topic keywords'
    # inputFilename = fileName
    # Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
    #                                           outputFileLabel='TM_Gensim',
    #                                           chart_type_list=["bar"],
    #                                           chart_title='Percentage Contribution of Each Topic',
    #                                           column_xAxis_label_var='Topic number',
    #                                           hover_info_column_list=hover_label)
    #
    # if Excel_outputFilename != "":
    #     filesToOpen.append(Excel_outputFilename)

    # Topic distribution across documents
    # Number of Documents for Each Topic
    topic_counts = df_topic_sents_keywords['Dominant topic'].value_counts()
    print("Topic counts: ")
    print(topic_counts)
    print("Type of topic count: ")
    print(type(topic_counts))
    print()
    
    # Percentage of Documents for Each Topic
    topic_contribution = round(topic_counts/topic_counts.sum(), 4)
    print("Topic contribution: ")
    print(topic_contribution)
    print("Type of topic contribution: ")
    print(type(topic_contribution))
    print()
    
    # Topic Number and Keywords
    topic_num_keywords = df_topic_sents_keywords[['Dominant topic', 'Topic keywords']]

    # Concatenate Column wise
# 	df_dominant_topics = pd.concat([topic_num_keywords, topic_counts, topic_contribution], axis=1)
    
    # Change Column names

    df_dominant_topics = topic_num_keywords 

    num_row = df_dominant_topics.shape[0]
    topic_order_list = df_dominant_topics["Dominant topic"]
# 	print(topic_order_list)
# 	print(type(topic_order_list))
    num_docs = []
    perc_documents = []
# 	print()
    for i in range(num_row):
        topic = topic_order_list.get(i)
        num_docs.append(topic_counts.get(topic))
        perc_documents.append(topic_contribution.get(topic))
    df_dominant_topics["Number of documents"] = num_docs
    df_dominant_topics["% documents"] = perc_documents
    df_dominant_topics.columns = ['Dominant topic', 'Topic keywords', 'Number of documents', '% documents']

    # dominant_topics seems to create duplicate records; the .drop_duplicates() method will solve the problem
    df_dominant_topics.columns = ['Dominant topic', 'Topic keywords', 'Number of documents', '% documents']
    df_dominant_topics = df_dominant_topics.drop_duplicates()

    print("Number of rows of topic_distribution.csv: ", df_dominant_topics.shape[0])
    print("Number of columns of topic_distribution.csv: ", df_dominant_topics.shape[1])
    # Save csv file
    fileName=os.path.join(outputDir, "NLP_Gensim_topic_distribution.csv")
    df_dominant_topics.to_csv(fileName, index=False)
    filesToOpen.append(fileName)

    # columns_to_be_plotted = [[1, 2]]
    # hover_label = 'Topic keywords'
    # inputFilename = fileName
    # Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
    #                                           outputFileLabel='TM_Gensim',
    #                                           chart_type_list=["bar"],
    #                                           chart_title='Percentage Contribution of Each Topic',
    #                                           column_xAxis_label_var='Topic number',
    #                                           hover_info_column_list=hover_label)
    #
    # if Excel_outputFilename != "":
    #     filesToOpen.append(Excel_outputFilename)


    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Mallet LDA topic modeling at',True)

def run_Gensim(window, inputDir, outputDir, num_topics, remove_stopwords_var,
                                      lemmatize, nounsOnly, run_Mallet, openOutputFiles,createExcelCharts):
    global filesToOpen
    filesToOpen=[]

    numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
    if numFiles == 0:
        mb.showerror(title='Number of files error',
                     message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
        return
    elif numFiles == 1:
        mb.showerror(title='Number of files error', message='The selected input directory contains only ' + str(
            numFiles) + ' file of txt type.\n\nTopic modeling requires a large number of files to produce valid results. That is true even if the available file contains several different documents morged together.')
        return
    elif numFiles < 50:
        result = mb.askyesno(title='Number of files', message='The selected input directory contains only ' + str(
            numFiles) + ' files of txt type.\n\nTopic modeling requires a large number of files (in the hundreds at least; read TIPS file) to produce valid results.\n\nAre you sure you want to continue?',
                             default='no')
        if result == False:
            return

    IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start',
                                       'Started running Gensim Topic modeling at ', True,
                                       "Depending upon corpus size, computations may take a while... Please, be patient...")

    outputFilename = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.html', 'Gensim_topic_modeling')

    content = []
    for fileName in os.listdir(inputDir):
        if fileName.endswith('.txt'):
            with open(os.path.join(inputDir, fileName), 'r', encoding='utf-8', errors='ignore') as file:
                content.append(file.read())
            file.close()

    # TODO: read in the article title in stead of an arbitrary number (1 here)
    raw_data = {"title": 1, "content": content}

    df = pd.DataFrame(data=raw_data)

    data = df.content.values.tolist()

    stop_words = stopwords.words('english')
    # TODO: (optional) add more stop words that are common but unncesseary for topic modeling
    # stop_words.extend(['','']
    # 	stop_words = stopwords.words('english')
    stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

    # TODO: import data

    # tokenize, clean up, deacc true is removing the punctuation
    def sent_to_words(sentences):
        for sentence in sentences:
            yield (gensim.utils.simple_preprocess(str(sentence), deacc=True))

    data_words = list(sent_to_words(data))

    # Build the bigram and trigram models
    bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.
    trigram = gensim.models.Phrases(bigram[data_words], threshold=100)

    # Faster way to get a sentence clubbed as a trigram/bigram
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)

    # See trigram example
    # @print(trigram_mod[bigram_mod[data_words[0]]])

    # Define functions for stopwords, bigrams, trigrams and lemmatization
    def remove_stopwords(texts):
        return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

    def make_bigrams(texts):
        return [bigram_mod[doc] for doc in texts]

    def make_trigrams(texts):
        return [trigram_mod[bigram_mod[doc]] for doc in texts]

    def lemmatization(texts, lemmatize=True, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        """https://spacy.io/api/annotation"""
        texts_out = []
        for sent in texts:
            doc = nlp(" ".join(sent))
            if lemmatize:
                texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
            else:
                texts_out.append([token for token in doc if token.pos_ in allowed_postags])
        return texts_out

    # Remove Stop Words
    if remove_stopwords_var == True:
        data_words_nostops = remove_stopwords(data_words)
    else:
        data_words_nostops = data_words

    # Form Bigrams
    data_words_bigrams = make_bigrams(data_words_nostops)

    # Initialize spacy 'en_core_web_sm' model, keeping only tagger component (for efficiency)
    # Python -m spacy download en
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

    if nounsOnly == True:
        # Do lemmatization keeping only noun
        data_lemmatized = lemmatization(data_words_bigrams, lemmatize, allowed_postags=['NOUN'])
    else:
        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized = lemmatization(data_words_bigrams, lemmatize,
                                        allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

    # @print(data_lemmatized[:1])

    # Create Dictionary
    id2word = corpora.Dictionary(data_lemmatized)

    # Create Corpus
    texts = data_lemmatized

    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]

    # View
    # @print(corpus[:1])

    ########################################

    # good code on various parameters
    # https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/

    # Build LDA model
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                id2word=id2word,
                                                num_topics=num_topics,
                                                random_state=100,
                                                update_every=1,
                                                chunksize=100,
                                                passes=10,
                                                alpha='auto',
                                                per_word_topics=True)

    # Compute Perplexity; a measure of how good the model is. lower the better.
    print('\nPerplexity Score: ', lda_model.log_perplexity(corpus))

    # TODO the coherence lines produce an error
    # Compute Coherence Score
    # coherence_model_lda = CoherenceModel(model=lda_model, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
    # coherence_lda = coherence_model_lda.get_coherence()
    # print('\nCoherence Score: ', coherence_lda)

    # Print the Keywords in the topics
    # TODO visualize most relevant topics in Excel bar charts, with hover over of the words in each topic
    # step 13 of website

    # 	print("\n")
    # 	print("List of keywords and their weights for each of the " + str(num_topics) + " topics analyzed:")
    # 	print("\n")
    pprint(lda_model.print_topics())
    # 	print("Type of lda_model.print_topics(): ", type(lda_model.print_topics()))
    # 	print("\n\n")
    doc_lda = lda_model[corpus]
    # 	print("Type of doc_lda: ", type(doc_lda))
    # visualize and generate html
    # step 15 in website
    vis = pyLDAvis.gensim.prepare(lda_model, corpus, id2word)
    pyLDAvis.prepared_data_to_html(vis)
    try:
        pyLDAvis.save_html(vis, outputFilename)
    except:
        mb.showerror(title='Output html file error', message='Gensim failed to generate the html output file.')
        return

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Gensim topic modeling at',True,'\n\nThe file ' + outputFilename + ' was created. The results will display shortly on the web browser.')
    # \n\nYou now need to exit the server.\n\nAt command prompt, enter Ctrl+C, perhaps repeatedly, to exit the server.'

    # open and display on web
    def show_web(vis):
        pyLDAvis.display(vis)
        pyLDAvis.show(vis)
        pyLDAvis.kill()

    # necessary to avoid having to do Ctrl+C to kill pyLDAvis to continue running the code
    start_new_thread(show_web, (vis,))

    if run_Mallet==True:
        # check that the MalletDir as been setup
        MalletDir, missing_external_software = IO_libraries_util.get_external_software_dir('topic_modeling_gensim', 'Mallet')
        if MalletDir==None:
            return

        MalletDir = os.path.join(MalletDir, "bin/mallet")

        # building LDA Mallet Model
        malletModelling(MalletDir, outputDir, createExcelCharts, corpus, num_topics, id2word, data_lemmatized,
                                                   lda_model, data)
    
    if openOutputFiles==True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
            filesToOpen=[] # to avoid opening files twice, here and in calling function

    return filesToOpen