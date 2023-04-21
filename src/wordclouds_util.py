# written by Cynthia Dong November 2019
# edited by Tony Chen Gu Spring 2022

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"wordclouds_util",['wordcloud','numpy','matplotlib','ntpath','PIL','stanza','csv'])==False:
    sys.exit(0)

# The script uses Andreas Christian Mueller WordCloud package
# https://amueller.github.io/word_cloud/

import os
from collections import Counter
import numpy as np
from PIL import Image

import pandas as pd
from collections import defaultdict
import tkinter.messagebox as mb
import stanza
try:
    stanza.download('en')
except:
    import IO_internet_util
    IO_internet_util.check_internet_availability_warning("wordclouds_util.py (stanza.download(en))")
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator, get_single_color_func
import matplotlib.pyplot as plt #pip install matplotlib
import csv
import ntpath #to split the path from filename

import IO_files_util
import IO_user_interface_util

#written by Tony Chen Gu Feb 22, 2022
#this function is to tell whether the machine is Mac or Windows
def get_os_type():
    if os.name == 'posix':
        return 'Mac'
    else:
        return 'Windows'

#get the font installation location on the machine base on the OS
def get_font_installed():
    os_type = get_os_type()
    if os_type == 'Mac':
        #location where Mac OS X stores the fonts
        font_path = '/Library/Fonts/'
    else:
        #location where Windows stores the fonts
        font_path = 'C:/Windows/Fonts/'
    return font_path

#get list of font installed on the machine
def get_font_list():
    font_list = os.listdir(get_font_installed())
    #the Default should be the first font in the list
    #it means not specifying any font for the python wordcloud, the font_path will be set to None
    font_list = [font[:-4] for font in font_list if font.endswith('.ttf') or font.endswith('.otf') or font.endswith('.TTF') or font.endswith('.OTF')]
    font_list.insert(0, 'Default')
    return font_list

#when users select the font, try both ttf and otf
#if none of them works, use the default font
#TODO: should give a error message (pop up window) telling them the font file is lost, using default now
def get_font_path(font):
    if font == 'Default':
        return None
    font_list = os.listdir(get_font_installed())
    word_len = len(font)
    for item in font_list:
        if item[:word_len] == font:
            return item
    #return none if none of the file matches the font
    #should give a error here
    return None

#Added by Tony
#change the transparent pixel to white
#user could use the website such as https://www.remove.bg/ to remove the background
#They could Google for remove background
def changeTransparentToWhite(img):
    '''
    :param img: the Image to be changed
    :return: the Image with transparent pixel changed to white
    '''
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[3] == 0: #if alpha value is zero, it is transparent
            newData.append((255, 255, 255, 255))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

def changeWhiteToTransparent(img):
    '''
    :param img: the Image to be changed
    :return: the Image with white pixel changed to transparent'''
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255: #if it is white
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

#Do Not Needed
'''
def transform_format(val):
    val = np.where(val == 0, 255 , val)
    return val
'''

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

