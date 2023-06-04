
import charts_util
import reminders_util
import IO_csv_util

# outputFilename is actually the file containing fields to be charted
def parsers_annotators_visualization(configFilename, inputFilename, inputDir, outputDir, outputFilename,
                annotator_params, kwargs, createCharts, chartPackage, openFiles=True):
    # headers = IO_csv_util.get_csvfile_headers_pandas(outputFilename)
    # docCol = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Document ID', inputFilename)
    # docCol = docCol + 1  # we need to visualize the doc filename

    # generate visualization output ----------------------------------------------------------------
# Lemma ________________________________________________________________
    import os
    # cannot use the usual scriptName here otherwise it would be parsers_annotators_visualization_util
    #   and what we want is the calling script in config.csv, e.g., NER_config.csv
    # head, scriptName = os.path.split(os.path.basename(__file__))
    scriptName=configFilename.replace("_config.csv","")
    filesToOpen=[]
    if "Lemma" in str(annotator_params) and 'Lemma' in outputFilename:
        # reminders_util.checkReminder(scriptName, reminders_util.lemma_frequencies,
        #                              reminders_util.message_lemma_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Form','Lemma'],
                                                           chartTitle='Frequency Distribution of Form & Lemma Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='form-lemma', #'POS_bar',
                                                           column_xAxis_label='Lemma values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Lemma Values')

        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# All POS ________________________________________________________________

    elif 'All POS' in str(annotator_params) and 'All POS' in outputFilename:
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['POS'],
                                                           chartTitle='Frequency Distribution of POS Tag Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='POS', #'POS_bar',
                                                           column_xAxis_label='POS tag values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='POS Tag Values')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# NER ________________________________________________________________

    elif 'NER' in str(annotator_params) and 'NER' in outputFilename:
        reminders_util.checkReminder(scriptName, reminders_util.NER_frequencies,
                                     reminders_util.message_NER_frequencies)
        if IO_csv_util.get_csvfile_headers(outputFilename, False)[1] == "NER":
            # plot NER tag (e.g, LOCATION)
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                               outputDir,
                               columns_to_be_plotted_xAxis=[],
                               columns_to_be_plotted_yAxis=['NER'],
                               chartTitle='Frequency Distribution of NER Tags',
                               # count_var = 1 for columns of alphabetic values
                               count_var=1, hover_label=[],
                               outputFileNameType='NER-tag', #'NER_tag_bar',
                               column_xAxis_label='NER tag',
                               groupByList=['Document ID','Document'],
                               plotList=['Frequency'],
                               chart_title_label='NER tag')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

            # import statistics_csv_util
            # import GUI_util
            # columns_to_be_plotted_yAxis=['NER']
            # pivot=False
            # temp_outputFilename = statistics_csv_util.compute_csv_column_frequencies(GUI_util.window,
            #                                                           outputFilename,
            #                                                           None, outputDir,
            #                                                           False,
            #                                                           createCharts,
            #                                                           chartPackage,
            #                                                           # selected_col=columns_to_be_plotted_numeric,
            #                                                           selected_col=columns_to_be_plotted_yAxis,
            #                                                           hover_col=[],
            #                                                           group_col=['NER'],
            #                                                           complete_sid=False,
            #                                                           fileNameType=
            #                                                           columns_to_be_plotted_yAxis[
            #                                                               0],
            #                                                           chartType='',
            #                                                           pivot=pivot)
            # new_inputFilename = temp_outputFilename[0]
            # # temp_outputFilename[0] is the frequency filename (with no hyperlinks)
            # count_var = 0
            # remove_hyperlinks = False  # already removed in compute frequencies
            # # 2,3 are the Document and Frequency columns in temp_outputFilename
            # # columns_to_be_plotted_byDoc = [[2,3]] # document 2, first item; frequencies 3 second item
            # # columns_to_be_plotted_byDoc = [[1,2],[1,3]]
            # # pivot = True
            #
            # headers = IO_csv_util.get_csvfile_headers_pandas(new_inputFilename)
            #
            # # 1 is the Document with no-hyperlinks,
            # # 2 is the column plotted (e.g., Gender) in temp_outputFilename
            # # 3 is Frequency,
            # # TODO TONY we should ask the same type of question for columns that are already in quantitative form if we want to compute a single MEAN value
            # sel_column_name = IO_csv_util.get_headerValue_from_columnNumber(headers, 2)
            # # columns_to_be_plotted_byDoc = [[0, 2]] # will give one bar
            # n_documents=0
            # if n_documents == 1:
            #     columns_to_be_plotted_byDoc = [[2, 3]]  # will give different bars for each value
            # else:
            #     columns_to_be_plotted_byDoc = [[1, 3, 2]]  # will give different bars for each value
            # # columns_to_be_plotted_byDoc = [[0, 1, 2]] # No!!!!!!!!!!!
            # outputFileLabel='temp'
            # chartTitle='merdata'
            # hover_label=[]
            # column_yAxis_label = 'Frequencies'
            # if chartPackage == "Excel":
            #     column_name = IO_csv_util.get_headerValue_from_columnNumber(headers, 1)
            #     number_column_entries = len(IO_csv_util.get_csv_field_values(new_inputFilename, column_name))
            #     chart_outputFilename = charts_util.run_all(columns_to_be_plotted_byDoc, new_inputFilename, outputDir,
            #                                               outputFileLabel=outputFileLabel, # outputFileNameType + 'byDoc', #outputFileLabel,
            #                                               chartPackage=chartPackage,
            #                                               chart_type_list=['bar'],
            #                                               chart_title=chartTitle + ' by Document',
            #                                               column_xAxis_label_var='',
            #                                               column_yAxis_label_var=column_yAxis_label,
            #                                               hover_info_column_list=hover_label,
            #                                               # count_var is set in the calling function
            #                                               #     0 for numeric fields;
            #                                               #     1 for non-numeric fields
            #                                               count_var=count_var,
            #                                               remove_hyperlinks=remove_hyperlinks)
            #     if chart_outputFilename!=None:
            #         if len(chart_outputFilename) > 0:
            #             filesToOpen.append(chart_outputFilename)

            # # plot the words contained in each NER tag (e.g, the word 'Rome' in NER tag LOCATION)
            # hover_label = []
            # columns_to_be_plotted = [[1, 0, 1]]
            # chartTitle = 'Frequency Distribution of words'
            # chart_outputFilename = charts_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
            #                                outputFileLabel='byNER_',
            #                                # outputFileNameType + 'byDoc', #outputFileLabel,
            #                                chartPackage=chartPackage,
            #                                chart_type_list=['bar'],
            #                                chart_title=chartTitle + ' by NER',
            #                                column_xAxis_label_var='',
            #                                column_yAxis_label_var='Frequency',
            #                                hover_info_column_list=hover_label,
            #                                # count_var is set in the calling function
            #                                #     0 for numeric fields;
            #                                #     1 for non-numeric fields
            #                                count_var=1,
            #                                remove_hyperlinks=True)
            # if chart_outputFilename != None:
            #     if len(chart_outputFilename) > 0:
            #         filesToOpen.append(chart_outputFilename)



            # chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
            #                            outputDir,
            #                            columns_to_be_plotted_xAxis=[], #['NER'],
            #                            columns_to_be_plotted_yAxis=['Word'],
            #                            chartTitle='Frequency Distribution of Words by NER Tag', # + ner_tags,
            #                            # count_var = 1 for columns of alphabetic values
            #                            count_var=1, hover_label=[],
            #                            outputFileNameType='NER-word', #'NER_word_bar',
            #                            column_xAxis_label='Word',
            #                            groupByList=['Document ID','Document'],
            #                            plotList=['Frequency'],
            #                            chart_title_label='NER Words')
            # if chart_outputFilename != None:
            #     if len(chart_outputFilename) > 0:
            #         filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# date ________________________________________________________________
    # dates are extracted by the date annotator, but also as part of SVO and OpenIE
    elif (('date' in str(annotator_params) and 'date' in outputFilename)) or \
            ('OpenIE' in str(annotator_params) and 'OpenIE' in outputFilename):
            # (('SVO' in str(annotator_params) and 'SVO' in outputFilename)) or \
            # visualizing normalized-date for SVO is done in SVO_util called in SVO_main
        # Date expressions are in the form yesterday, tomorrow morning, the day before Christmas
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Date expression'],
                                                           chartTitle='Frequency Distribution of Date Expressions',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='date-express', #'NER_info_bar',
                                                           column_xAxis_label='Date expression',
                                                           groupByList=['Document ID','Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Date Expressions')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        # normalized dates are in the form PAST_REF, NEXT_IMMEDIATE P1D, ...
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Normalized date'],
                                                           chartTitle='Frequency Distribution of Normalized Dates',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='date', #'NER_date_bar',
                                                           column_xAxis_label='Normalized date',
                                                           groupByList=['Document ID','Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Normalized Dates')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        # Date types are in the form PAST, PRESENT, OTHER
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Date type'],
                                                           chartTitle='Frequency Distribution of Date Types',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='date-types', #'NER_info_bar',
                                                           column_xAxis_label='Date type',
                                                           groupByList=['Document ID','Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Date Types')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# gender ________________________________________________________________

    elif 'gender' in str(annotator_params) and 'gender' in outputFilename:
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Gender'],
                                                           chartTitle='Frequency Distribution of Gender Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='gender-values', #'gender_bar',
                                                           column_xAxis_label='Gender values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for Gender')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Word'],
                                                           chartTitle='Frequency Distribution of Gendered Words',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='gender-words', #'gender_bar',
                                                           column_xAxis_label='Gender words',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for Gendered Words')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = visualize_html_file(inputFilename, inputDir, outputDir, configFilename, outputFilename)
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)


