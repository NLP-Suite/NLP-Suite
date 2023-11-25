
import charts_util
import reminders_util
import IO_csv_util

# outputFilename is actually the file containing fields to be charted
def parsers_annotators_visualization(configFilename, inputFilename, inputDir, outputDir, outputFilename,
                annotator_params, kwargs, createCharts, chartPackage, openFiles=True):
    # headers = IO_csv_util.get_csvfile_headers_pandas(outputFilename)
    # docCol = IO_csv_util.get_columnNumber_from_headerValue(headers, inputFilename)
    # docCol = docCol + 1  # we need to visualize the doc filename

    # generate visualization output ----------------------------------------------------------------
# Lemma ________________________________________________________________
    import os
    # cannot use the usual scriptName here otherwise it would be parsers_annotators_visualization_util
    #   and what we want is the calling script in config.csv, e.g., NER_config.csv
    # head, scriptName = os.path.split(os.path.basename(__file__))
    scriptName=configFilename.replace("_config.csv","")
    filesToOpen=[]
    if ("Lemma" in str(annotator_params) and 'Lemma' in outputFilename) or 'parse' in str(annotator_params):
        # reminders_util.checkReminder(scriptName, reminders_util.lemma_frequencies,
        #                              reminders_util.message_lemma_frequencies, True)
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Form','Lemma'],
                                                           chart_title='Frequency Distribution of Form & Lemma Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='form-lemma', #'POS_bar',
                                                           column_xAxis_label='Form & Lemma values',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Lemma Values')

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# All POS ________________________________________________________________

    if ('POS' in str(annotator_params) and 'POS' in outputFilename) or 'parse' in str(annotator_params):
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['POS'],
                                                           chart_title='Frequency Distribution of Part of Speech (POS) Tags',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='POS', #'POS_bar',
                                                           column_xAxis_label='POS (Part of Speech) tag values',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='POS (Part of Speech) Tag Values')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Form'],
                                                           chart_title='Frequency Distribution of Form Values', # by Part of Speech (POS) Tags
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='Form', #'POS_bar',
                                                           column_xAxis_label='Form values',
                                                           groupByList=['POS'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Form Values')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# NER ________________________________________________________________

    if ('NER' in str(annotator_params) and 'NER' in outputFilename) or 'parse' in str(annotator_params):
        reminders_util.checkReminder(scriptName, reminders_util.NER_frequencies,
                                     reminders_util.message_NER_frequencies)
        if IO_csv_util.get_csvfile_headers(outputFilename, False)[1] == "NER":
            # plot NER tag (e.g, LOCATION), standard bar and by Doc
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                               outputDir,
                               columns_to_be_plotted_xAxis=[],
                               columns_to_be_plotted_yAxis=['NER'],
                               chart_title='Frequency Distribution of NERs',
                               # count_var = 1 for columns of alphabetic values
                               count_var=1, hover_label=[],
                               outputFileNameType='NER-tag', #'NER_tag_bar',
                               column_xAxis_label='NER tags',
                               groupByList=['Document'],
                               plotList=['Frequency'],
                               chart_title_label='NER')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            # plot Form values by NER tag (e.g, Atlanta in LOCATION)
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                               outputDir,
                               columns_to_be_plotted_xAxis=[],
                               columns_to_be_plotted_yAxis=['Form'],
                               chart_title='Frequency Distribution of Form Values',
                               # count_var = 1 for columns of alphabetic values
                               count_var=1, hover_label=[],
                               outputFileNameType='Form', #'NER_tag_bar',
                               column_xAxis_label='Form values',
                               groupByList=['NER'],
                               plotList=['Frequency'],
                               chart_title_label='Form')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# generate visualization output ----------------------------------------------------------------