# CYNTHIA: wordcloud function particularly designed for SVO
def SVOWordCloud(svoFile, inputFilename, outputDir, transformed_image_mask, prefer_horizontal):
    # read SVO result in
    svo_df = pd.read_csv(svoFile, encoding='utf-8',on_bad_lines='skip')
    svo_df = svo_df.fillna("")
    words_list = []
    # RGB color codes: red for S, blue for V, green for O
    red_code = "(250, 0, 0)"
    blue_code = "(0, 0, 250)"
    green_code = "(0, 250, 0)"
    default_code = "(169, 169, 169)" # grey
    color_list = {
        red_code: [],
        blue_code: [],
        green_code: []
    }
    for _, row in svo_df.iterrows():
        if row["Subject (S)"] != "":
            # check if the strings contains special character
            words_list.append(" ".join(["".join(filter(str.isalnum, s)) for s in row["Subject (S)"].lower().split(" ")]))
            color_list[red_code].append(" ".join(["".join(filter(str.isalnum, s)) for s in row["Subject (S)"].lower().split(" ")]))
        if row["Verb (V)"] != "":
            words_list.append(" " + (" ".join(["".join(filter(str.isalnum, s)) for s in row["Verb (V)"].lower().split(" ")])))
            color_list[blue_code].append(" " + (" ".join(["".join(filter(str.isalnum, s)) for s in row["Verb (V)"].lower().split(" ")])))
        if row["Object (O)"] != "":
            words_list.append((" ".join(["".join(filter(str.isalnum, s)) for s in row["Object (O)"].lower().split(" ")])) + " ")
            color_list[green_code].append((" ".join(["".join(filter(str.isalnum, s)) for s in row["Object (O)"].lower().split(" ")])) + " ")
    words_count_dict = Counter(words_list)
    # print (words_count_dict)
    max_words = 1000 # TODO MINO: make max_words bigger to include generally lower frequency "Object (O)" words
    if len(transformed_image_mask) != 0:
        wc = WordCloud(width = 800, height = 800, max_words=max_words, prefer_horizontal=prefer_horizontal, mask=transformed_image_mask,
                       contour_width=3, contour_color='firebrick', background_color ='white').generate_from_frequencies(words_count_dict)
    else:
        wc = WordCloud(width=800, height=800, max_words=max_words, prefer_horizontal=prefer_horizontal, contour_width=3,
                        background_color='white').generate_from_frequencies(words_count_dict)
    grouped_color_func = GroupedColorFunc(color_list, default_code)
    wc.recolor(color_func=grouped_color_func)
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    output_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.png', 'WC', 'img')
    wc.to_file(output_file_name)
    return output_file_name



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

# add bg_image_flag parameter to indicate whether to add background image
def display_wordCloud_sep_color(inputFilename, outputDir, text, color_to_words, transformed_image_mask,collocation,prefer_horizontal, bg_image = None,bg_image_flag = False, font = None, max_words = 100):
    # stopwords dealt with in main function
    stopwords=''
    c_wid = 0 if bg_image_flag else 3
    if len(transformed_image_mask) != 0:
        wc = WordCloud(collocations=collocation,width = 800, height = 800, max_words=max_words, prefer_horizontal=prefer_horizontal, stopwords = stopwords, mask=transformed_image_mask,
                       contour_width=c_wid, contour_color='firebrick', background_color ='white', font_path = font).generate(text)
    else:
        wc = WordCloud(collocations=collocation, width=800, height=800, max_words=max_words,prefer_horizontal=prefer_horizontal,stopwords = stopwords, contour_width=c_wid,
                        background_color='white', font_path = font).generate(text)
    default_color = "(169, 169, 169)" # dark grey; black is 0,0,0
    grouped_color_func = GroupedColorFunc(color_to_words, default_color)
    wc.recolor(color_func=grouped_color_func)
    plt.figure(figsize = (8, 8), facecolor = None)
    output_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.png', 'WC', 'img')
    if bg_image_flag and bg_image is not None:
        img = changeWhiteToTransparent(wc.to_image())
        img = img.resize(bg_image.size)
        img = Image.alpha_composite(bg_image, img)
        plt.imshow(img,interpolation='bilinear')
        plt.axis("off")
        #title must be set before layout
        plt.tight_layout(pad = 0)
        # Save the image in the output folder
        plt.figure()
        plt.axis('off')
        fig = plt.imshow(img, interpolation='nearest')
        plt.savefig(output_file_name,
                    bbox_inches='tight',
                    pad_inches=0,
                    format='png',
                    dpi=300)
    else:
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        wc.to_file(output_file_name)
    return output_file_name

