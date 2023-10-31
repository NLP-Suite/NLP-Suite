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

if not IO_libraries_util.install_all_Python_packages(GUI_util.window, "MALLET Topic modeling",
                                              ['os', 'tkinter.messagebox', 'subprocess']):
    sys.exit(0)

import os
import tkinter.messagebox as mb
import subprocess
from sys import platform

import IO_files_util
import charts_util
import file_converter_util
import IO_user_interface_util


# RUN section __________________________________________________________________________________________________________

def run_MALLET(inputDir, outputDir, openOutputFiles, createCharts, chartPackage, OptimizeInterval, numTopics):
    # to setup environment variable programmatically
    #   https://stackoverflow.com/questions/4906977/how-to-access-environment-variable-values
    # to get an environment variable
    #   malletEnvDir=os.getenv('', 'MALLET_HOME')
    # os.environ lists all environment variables
    # # remove env variable; two alternatives
    # os.environ.pop("MALLET_HOME")
    # del os.environ['MALLET_HOME']

    # check that the CoreNLPdir as been setup
    MALLETDir, existing_software_config, errorFound = IO_libraries_util.external_software_install(
        'topic_modeling_mallet_util',
        'MALLET',
        '',
        silent=False, errorFound=False)

    if MALLETDir == None or MALLETDir=='':
        return

    MALLETPath = ''
    try:
        # if MALLET_HOME has been set up os.getenv returns the MALLET installation path
        MALLETPath = os.getenv('MALLET_HOME', 'MALLET_HOME')
        if MALLETPath == 'MALLET_HOME':
            # the env variable has not been setup
            MALLETPath = ''
            mb.showwarning(title='MALLET-HOME environment variable',
                           message='The value MALLET-HOME needed by MALLET to run was not found in the environment '
                                   'variables.\n\nThe MALLET_HOME value was added programmatically to your '
                                   'environment variables.\n\nTHIS IS A TEMPORARY FIX VALID FOR RUNNING THE MALLET AS '
                                   'LONG AS THIS GUI REMAINS OPEN. For a more permanent solution, please read the '
                                   'TIPS on MALLET installation and setting MALLET environment variables.')
            # add environment variable
            os.environ["MALLET_HOME"] = MALLETDir
        else:
            MALLETDir = MALLETDir.replace("\\", "/")
            MALLETPath = MALLETPath.replace("\\", "/")
            if str(MALLETPath).lower() != str(MALLETDir).lower():
                # add updated environment variable
                os.environ["MALLET_HOME"] = MALLETDir
                mb.showwarning(title='MALLET environment variable path update',
                               message='The value MALLET-HOME in the environment variables was changed from\n\n  ' +
                                       MALLETPath + '\n\nto\n\n  ' + MALLETDir)
    except BaseException:
        mb.showwarning(title='MALLET-HOME environment variable',
                       message='The value MALLET-HOME needed by MALLET to run was not found in the environment '
                               'variables.\n\nThe MALLET_HOME value was added programmatically to your environment '
                               'variables.\n\nTHIS IS A TEMPORARY FIX VALID FOR RUNNING THE MALLET AS LONG AS THIS '
                               'GUI REMAINS OPEN. For a more permanent solution, please read the TIPS on MALLET '
                               'installation and setting MALLET environment variables.')
        MALLETDir = MALLETDir.replace("\\", "/")
        MALLETPath = MALLETPath.replace("\\", "/")
        if str(MALLETPath).lower() != str(MALLETDir).lower():
            # add environment variable
            os.environ["MALLET_HOME"] = MALLETDir

    filesToOpen = []

    MALLETDir = MALLETDir + os.sep + 'bin'

    if ' ' in inputDir:
        mb.showerror(title='Input file error',
                     message='The selected INPUT directory contains a blank (space) in the path. The MALLET code '
                             'cannot handle input/output paths that contain a space and will break.\n\nPlease, '
                             'place your input files in a directory with a path containing no spaces and try again.')
        return
    if ' ' in outputDir:
        mb.showerror(title='Output file error',
                     message='The selected OUTPUT directory contains a blank (space) in the path. The MALLET code '
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
    elif numFiles < 50:
        result = mb.askyesno(title='Number of files', message='The selected input directory contains only ' + str(
            numFiles) + ' files of txt type.\n\nTopic modeling requires a large number of files (in the hundreds at least; read TIPS file) to produce valid results.\n\nAre you sure you want to continue?',
                             default='no')
        if result == False:
            return

    """
    All OUTPUT file names can be changed and MALLET will still run successfully
    OUTPUT file names extensions for step two can be TXT or CSV
    """
    # output.mallet
    TXTFiles_MALLETFormatted_FileName = os.path.join(outputDir, "MALLETFormatted_TXTFiles.mallet")
    # output.csv or output.txt
    Composition_FileName = os.path.join(outputDir, "NLP-MALLET_Output_Composition")
    # keys.tsv or keys.txt
    Keys_FileName = os.path.join(outputDir, "NLP-MALLET_Output_Keys.tsv")
    # output.gz
    Compressed_FileName = os.path.join(outputDir, "NLP-MALLET_Output_Compressed.gz")

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

    # mb.showwarning(title="MALLET output files", message="The Python MALLET wrapper runs MALLET with default options. "
    #                                                     "If you want to provide custom options, please run MALLET "
    #                                                     "from the command prompt.\n\nThe NLP MALLET produces four "
    #                                                     "files in output (refer to the MALLET TIPS file for what each"
    #                                                     " file contains):\n\n" +
    #                                                     TXTFiles_MALLETFormatted_FileName + "\n" +
    #                                                     Composition_FileName + "\n" +
    #                                                     Keys_FileName + "\n" +
    #                                                     Compressed_FileName)

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running MALLET Topic modeling at ', True,
                                                   "Depending upon corpus size, computations may take a while... "
                                                   "Please, be patient...")

    # FIRST STEP

    # The output file MALLETFormatted_TXTFiles.mallet contains all corpus TXT files properly formatted for MALLET
    if platform == "win32":
        subprocess.call([MALLETDir + os.sep + 'mallet', 'import-dir', '--input', inputDir, '--output',
                         TXTFiles_MALLETFormatted_FileName, '--keep-sequence', '--remove-stopwords'], shell=True)
    # linux # OS X
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call([MALLETDir + os.sep + 'mallet', 'import-dir', '--input', inputDir, '--output',
                         TXTFiles_MALLETFormatted_FileName, '--keep-sequence', '--remove-stopwords'])

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
                [MALLETDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MALLETFormatted_FileName,
                 '--num-topics', str(numTopics), '--optimize-interval', str(numTopics), '--output-state',
                 Compressed_FileName, '--output-topic-keys', Keys_FileName, '--output-doc-topics',
                 Composition_FileName], shell=True)
        else:
            subprocess.call(
                [MALLETDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MALLETFormatted_FileName,
                 '--num-topics', str(numTopics), '--output-state', Compressed_FileName, '--output-topic-keys',
                 Keys_FileName, '--output-doc-topics', Composition_FileName], shell=True)
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        if OptimizeInterval:
            subprocess.call(
                [MALLETDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MALLETFormatted_FileName,
                 '--num-topics', str(numTopics), '--optimize-interval', str(numTopics), '--output-state',
                 Compressed_FileName, '--output-topic-keys', Keys_FileName, '--output-doc-topics',
                 Composition_FileName])
        else:
            subprocess.call(
                [MALLETDir + os.sep + 'mallet', 'train-topics', '--input', TXTFiles_MALLETFormatted_FileName,
                 '--num-topics', str(numTopics), '--output-state', Compressed_FileName, '--output-topic-keys',
                 Keys_FileName, '--output-doc-topics', Composition_FileName])

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running MALLET Topic modeling at ', True, '', True, startTime)

    # https://stackoverflow.com/questions/29759305/how-do-i-convert-a-tsv-to-csv

    # convert to csv MALLET tsv output files
    # read MALLET tab-delimited files; both Keys_FileName and Composition_FileName must be converted

    if (not os.path.isfile(Keys_FileName)) and (not os.path.isfile(Composition_FileName)):
        mb.showwarning(title='MALLET FATAL error',
                       message='MALLET has not produced the expected Keys and Composition files. It looks like MALLET '
                               'did NOT run.\n\nPlease, make sure that you have edited properly the environment '
                               'variables by reading the TIPS file for MALLET installation and setting MALLET '
                               'environment variables.')
        return
    Keys_FileName = file_converter_util.tsv_converter(GUI_util.window, Keys_FileName, outputDir)
    Composition_FileName = file_converter_util.tsv_converter(GUI_util.window, Composition_FileName, outputDir)
    filesToOpen.append(Keys_FileName)
    filesToOpen.append(Composition_FileName)

    if createCharts:
        # the MALLET files do not have headers to be able to use charts_util.visualize_chart

        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[]
        for i in range(2, numTopics):
            columns_to_be_plotted_yAxis.append([1, i])

        hover_label=[]
        chart_title = 'MALLET Topics\nTopic Contribution to Document'
        xAxis = 'Document'
        yAxis = 'Topic weight in document'

        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, Composition_FileName, outputDir,
                                                  'MALLET_TM',
                                                  chartPackage=chartPackage,
                                                  chart_type_list=["bar"],
                                                  chart_title=chart_title,
                                                  column_xAxis_label_var=xAxis,
                                                  hover_info_column_list=hover_label,
                                                  count_var=0,
                                                  column_yAxis_label_var=yAxis)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[[0, 1]]
        hover_label=[2]
        chart_title = 'MALLET Topics (Topic Weight by Topic)'
        xAxis = 'Topic #'
        yAxis = 'Topic weight'

        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, Keys_FileName, outputDir,
                                                  'MALLET_TM',
                                                  chartPackage=chartPackage,
                                                  chart_type_list=["bar"],
                                                  chart_title=chart_title,
                                                  column_xAxis_label_var=xAxis,
                                                  hover_info_column_list=[], #hover_label,
                                                  count_var=0,
                                                  column_yAxis_label_var=yAxis)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)
        filesToOpen=[] # to avoid opening files twice, here and in calling function

    return filesToOpen