# parser ________________________________________________________________
# 'depparse' used for Stanza and spaCy
    if 'parse' in str(annotator_params): # and 'CoNLL' in outputFilename) or ('depparse' in str(annotator_params)):

        # Form & Lemma values charted above

        reminders_util.checkReminder(scriptName, reminders_util.DepRel_frequencies,
                                     reminders_util.message_DepRel_frequencies, True)
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['DepRel'],
                                                           chart_title='Frequency Distribution of DepRel (Dependency Relations) Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='DepRel',
                                                           column_xAxis_label='DepRel values',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='DepRel')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Form'],
                                                           chart_title='Frequency Distribution of Form Values', # by DepRel (Dependency Relations) Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='Form',
                                                           column_xAxis_label='Form values',
                                                           groupByList=['DepRel'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Form Values')

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# SPECIAL ANNOTATORS: date, gender, quote, sentiment, SVO, OpenIE
# date ________________________________________________________________
    # dates are extracted by the date annotator, but also as part of SVO and OpenIE
    if (('date' in str(annotator_params) and 'date' in outputFilename)) or \
            ('OpenIE' in str(annotator_params) and 'OpenIE' in outputFilename):
            # (('SVO' in str(annotator_params) and 'SVO' in outputFilename)) or \
            # visualizing normalized-date for SVO is done in SVO_util called in SVO_main
        # Date expressions are in the form yesterday, tomorrow morning, the day before Christmas
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Date expression'],
                                                           chart_title='Frequency Distribution of Date Expressions',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='date-express', #'NER_info_bar',
                                                           column_xAxis_label='Date expression',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Date Expressions')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

            # normalized dates are in the form PAST_REF, NEXT_IMMEDIATE P1D, ...
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Normalized date'],
                                                           chart_title='Frequency Distribution of Normalized Dates',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='date', #'NER_date_bar',
                                                           column_xAxis_label='Normalized date',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Normalized Dates')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

            # Date types are in the form PAST, PRESENT, OTHER
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Date type'],
                                                           chart_title='Frequency Distribution of Date Types',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='date-types', #'NER_info_bar',
                                                           column_xAxis_label='Date type',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Date Types')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# gender ________________________________________________________________

    if 'gender' in str(annotator_params) and 'gender' in outputFilename:
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Gender'],
                                                           chart_title='Frequency Distribution of Gender Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='gender-values', #'gender_bar',
                                                           column_xAxis_label='Gender values',
                                                           groupByList=['Document'],
                                                           plotList=['Gender'],
                                                           chart_title_label='Gender')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Word'],
                                                           chart_title='Frequency Distribution of Gendered Words',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='gender-words', #'gender_bar',
                                                           column_xAxis_label='Gender words',
                                                           groupByList=['Gender','Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Gendered Words')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = visualize_html_file(inputFilename, inputDir, outputDir, configFilename, outputFilename)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        headers=IO_csv_util.get_csvfile_headers(outputFilename)
        Sankey_limit1_var=12
        Sankey_limit2_var = 12
        three_way_Sankey = False
        var3 = None
        Sankey_limit3_var = None

        output_label = 'sankey'
        import IO_files_util
        outputFilename_sankey = IO_files_util.generate_output_file_name(outputFilename, inputDir, outputDir,
                                                                 '.html', output_label)
        outputFiles = charts_util.Sankey(outputFilename, outputFilename_sankey,
                            'Gender', Sankey_limit1_var, 'Word', Sankey_limit2_var, three_way_Sankey, var3, Sankey_limit3_var)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# quote ________________________________________________________________

    if 'quote' in str(annotator_params) and 'quote' in outputFilename:
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Speakers'],
                                                           chart_title='Frequency Distribution of Speakers\n(CoreNLP Quote Annotator)',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='quote', #'quote_bar',
                                                           column_xAxis_label='Speakers',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Quotes')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# sentiment ________________________________________________________________

    if 'sentiment' in str(annotator_params) and 'sentiment' in outputFilename:
        if IO_csv_util.get_csvfile_headers(outputFilename, False)[0] == "Sentiment score":
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Sentiment score'], # sentiment score
                                                               chart_title='Frequency Distribution of Sentiment Scores',
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='score', #'senti_bar',
                                                               column_xAxis_label='Sentiment score',
                                                               groupByList=['Document'],
                                                               plotList=['Sentiment score'],
                                                               chart_title_label='Sentiment Score Statistics')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if IO_csv_util.get_csvfile_headers(outputFilename, False)[1] == "Sentiment label":
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Sentiment label'],
                                                               chart_title='Frequency Distribution of Sentiment Labels',
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='label', #'senti_bar',
                                                               column_xAxis_label='Sentiment label',
                                                               groupByList=['Document'],
                                                               plotList=['Sentiment label'],
                                                               chart_title_label='Sentiment Label Statistics')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# generate visualization output ----------------------------------------------------------------