def display_wordCloud(inputFilename,inputDir,outputDir,textToProcess,doNotListIndividualFiles,transformed_image_mask, collocation, prefer_horizontal,bg_image = None, bg_image_flag = True, font = None, max_words=100):
    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='wordcloud',
                                                       silent=True)
    if outputDir == '':
        return

    comment_words = ' '
    # stopwords = set(STOPWORDS)
    # for val in textToProcess:
    #     # typecaste each val to string
    #     val = str(textToProcess)
    # # split the value
    # tokens = val.split()
    # # Converts each token into lowercase and delete non alphabetic chars
    # regex = re.compile('[^a-zA-Z]')
    # for i in range(len(tokens)):
    #     tokens[i] = regex.sub('', tokens[i].lower())
    # for words in tokens:
    #     comment_words = comment_words + words + ' '
    c_wid = 0 if bg_image_flag else 3
    if len(transformed_image_mask)!=0:
        wordcloud = WordCloud(width = 800, height = 800,
                        background_color ='white',
                        max_words=100,
                        mask=transformed_image_mask,
                        prefer_horizontal=prefer_horizontal,
                        # stopwords = stopwords,
                        contour_width=c_wid,
                        contour_color='firebrick',
                        #min_font_size = 10, collocations=collocation).generate(comment_words)
                        #min_font_size = 10, collocations=collocation).generate(textToProcess)
                        collocations = collocation,
                        font_path = font).generate(textToProcess)
    else:
        wordcloud = WordCloud(width = 800, height = 800,
                        background_color ='white',
                        max_words=max_words,
                        prefer_horizontal=prefer_horizontal,
                        # stopwords = stopwords,
                        contour_width=c_wid,
                        #min_font_size = 10, collocations=collocation).generate(comment_words)
                        #min_font_size = 10, collocations = collocation).generate(textToProcess)
                        collocations = collocation,
                        font_path = font).generate(textToProcess)
    if doNotListIndividualFiles==True:
        plt.title(inputDir)
        output_file_name=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.png', 'WC', 'img')
    else:
        plt.title(ntpath.basename(inputFilename))
        output_file_name=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.png', 'WC', 'img')
    # plot the WordCloud image
    plt.figure(figsize = (8, 8), facecolor = None)
    if bg_image_flag and bg_image is not None:
        img = changeWhiteToTransparent(wordcloud.to_image())
        img = img.resize(bg_image.size)
        img = Image.alpha_composite(bg_image, img)
        plt.imshow(img,interpolation='bilinear')
        plt.axis("off")
        #title must be set before layout
        plt.tight_layout(pad = 0)
        # Save the image in the output folder
        plt.figure()
        plt.axis('off')
        fig = plt.imshow(img, interpolation='nearest')
        plt.savefig(output_file_name,
                    bbox_inches='tight',
                    pad_inches=0,
                    format='png',
                    dpi=300)
    else:
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        wordcloud.to_file(output_file_name)
    return output_file_name

# check if file is empty
# 2 returned boolean
#   the first one tells user that the program MUST exit;
#   the second that a file is empty and processing moves to the next file
def check_file_empty(currenttext,inputFilename,nDocs,NumEmptyDocs):
    if len(currenttext) == 0:
        NumEmptyDocs=NumEmptyDocs+1
        if nDocs == 1:
            mb.showerror(title='File empty', message='The file ' + inputFilename + ' is empty.\n\nPlease, use another file and try again.')
            return True, True, NumEmptyDocs # must exit script
        else:
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Empty file',
                                               'The file ' + inputFilename + ' is empty.')
        return False, True, NumEmptyDocs
    else:
        return False, False, NumEmptyDocs

#Modified by Tony 01/23/2022  add bg_image and bg_image_flag
def processCsvColumns(inputFilename, inputDir, outputDir, openOutputFiles,csvField_color_list, doNotListIndividualFiles, bg_image=None, bg_image_flag=False):
    transformed_image_mask=[]
    collocation=False
    prefer_horizontal=.9
    currenttext = ''
    color_to_words = defaultdict(list)
    with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as myfile:
        if len(csvField_color_list) != 0:
            # process csvField_color_list
            currenttext, color_to_words = processColorList(currenttext, color_to_words, csvField_color_list, myfile)
            tempOutputfile = display_wordCloud_sep_color(inputFilename, outputDir, currenttext, color_to_words, transformed_image_mask, collocation, prefer_horizontal, bg_image = bg_image, bg_image_flag= bg_image_flag)
    myfile.close()
    return tempOutputfile