# generate visualization output ----------------------------------------------------------------
# parser ________________________________________________________________
    # 'depparse' used for Stanza and spaCy
    elif ('parse' in str(annotator_params) and 'CoNLL' in outputFilename) or ('depparse' in str(annotator_params)):

        # Form & Lemma values
        # reminders_util.checkReminder(scriptName, reminders_util.lemma_frequencies,
        #                              reminders_util.message_lemma_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Form','Lemma'],
                                                           chartTitle='Frequency Distribution of FORM & LEMMA Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='form-lemma',
                                                           column_xAxis_label='FORM & LEMMA values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for Form & Lemma Values')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# quote ________________________________________________________________

    elif 'quote' in str(annotator_params) and 'quote' in outputFilename:
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Speakers'],
                                                           chartTitle='Frequency Distribution of Speakers\n(CoreNLP Quote Annotator)',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='quote', #'quote_bar',
                                                           column_xAxis_label='Speakers',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for Quotes')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# POS Tag values in CoNLL table
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['POS'],
                                                           chartTitle='Frequency Distribution of POS (Part of Speech) Tags',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='POS',
                                                           column_xAxis_label='POS tags',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for POS Tags')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# NER Tag values in CoNLL table _____________________________________________________________________
        reminders_util.checkReminder(scriptName, reminders_util.NER_frequencies,
                                     reminders_util.message_NER_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['NER'],
                                                           chartTitle='Frequency Distribution of NER (Named Entity Recognition) Tags',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='NER',
                                                           column_xAxis_label='NER tags',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for Form & Lemma Values')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# DEPrel values in CoNLL table
        reminders_util.checkReminder(scriptName, reminders_util.DepRel_frequencies,
                                     reminders_util.message_DepRel_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['DepRel'],
                                                           chartTitle='Frequency Distribution of DEP Rel (Dependency Relations) Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='DEPRel',
                                                           column_xAxis_label='DEP Rel values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for DEPRel Values')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# sentiment ________________________________________________________________

    elif 'sentiment' in str(annotator_params) and 'sentiment' in outputFilename:
        if IO_csv_util.get_csvfile_headers(outputFilename, False)[0] == "Sentiment score":
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Sentiment score'], # sentiment score
                                                               chartTitle='Frequency Distribution of Sentiment Scores',
                                                               count_var=0, hover_label=[],
                                                               outputFileNameType='score', #'senti_bar',
                                                               column_xAxis_label='Sentiment score',
                                                               groupByList=['Document ID', 'Document'],
                                                               plotList=['Sentiment score'],
                                                               chart_title_label='Sentiment Statistics')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

        if IO_csv_util.get_csvfile_headers(outputFilename, False)[1] == "Sentiment label":
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Sentiment label'],
                                                               chartTitle='Frequency Distribution of Sentiment Labels',
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='label', #'senti_bar',
                                                               column_xAxis_label='Sentiment label',
                                                               groupByList=['Document ID', 'Document'],
                                                               plotList=['Sentiment label'],
                                                               chart_title_label='Sentiment Statistics')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# SVO and OpenIE ________________________________________________________________

    elif ('SVO' in str(annotator_params) and 'SVO' in outputFilename) or \
            ('OpenIE' in str(annotator_params) and 'OpenIE' in outputFilename):
        # create an SVO-unfiltered subdirectory of the main output directory
        import IO_files_util
        import os
        head, tail = os.path.split(outputDir)
        outputSVOUnFilterDir=head+os.sep+'SVO-form'
        if not os.path.isdir(outputSVOUnFilterDir):
            outputSVOUnFilterDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO-form',
                                                                        silent=True)
            if outputSVOUnFilterDir == '':
                return

        # plot Subjects
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputSVOUnFilterDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Subject (S)'],
                                                           chartTitle='Frequency Distribution of Subjects (unlemmatized, unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='S-form', #'S_bar',
                                                           column_xAxis_label='Subjects (unlemmatized, unfiltered)',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Subjects (unlemmatized, unfiltered)')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        # plot Verbs
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputSVOUnFilterDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Verb (V)'],
                                                           chartTitle='Frequency Distribution of Verbs (unlemmatized, unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='V-form', #'V_bar',
                                                           column_xAxis_label='Verbs (unlemmatized, unfiltered)',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Verbs (unlemmatized, unfiltered)')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        # plot Objects
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputSVOUnFilterDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Object (O)'],
                                                           chartTitle='Frequency Distribution of Objects (unlemmatized, unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='O-form', #'O_bar',
                                                           column_xAxis_label='Objects (unlemmatized, unfiltered)',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Objects (unlemmatized, unfiltered)')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# coref ________________________________________________________________

    if "coref table" in str(annotator_params) or "parser" in str(annotator_params) \
            or "SVO" in str(annotator_params):
        if "coref table" in str(annotator_params):
            param = "coref table"
        if "parser" in str(annotator_params):
            param = "CoNLL"
        if "SVO" in str(annotator_params):
            param = "SVO"
        # TODO temporary needs to restore
        # pronoun_files = check_pronouns(configFilename, outputFilename,
        #                          outputDir, filesToOpen,
        #                          createCharts,chartPackage, param, corefed_pronouns, all_pronouns)
        # if len(pronoun_files)>0:
        #     filesToOpen.extend(pronoun_files)

        if "coref table" in str(annotator_params):
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Pronoun'],
                                                               chartTitle='Frequency Distribution of Pronouns (Antecedents)',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='pronouns',  # 'O_bar',
                                                               column_xAxis_label='Pronouns (antecedents)',
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Referent'],
                                                               chartTitle='Frequency Distribution of Coreferences (Referents)',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='referents',  # 'O_bar',
                                                               column_xAxis_label='Coreferences (referents)',
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

    return filesToOpen

# the gender annotator displays results in an html file
def visualize_html_file(inputFilename, inputDir, outputDir, configFileName, dictFilename, genderCol=["Gender"], wordCol=[]):
    import html_annotator_dictionary_util
    chart_outputFilename=[]
    for col in genderCol:
        if col not in IO_csv_util.get_csvfile_headers(dictFilename, False):
            return chart_outputFilename
    # annotate the input file(s) for gender values
    csvValue_color_list = [genderCol, '|', 'FEMALE', 'red', '|', 'MALE', 'blue', '|']
    bold_var = True
    tagAnnotations = ['<span style="color: blue; font-weight: bold">', '</span>']
    chart_outputFilename = html_annotator_dictionary_util.dictionary_annotate(inputFilename, inputDir, outputDir, configFileName,
                                                             dictFilename, wordCol,
                                                             csvValue_color_list, bold_var, tagAnnotations,
                                                             fileType='.txt', fileSubc='gender')
    # the annotator returns a list rather than a string
    return chart_outputFilename