# SVO and OpenIE ________________________________________________________________

    if ('SVO' in str(annotator_params) and 'SVO' in outputFilename) or \
            ('OpenIE' in str(annotator_params) and 'OpenIE' in outputFilename):
        # create an SVO-unfiltered subdirectory of the main output directory
        import IO_files_util
        import os
        head, tail = os.path.split(outputDir)
        outputSVOUnFilterDir=head+os.sep+'SVO-form'
        if not os.path.isdir(outputSVOUnFilterDir):
            outputSVOUnFilterDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO_form',
                                                                        silent=True)
            if outputSVOUnFilterDir == '':
                return

        # wordclouds of locations, persons, organizations

        import wordclouds_util
        # run with all default values;
        prefer_horizontal = .9
        doNotListIndividualFiles = True
        collocation = False
        transformed_image_mask = []
        stopwords = ''

        column_name='Locations'

        textToProcess = IO_csv_util.get_csv_field_values(outputFilename, column_name, uniqueValues=False, returnList=False)

        outputFiles = wordclouds_util.display_wordCloud(outputFilename, '', outputDir, textToProcess, doNotListIndividualFiles,
                              transformed_image_mask, stopwords, collocation, prefer_horizontal, bg_image=None,
                              bg_image_flag=True, font=None, max_words=100)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                # rename outputfile not to be overwritten by the next wordclouds
                os.rename(outputFiles,outputFiles[:-4] + "_locations.png")
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        column_name='Persons'

        textToProcess = IO_csv_util.get_csv_field_values(outputFilename, column_name, uniqueValues=False, returnList=False)

        outputFiles = wordclouds_util.display_wordCloud(outputFilename, '', outputDir, textToProcess, doNotListIndividualFiles,
                              transformed_image_mask, stopwords, collocation, prefer_horizontal, bg_image=None,
                              bg_image_flag=True, font=None, max_words=100)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                # rename outputfile not to be overwritten by the next wordclouds
                os.rename(outputFiles,outputFiles[:-4] + "_persons.png")
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        column_name='Organizations'

        textToProcess = IO_csv_util.get_csv_field_values(outputFilename, column_name, uniqueValues=False, returnList=False)

        outputFiles = wordclouds_util.display_wordCloud(outputFilename, '', outputDir, textToProcess, doNotListIndividualFiles,
                              transformed_image_mask, stopwords, collocation, prefer_horizontal, bg_image=None,
                              bg_image_flag=True, font=None, max_words=100)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                os.rename(outputFiles,outputFiles[:-4] + "_organizations.png")
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        # plot Subjects
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputSVOUnFilterDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Subject (S)'],
                                                           chart_title='Frequency Distribution of Subjects (unlemmatized, unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='S-form', #'S_bar',
                                                           column_xAxis_label='Subjects (unlemmatized, unfiltered)',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Subjects (unlemmatized, unfiltered)')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        # plot Verbs
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputSVOUnFilterDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Verb (V)'],
                                                           chart_title='Frequency Distribution of Verbs (unlemmatized, unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='V-form', #'V_bar',
                                                           column_xAxis_label='Verbs (unlemmatized, unfiltered)',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Verbs (unlemmatized, unfiltered)')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        # plot Objects
        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputSVOUnFilterDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Object (O)'],
                                                           chart_title='Frequency Distribution of Objects (unlemmatized, unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='O-form', #'O_bar',
                                                           column_xAxis_label='Objects (unlemmatized, unfiltered)',
                                                           groupByList=['Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Objects (unlemmatized, unfiltered)')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

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
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Pronoun'],
                                                               chart_title='Frequency Distribution of Pronouns (Antecedents)',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='pronouns',  # 'O_bar',
                                                               column_xAxis_label='Pronouns (antecedents)',
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Referent'],
                                                               chart_title='Frequency Distribution of Coreferences (Referents)',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='referents',  # 'O_bar',
                                                               column_xAxis_label='Coreferences (referents)',
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)


            headers=IO_csv_util.get_csvfile_headers(outputFilename)
            Sankey_limit1_var=12
            Sankey_limit2_var = 12
            three_way_Sankey = False
            var3 = None
            Sankey_limit3_var = None

            output_label = 'sankey'
            import IO_files_util
            outputFilename_sankey = IO_files_util.generate_output_file_name(outputFilename, inputDir, outputDir,
                                                                     '.html', output_label)
            outputFiles = charts_util.Sankey(outputFilename, outputFilename_sankey,
                                'Pronoun', Sankey_limit1_var, 'Referent', Sankey_limit2_var, three_way_Sankey, var3, Sankey_limit3_var)

            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    return filesToOpen

# the gender annotator displays results in an html file
def visualize_html_file(inputFilename, inputDir, outputDir, configFileName, dictFilename, genderCol=["Gender"], wordCol=[]):
    import html_annotator_dictionary_util
    outputFiles=[]
    for col in genderCol:
        if col not in IO_csv_util.get_csvfile_headers(dictFilename, False):
            return outputFiles
    # annotate the input file(s) for gender values
    csvValue_color_list = [genderCol, '|', 'FEMALE', 'red', '|', 'MALE', 'blue', '|']
    bold_var = True
    tagAnnotations = ['<span style="color: blue; font-weight: bold">', '</span>']
    outputFiles = html_annotator_dictionary_util.dictionary_annotate(inputFilename, inputDir, outputDir, configFileName,
                                                             dictFilename, wordCol,
                                                             csvValue_color_list, bold_var, tagAnnotations,
                                                             fileType='.txt', fileSubc='gender')
    # the annotator returns a list rather than a string
    return outputFiles

