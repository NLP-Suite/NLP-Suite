"""
    Read in html file with words previously annotated via the annotation builders
    gather text between annotation tags
    output aggregate data to cvs table, clean files NO HTML OUTPUT 
    Last updated: July 18, 2019
    by Jack Hester
    rewritten by Roberto Franzosi, Zhangyi Pan
"""

import sys

import GUI_IO_util
import IO_files_util
import Excel_util
import GUI_util
import IO_libraries_util
import IO_user_interface_util

if IO_libraries_util.install_all_packages(GUI_util.window,"annotator_html_extractor_util",['os','tkinter','re','csv','ntpath'])==False:
    sys.exit(0)

import re
import os
import csv
import ntpath


# Optional routine to clean any places where a duplicate tag emerged on accident
# Takes in text to check and list of tags to check duplicates/triplicates, etc. of
# Checks up to 10x occuring, allows occuring once
def cleanMultipleTags(text, tags):
    sorted_tags = sorted(tags, key=len)
    for tag in sorted_tags:
        for n in range(2, 11):
            text = text.replace(n*tag, '')
    return text

# Take in html files, find tagged words and extract them
# Tags require a list of two strings in the form ['openingTag','closingTag']
# mustInclude means that the tag must appear in the line (to avoid headers/extra paragraphs)
def gatherAnnotations(inputFile, tags, mustInclude='<p>', cleanMultiples=True):
    openingTag, closingTag = tags[0], tags[1]
    starts, ends, words = [], [], []
    with open(inputFile, 'r',encoding='utf-8',errors='ignore') as f:
        for line in f.readlines():
            if mustInclude in line:
                if cleanMultiples==True:
                    line = cleanMultipleTags(line, tags)
                for tag in re.finditer(openingTag, line):
                    starts.append(tag.end())
                for tag in re.finditer(closingTag, line):
                    ends.append(tag.start())
                for i in range(0, min(len(ends),len(starts))):
                    words.append(line[starts[i]:ends[i]])
            starts, ends = [],[]
    words = [w for w in words if w!='']
    if openingTag!='">' and closingTag!='</a':
        result=[]
        for word in words:
            result.append(word.split('>',1)[1])
    else:
        result=words
    return result
        

def buildcsv(inputHTMLFile, inputHTMLFolder, outputDir,openOutputFiles,createExcelCharts):
    filesToOpen=[]
    outputFilename=IO_files_util.generate_output_file_name('DBpedia annotations', '', outputDir, '.csv', 'html extractor', '', '')
    filesToOpen.append(outputFilename)
    annotatedHtmlFiles = []

    annotatedHtmlFiles=IO_files_util.getFileList(inputHTMLFile, inputHTMLFolder, '.html')
    nFile=len(annotatedHtmlFiles)

    if nFile==0:
        return
    i=0

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running html annotator extractor at', True, "You can follow html annotation extractor in command line.")

    csvFile=os.path.join(outputDir, outputFilename)
    writeCSV = IO_files_util.openCSVFile(csvFile, 'w')
    if writeCSV=='':
        return
    writer = csv.writer(writeCSV)
    writer.writerow(['Filename','Word','Annotation Type'])
    for file in annotatedHtmlFiles:
        i=i+1
        print("Processing html annotated file " + str(i) + "/" + str(nFile), file)
        DBpediaWordList = gatherAnnotations(file, ['">',"</a"],'',False)
        dictionaryWordList = gatherAnnotations(file, ['<span',"</span>"],'',True)
        fileName = ntpath.basename(file)
        for word in DBpediaWordList:
            writer.writerow([fileName, word,'DBpedia'])
        for word in dictionaryWordList:
            writer.writerow([fileName, word,'Dictionary'])

        # combinedList=[]
        # for word in dictionaryWordList:
        #     if word in DBpediaWordList:
        #         combinedList.append(word)
        # for word in dictionaryWordList:
        #     if word not in combinedList:
        #         writer.writerow([fileName, word,'','X'])
        # for word in DBpediaWordList:
        #     if word not in combinedList:
        #         writer.writerow([fileName, word,'X',''])
        # for word in combinedList:
        #     writer.writerow([fileName, word,'X','X'])

    writeCSV.close()

    # if createExcelCharts==True:
    #     # TODO need to create bar and line charts
    #     chartTitle='HTML extractor'
    #     columns_to_be_plotted = [2,2]
    #     hover_label=['']
    #     chartType='bar'
    #     fileNameType='html_extr'
    #     excel_outputFilename_1 = Excel_util.run_all(columns_to_be_plotted, csvFile, outputDir, csvFile, chart_type_list=[chartType], chart_title=chartTitle, column_xAxis_label_var='', column_yAxis_label_var='Frequencies', outputExtension = '.xlsm', label1=fileNameType,label2=chartType,label3='chart',label4='',label5='', useTime=False,disable_suffix=True,  count_var=1, column_yAxis_field_list = [], reverse_column_position_for_series_label=False , series_label_list=[], second_y_var=0, second_yAxis_label='', hover_info_column_list=hover_label)
    #     if excel_outputFilename_1 != "":
    #         filesToOpen.append(excel_outputFilename_1)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running html annotator extractor at', True, '', True, startTime)
    
    if openOutputFiles==True :
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

# Testing program
def main():
    buildcsv('test', 'test')

if __name__ == '__main__':
    main()