def python_wordCloud(inputFilename, inputDir, outputDir, configFileName, selectedImage, use_contour_only, prefer_horizontal, font, max_words, lemmatize, exclude_stopwords, exclude_punctuation, lowercase, differentPOS_differentColors, differentColumns_differentColors, csvField_color_list, doNotListIndividualFiles,openOutputFiles, collocation):
    # https://www.geeksforgeeks.org/generating-word-cloud-python/
    # Python program to generate WordCloud
    # for a more sophisticated Python script see
    #   https://www.datacamp.com/community/tutorials/wordcloud-python
    #   they provide code to display wc in a selected image
    global filesToOpen
    filesToOpen=[]

    if differentColumns_differentColors==True or inputFilename[-3:]=='csv':
        fileType='.csv'
    else:
        fileType='.txt'

    inputDocs=IO_files_util.getFileList(inputFilename, inputDir,fileType, silent=False, configFileName=configFileName)
    nDocs=len(inputDocs)
    if nDocs==0:
        return filesToOpen

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='wordcloud',
                                                       silent=True)
    if outputDir == '':
        return filesToOpen

    #font = 'IMPRISHA.TTF'
    font = get_font_path(font)

    transformed_image_mask=[]

    use_contour_only = not use_contour_only

    if prefer_horizontal==0:
        prefer_horizontal=.9
    else:
        prefer_horizontal=1

    img = None

    if len(selectedImage)!=0:
        # In order to create a shape for your wordcloud, first, you need to find a PNG file to become the mask.
        # Not all mask images have the same format resulting in different outcomes, hence making the WordCloud function not working properly.
        # The way the masking functions works is that it requires all white part of the mask should be 255 not 0 (integer type). This value represents the "intensity" of the pixel. Values of 255 are pure white, whereas values of 1 are black. Here, you can use the provided function below to transform your mask if your mask has the same format as above. Notice if you have a mask that the background is not 0, but 1 or 2, adjust the function to match your mask.
        try:
            img = Image.open(selectedImage)
        except:
            mb.showwarning(title='Image file error',
                           message="An error was encountered opening the input image file\n\n" + selectedImage + "\n\nPlease, use another image file and try again.")
            return
        img = changeTransparentToWhite(img)
        image_mask = np.array(img)
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
        transformed_image_mask = image_mask
        '''
        for j in range(len(image_mask)):
            transformed_image_mask[j] = list(map(transform_format, image_mask[j]))
            '''
        # Check the expected result of your mask
        # if i==1: #only print once
        print("transformed_image_mask (SHOULD ALL BE 255 VALUES)",transformed_image_mask)

    # can only process a single conll table or a csv file (e.g., SVO reasults where the user selects the columns to be used for color display
    if len(inputDir)>0:
        fileType='.txt'

    # if differentColumns_differentColors:
    #     processCsvColumns(inputFilename, inputDir, outputDir, openOutputFiles, csvField_color_list, doNotListIndividualFiles, bg_image=img, bg_image_flag=use_contour_only)
    #     return

    # RED for NOUNS, BLUE for VERBS, GREEN for ADJECTIVES, GREY for ADVERBS
    #   YELLOW for anything else; no longer used
    # RGB color codes
    red_code = "(250, 0, 0)"
    blue_code = "(0, 0, 250)"
    green_code = "(0, 250, 0)"
    grey_code = "(80, 80, 80)"
    yellow_code = "(255, 255, 0)"
    color_to_words = {
        red_code:[], #red/nouns
        blue_code:[], #blue/verbs
        green_code:[], #green/adjs
        grey_code: [],  # grey/advs
        yellow_code: []  # all other word POS types; no longer used
    }
    combinedtext = ''
    currenttext = ''
    textToProcess = ''
    stopwords = ''
    NumEmptyDocs = 0
    i = 0

    runStanza = False
    if fileType=='.txt':
        # always tokenize to convert each token to lowercase
        #   to avoid the same improper word to appear with lower and upper case at the beginning of a sentence
        stannlp = stanza.Pipeline(lang='en', processors='tokenize, mwt')
        runStanza = True
        if lemmatize:
            # stanza.download('en')#set the annotator that gives postag
            stannlp = stanza.Pipeline(lang='en', processors='tokenize, mwt, lemma')
            runStanza=True
        if exclude_stopwords:
            stopwords = set(STOPWORDS)
            # stanza.download('en')#set the annotator that gives postag
            stannlp = stanza.Pipeline(lang='en', processors='tokenize, mwt')
            runStanza = True
        if exclude_punctuation or differentPOS_differentColors:
            # stanza.download('en') #set the annotator that gives postag
            stannlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos')
            runStanza = True
        if lemmatize and (exclude_punctuation or differentPOS_differentColors):
            # stanza.download('en')  # set the annotator that gives postag
            stannlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,lemma,pos')
            runStanza = True

    if runStanza:
        startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Running STANZA & wordcloud',
                                           'Started running STANZA and wordcloud at', True,
                                           'Please, be patient. Depending upon the number of documents processed this may take a few minutes.',True,'',False)
    for doc in inputDocs:
        i = i+1
        head, tail = os.path.split(doc)
        print("Processing file " + str(i) + "/" + str(nDocs) + ' ' + tail)
        if doc[-4:]=='.csv':#processing CoNLL table that contains pos values
            # check that input file is a CoNLL table
            import CoNLL_util
            if not CoNLL_util.check_CoNLL(doc,True):
                if differentColumns_differentColors:
                    tempOutputfile = processCsvColumns(inputFilename, inputDir, outputDir, openOutputFiles, csvField_color_list,
                                      doNotListIndividualFiles, bg_image=img, bg_image_flag=use_contour_only)
                    if tempOutputfile!='':
                        filesToOpen.append(tempOutputfile)
            else:
                try:
                    # this assumes that the input csv file is a CoNLL table
                    df = pd.read_csv(doc, encoding='utf-8',on_bad_lines='skip')
                    postags_ = df['POStag']
                    forms_ = df['Form']
                    lemmas_ = df['Lemma']

                    #text: summing tokens in each line together
                    words_ = []
                    if lemmatize:
                        currenttext = (" ").join(lemmas_)
                        words_ = lemmas_
                    else:
                        currenttext = (" ").join(forms_)
                        words_ = forms_

                    for j in range(len(words_)):
                        # print("word: ", forms_[i])
                        # print("pos: ", postags_[i])
                        # RED for NOUNS, BLUE for VERBS, GREEN for ADJECTIVES, GREY for ADVERBS
                        #   YELLOW for anything else; no longer used
                        if len(postags_[j]) >= 2 and postags_[j][0:2] == "VB":
                            color_to_words[blue_code].append(words_[j])
                        elif len(postags_[j]) >= 2 and postags_[j][0:2] == "NN":
                            color_to_words[red_code].append(words_[j])
                        elif len(postags_[j]) >= 2 and postags_[j][0:2] == "JJ":
                            color_to_words[green_code].append(words_[j])
                        elif len(postags_[j]) >= 2 and postags_[j][0:2] == "RB":
                            color_to_words[grey_code].append(words_[j])
                        # else:  # should not process? Skip any other tags?
                        #     color_to_words[yellow_code].append(words_[j])
                        if postags_[j][0:2] == "NN" or postags_[j][0:2] == "VB" or \
                                postags_[j][0:2] == "JJ" or postags_[j][0:2] == "RB":
                            textToProcess = textToProcess + ' ' + words_[j]
                except:
                    mb.showwarning(title='Not a CoNLL table',
                                   message=doc + " is not a CoNLL table.\n\nPlease, select in input a proper csv CoNLL file with Form, Lemma, and POStag columns and try again.")
                    return
        elif doc[-4:]=='.txt':
            with open(doc, 'r', encoding='utf-8', errors='ignore') as myfile:
                textToProcess = ''
                currenttext = myfile.read()
                # check for empty file
                error, error2, NumEmptyDocs = check_file_empty(currenttext, doc, nDocs, NumEmptyDocs)
                if error:
                    return
                if error2:
                    continue
                if runStanza:
                    textToProcess = ''
                    annotated = stannlp(currenttext)
                    for sent_id in range(len(annotated.sentences)):
                        for word in annotated.sentences[sent_id].words:
                            # RED for NOUNS, BLUE for VERBS, GREEN for ADJECTIVES, GREY for ADVERBS
                            #   YELLOW for anything else; no longer used
                            if lemmatize:
                                word_str = word.lemma
                                if word_str==None:
                                    word_str = word.text
                            else:
                                word_str = word.text
                            if exclude_stopwords:
                                if word_str in stopwords:
                                    continue  # do not process stopwords & punctuation marks
                            # print("   word_str",word_str,"word.pos",word.pos)
                            # convert to lower case for same improper words that may appear after a full stop
                            if lowercase:
                                if word_str=='':
                                    word_str = word.text
                                if word_str!=None:
                                    word_str = word_str.lower()
                            if exclude_punctuation:
                                if word.pos == "PUNCT":
                                    continue  # do not process punctuation marks
                            if word.pos == "NOUN":
                                color_to_words[red_code].append(word_str)
                            elif word.pos == "VERB":
                                color_to_words[blue_code].append(word_str)
                            elif word.pos == "ADJ":
                                color_to_words[green_code].append(word_str)
                            elif word.pos == "ADV":
                                color_to_words[grey_code].append(word_str)
                            if differentColumns_differentColors:
                                if word.pos == "NOUN" or word.pos == "VERB" or \
                                        word.pos == "ADJ" or word.pos == "ADV":
                                    if word_str!= None:
                                        textToProcess = textToProcess + ' ' + word_str
                                else:
                                    if word_str != None:
                                        textToProcess = textToProcess + ' ' + word_str
                    if len(textToProcess) == 0:
                        textToProcess = currenttext

            if doNotListIndividualFiles==False or len(inputFilename)>0:
                if differentPOS_differentColors:
                    tempOutputfile = display_wordCloud_sep_color(doc, outputDir, textToProcess, color_to_words,
                                                                 transformed_image_mask, collocation,prefer_horizontal, bg_image = img, bg_image_flag = use_contour_only, font = font, max_words = max_words)
                else:
                    tempOutputfile=display_wordCloud(doc,inputDir,outputDir,textToProcess, doNotListIndividualFiles,transformed_image_mask, collocation,prefer_horizontal, bg_image = img, bg_image_flag = use_contour_only , font = font, max_words = max_words)
                filesToOpen.append(tempOutputfile)
                # write an output txt file that can be used for internet wordclouds services
                if lemmatize or exclude_stopwords:
                    with open(tempOutputfile[:-8]+'.txt', 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(textToProcess)
            combinedtext = combinedtext + textToProcess

    if len(inputDir)>0:
        if differentPOS_differentColors:
            tempOutputfile=display_wordCloud_sep_color(inputDir, outputDir, combinedtext, color_to_words, transformed_image_mask, collocation, prefer_horizontal,bg_image=img, bg_image_flag = use_contour_only, font = font, max_words = max_words)
        else:
            tempOutputfile=display_wordCloud(inputDir,inputDir,outputDir,combinedtext, doNotListIndividualFiles,transformed_image_mask, collocation,prefer_horizontal, bg_image=img, bg_image_flag = use_contour_only, font = font, max_words = max_words)
        filesToOpen.append(tempOutputfile)
        # write an output txt file that can be used for internet wordclouds services
        if lemmatize or exclude_stopwords:
            with open(tempOutputfile[:-8] + '.txt', 'w', encoding='utf-8', errors='ignore') as f:
                f.write(combinedtext)
            nDocsRewritten = 1
            if doNotListIndividualFiles==False:
                nDocsRewritten = nDocs+1
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Python wordclouds txt files output',
                                               'The Python 3 wordclouds algorithm has produced '+ str(nDocsRewritten)+' txt file(s) without stopwords, punctuation, and with lemmatized words, depending upon your selected filter options.\n\nYou will find the file(s) in your output directory.\n\nYou can use the file(s) to produce wordclouds using any of the internet wordcloud services.')

        if len(combinedtext) < 1:
            print('All ' + str(NumEmptyDocs) + ' txt files in your input directory\n' + str(
                inputDir) + ' are empty.\n\nPlease, check your directory and try again.')
            mb.showerror(title='Files empty',
                         message='All ' + str(NumEmptyDocs) + ' txt files are empty in your input directory\n' + str(
                             inputDir) + '\n\nPlease, check your directory and try again.')
        if NumEmptyDocs > 0:
            mb.showerror(title='Empty file(s)',
                         message=str(NumEmptyDocs) + ' file(s) empty in the input directory\n' + str(
                             inputDir) + '\n\nFile(s) listed in command line. Please, make sure to check the file(s) content.')

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)
        filesToOpen = None
    return filesToOpen

    # plt.show()

    #=======================================================================================================================
    #Debug use
    #=======================================================================================================================
# def main():
#     a = get_font_list()
#     print("123")

# if __name__ == "__main__":
#     main()
