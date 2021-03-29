import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"wordclouds_util",['wordcloud','numpy','matplotlib','ntpath','PIL','csv'])==False:
    sys.exit(0)

# The script uses Andreas Christian Mueller WordCloud package
# https://amueller.github.io/word_cloud/

import numpy as np
from PIL import Image
import stanza
import pandas as pd
from collections import defaultdict
import tkinter.messagebox as mb

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator, get_single_color_func
import matplotlib.pyplot as plt #pip install matplotlib
import csv
import ntpath #to split the path from filename
import re

import IO_files_util
import IO_user_interface_util

def transform_format(val):
    if val == 0:
        return 255
    else:
        return val
    
class GroupedColorFunc(object):
    """Create a color function object which assigns DIFFERENT SHADES of
       specified colors to certain words based on the color to words mapping.

       Uses wordcloud.get_single_color_func

       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.color_func_to_words = [
            (self.get_single_color(color), set(words))
            for (color, words) in color_to_words.items()]

        self.default_color_func = self.get_single_color(default_color)

    def get_single_color(self, color):
        color = color[1:-1]
        color_list = color.split(", ")
        return 'rgb({:.0f}, {:.0f}, {:.0f})'.format(int(color_list[0]), int(color_list[1]), int(color_list[2]))

    def get_color_func(self, word):
        """Returns a single_color_func associated with the word"""
        try:
            color_func = next(
                color_func for (color_func, words) in self.color_func_to_words
                if word in words)
        except StopIteration:
            color_func = self.default_color_func

        return color_func

    def __call__(self, word, **kwargs):
        return self.get_color_func(word)

# for label separate column with separate color only
def processColorList(currenttext, color_to_words, csvField_color_list, myfile):
    cur_list = []
    column_color = {}

    for item in csvField_color_list:
        if item != '|':
            cur_list.append(item)
        else:
            for key in cur_list[:-1]:
                column_color[key] = cur_list[-1]
            cur_list = []

    reader = csv.DictReader(myfile)  # read rows into a dictionary format
    for row in reader:  # read a row as {column1: value1, column2: value2,...}
        for (k, v) in row.items():  # go over each column name and value
            if k in column_color:
                if " " in v:
                    color_to_words[column_color[k]] += ["".join(filter(str.isalnum, s)) for s in v.lower().split(" ")]
                else:
                    color_to_words[column_color[k]].append("".join(filter(str.isalnum, v.lower())))
                currenttext += v.lower() + " "
    return currenttext, color_to_words


def display_wordCloud_sep_color(doc, outputDir, text, color_to_words, transformed_image_mask):
    stopwords = set(STOPWORDS)
    if len(transformed_image_mask) != 0:
        wc = WordCloud(collocations=False,width = 800, height = 800, max_words=1000, stopwords = stopwords, mask=transformed_image_mask,
                       contour_width=3, contour_color='firebrick', background_color ='white').generate(text.lower())
    else:
        wc = WordCloud(collocations=False, width=800, height=800, max_words=1000, stopwords = stopwords, contour_width=3,
                        background_color='white').generate(text.lower())
    default_color = "(169, 169, 169)"
    grouped_color_func = GroupedColorFunc(color_to_words, default_color)
    wc.recolor(color_func=grouped_color_func)
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    output_file_name = IO_files_util.generate_output_file_name(doc, '', outputDir, '.png', 'WC', 'img')
    # plt.show()
    wc.to_file(output_file_name)
    return output_file_name

def display_wordCloud(doc,inputDir,outputDir,textToProcess,doNotListIndividualFiles,transformed_image_mask):
# def display_wordCloud(doc, outputDir,textToProcess,transformed_image_mask):

    comment_words = ' '
    stopwords = set(STOPWORDS)
    for val in textToProcess:
        # typecaste each val to string
        val = str(textToProcess)
    # split the value
    tokens = val.split()
    # Converts each token into lowercase and delete non alphabetic chars
    regex = re.compile('[^a-zA-Z]')
    for i in range(len(tokens)):
        tokens[i] = regex.sub('', tokens[i].lower())
    for words in tokens:
        comment_words = comment_words + words + ' '
    if len(transformed_image_mask)!=0:
        wordcloud = WordCloud(width = 800, height = 800,
                        background_color ='white',
                        max_words=1000,
                        mask=transformed_image_mask,
                        stopwords = stopwords,
                        contour_width=3,
                        contour_color='firebrick',
                        min_font_size = 10, collocations=False).generate(comment_words)
    else:
        wordcloud = WordCloud(width = 800, height = 800,
                        background_color ='white',
                        max_words=1000,
                        stopwords = stopwords,
                        contour_width=3,
                        min_font_size = 10, collocations=False).generate(comment_words)
    # plot the WordCloud image
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud,interpolation='bilinear')
    plt.axis("off")
    if doNotListIndividualFiles==True:
        plt.title(inputDir)
        output_file_name=IO_files_util.generate_output_file_name('', inputDir, outputDir, '.png', 'WC', 'img')
    else:
        plt.title(ntpath.basename(doc))
        output_file_name=IO_files_util.generate_output_file_name(doc, '', outputDir, '.png', 'WC', 'img')
    #title must be set before layout
    plt.tight_layout(pad = 0)
    # Save the image in the output folder
    wordcloud.to_file(output_file_name)
    return output_file_name

# check if file is empty
# 2 returned boolean the first one tells user that the program MUST exit; the second that a file is empty and processing moves to the next file
def check_file_empty(currenttext,doc,Ndocs,NumEmptyDocs):
    if len(currenttext) == 0:
        NumEmptyDocs=NumEmptyDocs+1
        if Ndocs == 1:
            mb.showerror(title='File empty', message='The file ' + doc + ' is empty.\n\nPlease, use another file and try again.')
            return True, True, NumEmptyDocs # must exit script
        else:
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Empty file',
                                               'The file ' + doc + ' is empty.')
        return False, True, NumEmptyDocs
    else:
        return False, False, NumEmptyDocs

def python_wordCloud(inputFilename, inputDir, outputDir, selectedImage, differentPOS_differentColors_checkbox, csvField_color_list, doNotListIndividualFiles,openOutputFiles):
    # https://www.geeksforgeeks.org/generating-word-cloud-python/
    # Python program to generate WordCloud
    # for a more sophisticated Python script see
    #   https://www.datacamp.com/community/tutorials/wordcloud-python
    #   they provide code to display wc in a selected image
    global filesToOpen
    filesToOpen=[]
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False)
    Ndocs=len(inputDocs)
    if Ndocs==0:
        return

    transformed_image_mask=[]

    if len(selectedImage)!=0:
        # In order to create a shape for your wordcloud, first, you need to find a PNG file to become the mask.
        # Not all mask images have the same format resulting in different outcomes, hence making the WordCloud function not working properly.
        # The way the masking functions works is that it requires all white part of the mask should be 255 not 0 (integer type). This value represents the "intensity" of the pixel. Values of 255 are pure white, whereas values of 1 are black. Here, you can use the provided function below to transform your mask if your mask has the same format as above. Notice if you have a mask that the background is not 0, but 1 or 2, adjust the function to match your mask.

        image_mask = np.array(Image.open(selectedImage))
        print("Image_mask (SHOULD ALL BE 0 VALUES)",image_mask)
        numberImages=len(image_mask.shape)
        # if i==1: #only print once
        print("\n\n\nnumberImages",numberImages)
        
        # Transform your mask into a new one that will work with the function:
        if numberImages==1:
            transformed_image_mask = np.ndarray((image_mask.shape[0]), np.int32)
        elif numberImages==2:
            transformed_image_mask = np.ndarray((image_mask.shape[0],image_mask.shape[1]), np.int32)
        elif numberImages==3:
            transformed_image_mask = np.ndarray((image_mask.shape[0],image_mask.shape[1],image_mask.shape[2]), np.int32)
        else:
            return
        for j in range(len(image_mask)):
            transformed_image_mask[j] = list(map(transform_format, image_mask[j]))
        # Check the expected result of your mask
        # if i==1: #only print once
        print("transformed_image_mask (SHOULD ALL BE 255 VALUES)",transformed_image_mask)
        
    if differentPOS_differentColors_checkbox==True:
        # RED for NOUNS, BLUE for VERBS, GREEN for and ADJECTIVES
        red_code = "(250, 0, 0)"
        blue_code = "(0, 250, 0)"
        green_code = "(0, 0, 250)"
        color_to_words = {
            red_code:[],#red/nouns
            blue_code:[],#blue/verbs
            green_code:[]#green/adjs
        }
        combinedtext = ''
        currenttext = ''
        i = 0
        stanza.download('en')#set the annotator that gives postag
        stannlp = stanza.Pipeline(lang='en', processors='tokenize,ner,mwt,pos,lemma')
        NumEmptyDocs = 0
        for doc in inputDocs:
            i = i+1
            # print(i)
            # print(type(doc))
            # print(doc)
            if doc[-4:]=='.csv':#processing CoNLL table that contains pos values
                try: 
                    df = pd.read_csv(doc)
                    postags_ = df['POStag']
                    forms_ = df['Form']
                    #text: summing tokens in each line together
                    currenttext = (" ").join(forms_)
                    combinedtext = combinedtext + currenttext
                    for j in range(len(forms_)):
                        # print("word: ", forms_[i])
                        # print("pos: ", postags_[i])
                        # RED for NOUNS, BLUE for VERBS, GREEN for and ADJECTIVES
                        if postags_[j][0] == "V":
                            color_to_words[blue_code].append(forms_[j])
                        elif len(postags_[j]) >= 2 and postags_[j][0:2] == "NN":
                            color_to_words[red_code].append(forms_[j])
                        elif len(postags_[j]) >= 2 and postags_[j][0:2] == "JJ":
                            color_to_words[green_code].append(forms_[j])
                    
                except: 
                      print(doc+ " is not a CoNLL table")
            elif doc[-4:]=='.txt':
                with open(doc, 'r', encoding='utf-8', errors='ignore') as myfile:
                    currenttext = myfile.read()
                    combinedtext = combinedtext + currenttext
                    # check for empty file
                    error, error2, NumEmptyDocs = check_file_empty(currenttext, doc, Ndocs, NumEmptyDocs)
                    if error:
                        return
                    if error2:
                        continue
                    annotated = stannlp(currenttext)
                    for sent_id in range(len(annotated.sentences)):
                        for word in annotated.sentences[sent_id].words:
                            # print("word: ", word.text)
                            # print("postag: ", word.pos)
                            # RED for NOUNS, BLUE for VERBS, GREEN for and ADJECTIVES
                            if word.pos == "NOUN":
                                color_to_words[red_code].append(word.text)
                            elif word.pos == "VERB":
                                color_to_words[blue_code].append(word.text)
                            elif word.pos == "ADJ":
                                color_to_words[green_code].append(word.text)
            if inputDir!='' and doNotListIndividualFiles==True:
                textToProcess=combinedtext
            else:
                textToProcess=currenttext
                # wordclouds_util.display_wordCloud(doc,inputDir,outputDir,textToProcess,doNotListIndividualFiles,transformed_image_mask)
                tempOutputfile=display_wordCloud_sep_color(doc, outputDir, textToProcess, color_to_words, transformed_image_mask)
                filesToOpen.append(tempOutputfile)
            if i == len(inputDocs) and len(inputDir) > 0:
                # print(color_to_words)
                # wordclouds_util.display_wordCloud(inputDir,inputDir,outputDir,textToProcess,True,transformed_image_mask)
                tempOutputfile=display_wordCloud_sep_color(doc, outputDir, textToProcess, color_to_words, transformed_image_mask)
                filesToOpen.append(tempOutputfile)

    else: # not using NN*, VB*, JJ* POS tags for different colors
        combinedtext = ''
        currenttext = ''
        color_to_words = defaultdict(list)
        i=0
        NumEmptyDocs = 0
        for doc in inputDocs:
            i=i+1
            print("Processing document", doc, "\n")
            #open the doc and create wordcloud
            with open(doc, 'r', encoding='utf-8', errors='ignore') as myfile:
                if len(csvField_color_list) == 0 or (inputDir!='' and doNotListIndividualFiles):
                     # do not need to color each column separately
                    currenttext = myfile.read()
                    combinedtext = combinedtext + currenttext
                else:
                    if len(csvField_color_list) != 0:
                        # process csvField_color_list
                        currenttext, color_to_words = processColorList(currenttext, color_to_words, csvField_color_list, myfile)
                # check for empty files
                error, error2, NumEmptyDocs=check_file_empty(currenttext,doc,Ndocs,NumEmptyDocs)
                if error:
                    return
                if error2:
                    continue

                if len(csvField_color_list) != 0:
                    display_wordCloud_sep_color(doc, outputDir, currenttext, color_to_words, transformed_image_mask)
                else:
                    if inputDir!='' and doNotListIndividualFiles==True:
                        textToProcess=combinedtext
                    else:
                        textToProcess=currenttext
                        tempOutputfile=display_wordCloud(doc,inputDir,outputDir,textToProcess,doNotListIndividualFiles,transformed_image_mask)
                        filesToOpen.append(tempOutputfile)
                    if i == len(inputDocs) and len(inputDir) > 0:
                        tempOutputfile=display_wordCloud(inputDir,inputDir,outputDir,textToProcess,True,transformed_image_mask)
                        filesToOpen.append(tempOutputfile)

    if len(combinedtext) < 1:
        print('All ' + str(NumEmptyDocs) + ' txt files in your input directory\n' + str(
            inputDir) + ' are empty.\n\nPlease, check your directory an try again.')
        mb.showerror(title='Files empty',
                     message='All ' + str(NumEmptyDocs) + ' txt files are empty in your input directory\n' + str(
                         inputDir) + '\n\nPlease, check your directory and try again.')
    if NumEmptyDocs > 0:
        mb.showerror(title='Empty file(s)',
                     message=str(NumEmptyDocs) + ' file(s) empty in the input directory\n' + str(
                         inputDir) + '\n\nFile(s) listed in command line. Please, make sure to check the file(s) content.')

    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

    # plt.show()
