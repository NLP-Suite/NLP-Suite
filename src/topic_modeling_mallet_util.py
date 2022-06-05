"""
TWO STEPS ARE INVOLVED
STEP ONE: IMPORT YOUR CORPUS
    COMMAND: bin\\mallet import-dir --input folder\\files --output tutorial.mallet --keep-sequence --remove-stopwords

    Here, we tell MALLET to import all the TXT files of your corpus and to create a single MALLET-formatted file in output
    Parameter: --keep-sequence keep the original texts in the order in which they were listed;
    Parameter: --remove-stopwords strip out the stop words (words such as and, the, but, and if that occur in such frequencies that they obstruct analysis) using the default English stop-words dictionary.
    INPUT: all TXT files of your corpus
    OUTPUT: (tutorial.mallet) a single MALLET-formatted file containing all TXT input files

STEP TWO
    COMMAND: bin\\mallet train-topics  --input tutorial.mallet --num-topics 20 --output-state topic-state.gz --output-topic-keys tutorial_keys.txt --output-doc-topics tutorial_compostion.txt
    Here, we tell MALLET to create a topic model (train-topics) and everything with a double hyphen afterwards sets different parameters

    This Command trains MALLET to find 20 topics
       INPUT: the output file from STEP ONE (your tutorial.mallet file)
       OUTPUT (.gz): a .gz compressed file containing every word in your corpus of materials and the topic it belongs to (.gz; see www.gzip.org on how to unzip this)
       OUTPUT (KEYS): a CSV or TXT document (tutorial_keys.txt) showing you what the top key words are for each topic
       OUTPUT (COMPOSITION): a CSV or TXT  file (tutorial_composition.txt) indicating the breakdown, by percentage, of each topic within each original text file you imported.
           To see the full range of possible parameters that you may want to tweak, type bin\\mallet train-topics ?help at the prompt

All OUTPUT file names can be changed and MALLET will still run successfully
 OUTPUT file names extensions for step two can be TXT or CSV
"""
import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_packages(GUI_util.window, "Mallet Topic modeling",
                                              ['os', 'tkinter.messagebox', 'subprocess']):
    sys.exit(0)

import os
import tkinter.messagebox as mb
import subprocess
from sys import platform

import IO_files_util
import charts_Excel_util
import file_type_converter_util
import IO_user_interface_util


# RUN section __________________________________________________________________________________________________________

def run(inputDir, outputDir, openOutputFiles, createCharts, chartPackage, OptimizeInterval, numTopics):
    # to setup environment variable programmatically
    #   https://stackoverflow.com/questions/4906977/how-to-access-environment-variable-values
    # to get an environment variable
    #   malletEnvDir=os.getenv('', 'MALLET_HOME')
    # os.environ lists all environment variables
    # # remove env variable; two alternatives
    # os.environ.pop("MALLET_HOME")
    # del os.environ['MALLET_HOME']

    # check that the MalletDir as been setup
    MalletDir, missing_external_software = IO_libraries_util.get_external_software_dir('topic_modeling_mallet',
                                                                                       'Mallet')
    if MalletDir is None:
        return

    MalletPath = ''
    try:
        # if MALLET_HOME has been set up os.getenv returns the Mallet installation path
        MalletPath = os.getenv('MALLET_HOME', 'MALLET_HOME')
        if MalletPath == 'MALLET_HOME':
            # the env variable has not been setup
            MalletPath = ''
            mb.showwarning(title='MALLET-HOME environment variable',
                           message='The value MALLET-HOME needed by MALLET to run was not found in the environment '
                                   'variables.\n\nThe MALLET_HOME value was added programmatically to your '
                                   'environment variables.\n\nTHIS IS A TEMPORARY FIX VALID FOR RUNNING THE MALLET AS '
                                   'LONG AS THIS GUI REMAINS OPEN. For a more permanent solution, please read the '
                                   'TIPS on Mallet installation and setting Mallet environment variables.')
            # add environment variable
            os.environ["MALLET_HOME"] = MalletDir
        else:
            MalletDir = MalletDir.replace("\\", "/")
            MalletPath = MalletPath.replace("\\", "/")
            if str(MalletPath).lower() != str(MalletDir).lower():
                # add updated environment variable
                os.environ["MALLET_HOME"] = MalletDir
                mb.showwarning(title='Mallet environment variable path update',
                               message='The value MALLET-HOME in the environment variables was changed from\n\n  ' +
                                       MalletPath + '\n\nto\n\n  ' + MalletDir)
    except BaseException:
        mb.showwarning(title='MALLET-HOME environment variable',
                       message='The value MALLET-HOME needed by Mallet to run was not found in the environment '
                               'variables.\n\nThe MALLET_HOME value was added programmatically to your environment '
                               'variables.\n\nTHIS IS A TEMPORARY FIX VALID FOR RUNNING THE MALLET AS LONG AS THIS '
                               'GUI REMAINS OPEN. For a more permanent solution, please read the TIPS on Mallet '
                               'installation and setting Mallet environment variables.')
        MalletDir = MalletDir.replace("\\", "/")
        MalletPath = MalletPath.replace("\\", "/")
        if str(MalletPath).lower() != str(MalletDir).lower():
            # add environment variable
            os.environ["MALLET_HOME"] = MalletDir

    filesToOpen = []

    MalletDir = MalletDir + os.sep + 'bin'

    if ' ' in inputDir:
        mb.showerror(title='Input file error',
                     message='The selected INPUT directory contains a blank (space) in the path. The Mallet code '
                             'cannot handle input/output paths that contain a space and will break.\n\nPlease, '
                             'place your input files in a directory with a path containing no spaces and try again.')
        return
    if ' ' in outputDir:
        mb.showerror(title='Output file error',
                     message='The selected OUTPUT directory contains a blank (space) in the path. The Mallet code '
                             'cannot handle input/output paths that contain a space and will break.\n\nPlease, '
                             'select an output directory with a path containing no spaces and try again.')
        return
    if not os.path.isdir(inputDir):
        mb.showerror(title='Input directory error',
                     message='The selected input directory does NOT exist.\n\nPlease, select a different directory '
                             'and try again.')
        return
    if not os.path.isdir(outputDir):
        mb.showerror(title='Output directory error',
                     message='The selected output directory does NOT exist.\n\nPlease, select a different directory '
                             'and try again.')
        return

    numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')

    if numFiles == 0:
        mb.showerror(title='Number of files error',
                     message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a '
                             'different directory and try again.')
        return
    elif numFiles == 1:
        mb.showerror(title='Number of files error', message='The selected input directory contains only ' + str(
            numFiles) + ' file(s) of txt type.\n\nTopic modeling requires a large number of files to produce valid '
                        'results. That is true even if the available file contains several different documents morged'
                        ' together.')
        return
    elif numFiles < 10:
        mb.showwarning(title='Number of files', message='The selected input directory contains only ' + str(
            numFiles) + ' file(s) of txt type.\n\nTopic modeling requires a large number of files to produce valid '
                        'results.')

    """
    All OUTPUT file names can be changed and Mallet will still run successfully
    OUTPUT file names extensions for step two can be TXT or CSV
    """
    # output.mallet
    TXTFiles_MalletFormatted_FileName = os.path.join(outputDir, "MalletFormatted_TXTFiles.mallet")
    # output.csv or output.txt
    Composition_FileName = os.path.join(outputDir, "NLP-Mallet_Output_Composition")
    # keys.tsv or keys.txt
    Keys_FileName = os.path.join(outputDir, "NLP-Mallet_Output_Keys.tsv")
    # output.gz
    Compressed_FileName = os.path.join(outputDir, "NLP-Mallet_Output_Compressed.gz")

    # filesToOpen.append(Composition_FileName+'.csv')
    # filesToOpen.append(Keys_FileName+'.csv')
    #
    """
    The Key table has as many lines as desired topics and three columns 
        TOPIC #, 
        WEIGHT OF TOPIC that measures the weight of the topic across all the documents,
        KEY WORDS IN TOPIC that lists a set of typical words belonging to the topic.
        
    The Composition table has as many lines as documents analyzed (one document per line) and several columns:
        column 1 (Document ID), 
        column 2 (Document with path), 
        and as many successive pairs of columns as the number of topics, with column pairs as follow: 
            TOPIC is a number corresponding to the number in column 1 in the Keys file; 
            PROPORTION measures the % of words in the document attributed to that topic
            (pairs sorted in descending PROPORTION order).
    """

    # mb.showwarning(title="Mallet output files", message="The Python Mallet wrapper runs Mallet with default options. "
    #                                                     "If you want to provide custom options, please run Mallet "
    #                                                     "from the command prompt.\n\nThe NLP Mallet produces four "
    #                                                     "files in output (refer to the Mallet TIPS file for what each"
    #                                                     " file contains):\n\n" +
    #                                                     TXTFiles_MalletFormatted_FileName + "\n" +
    #                                                     Composition_FileName + "\n" +
    #                                                     Keys_FileName + "\n" +
    #                                                     Compressed_FileName)

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running Mallet Topic modeling at ', True,
                                                   "Depending upon corpus size, computations may take a while... "
                                                   "Please, be patient...")

    # FIRST STEP

    # The output file MalletFormatted_TXTFiles.mallet contains all corpus TXT files properly formatted for Mallet
    if platform == "win32":
        subprocess.call([MalletDir + os.sep + 'mallet', 'import-dir', '--input', inputDir, '--output',
                         TXTFiles_MalletFormatted_FileName, '--keep-sequence', '--remove-stopwords'], shell=True)
    # linux # OS X
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call([MalletDir + os.sep + 'mallet', 'import-dir', '--input', inputDir, '--output',
                         TXTFiles_MalletFormatted_FileName, '--keep-sequence', '--remove-stopwords'])

    # SECOND STEP
    # The output file Composition_FileName is a tsv file indicating the breakdown, by percentage,
    # of each topic within each original imported text file
    # The output file Keys_FileName is a text file showing what the top key words are for each topic
    # the .gz file contains in .gz compressed form every word in your corpus, with each topic associated with each
    # see www.gzip.org on how to unzip this
    # Interval Optimization leads to better results according to
    # http://programminghistorian.org/lessons/topic-modeling-and-mallet

    # the real format of the file created by mallet is .tsv or .txt

    if platform == "win32":
        if OptimizeInterval:
            subprocess.call(
                [MalletDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MalletFormatted_FileName,
                 '--num-topics', str(numTopics), '--optimize-interval', str(numTopics), '--output-state',
                 Compressed_FileName, '--output-topic-keys', Keys_FileName, '--output-doc-topics',
                 Composition_FileName], shell=True)
        else:
            subprocess.call(
                [MalletDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MalletFormatted_FileName,
                 '--num-topics', str(numTopics), '--output-state', Compressed_FileName, '--output-topic-keys',
                 Keys_FileName, '--output-doc-topics', Composition_FileName], shell=True)
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        if OptimizeInterval:
            subprocess.call(
                [MalletDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MalletFormatted_FileName,
                 '--num-topics', str(numTopics), '--optimize-interval', str(numTopics), '--output-state',
                 Compressed_FileName, '--output-topic-keys', Keys_FileName, '--output-doc-topics',
                 Composition_FileName])
        else:
            subprocess.call(
                [MalletDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MalletFormatted_FileName,
                 '--num-topics', str(numTopics), '--output-state', Compressed_FileName, '--output-topic-keys',
                 Keys_FileName, '--output-doc-topics', Composition_FileName])

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running Mallet Topic modeling at ', True, '', True, startTime)

    # https://stackoverflow.com/questions/29759305/how-do-i-convert-a-tsv-to-csv

    # convert to csv Mallet tsv output files 
    # read Mallet tab-delimited files; both Keys_FileName and Composition_FileName must be converted

    if (not os.path.isfile(Keys_FileName)) and (not os.path.isfile(Composition_FileName)):
        mb.showwarning(title='Mallet FATAL error',
                       message='Mallet has not produced the expected Keys and Composition files. It looks like Mallet '
                               'did NOT run.\n\nPlease, make sure that you have edited properly the environment '
                               'variables by reading the TIPS file for Mallet installation and setting Mallet '
                               'environment variables.')
        return
    Keys_FileName = file_type_converter_util.tsv_converter(GUI_util.window, Keys_FileName, outputDir)
    Composition_FileName = file_type_converter_util.tsv_converter(GUI_util.window, Composition_FileName, outputDir)
    filesToOpen.append(Keys_FileName)
    filesToOpen.append(Composition_FileName)

    if createCharts:
        columns_to_be_plotted = [[0, 1]]
        hover_label = [2]
        chartTitle = 'Mallet Topics'
        xAxis = 'Topic #'
        yAxis = 'Topic weight'
        fileName = Keys_FileName
        chart_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, fileName, outputDir,
                                                  'Mallet_TM',
                                                  chartPackage=chartPackage,
                                                  chart_type_list=["bar"],
                                                  chart_title=chartTitle,
                                                  column_xAxis_label_var=xAxis,
                                                  hover_info_column_list=hover_label,
                                                  count_var=0,
                                                  column_yAxis_label_var=yAxis)

        if chart_outputFilename != "":
            filesToOpen.append(chart_outputFilename)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
