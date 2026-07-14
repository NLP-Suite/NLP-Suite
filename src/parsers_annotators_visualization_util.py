
import charts_util
import reminders_util
import IO_csv_util

# outputFilename is actually the file containing fields to be charted
def parsers_annotators_visualization(configFilename, inputFilename, inputDir, outputDir, outputFilename,
                annotator_params, kwargs, chartPackage, dataTransformation, openFiles=True):
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

    # Honor "No charts": callers that only want the parsed CSV (e.g. the Corpus Profiler's POS pass)
    # pass chartPackage='No charts' to suppress these frequency charts. Charting a per-token CoNLL
    # table is pointless and, on a large corpus (>1M tokens), triggers the Excel->Plotly auto-switch
    # into a giant, useless chart. Return no chart files.
    if str(chartPackage) == 'No charts':
        return []

    head, tail = os.path.split(outputFilename)
    temp_outputFilename=tail

    if ("Lemma" in str(annotator_params) and 'Lemma' in temp_outputFilename) or 'parse' in str(annotator_params):
        # reminders_util.checkReminder(scriptName, reminders_util.lemma_frequencies,
        #                              reminders_util.message_lemma_frequencies, True)
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Form','Lemma'], title='Frequency Distribution of Form & Lemma Values', x_label='Form & Lemma values', file_label='form-lemma', plot_list=['Frequency'], title_label='Lemma Values')

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# All POS ________________________________________________________________

    if ('POS' in str(annotator_params) and 'POS' in temp_outputFilename) or 'parse' in str(annotator_params):
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['POS'], title='Frequency Distribution of Part of Speech (POS) Tags', x_label='POS (Part of Speech) tag values', file_label='POS', plot_list=['Frequency'], title_label='POS (Part of Speech) Tag Values')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Form'], title='Frequency Distribution of Form Values', x_label='Form values', file_label='Form', group_by=['POS'], plot_list=['Frequency'], title_label='Form Values')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# NER ________________________________________________________________

    if ('NER' in str(annotator_params) and 'NER' in temp_outputFilename) or 'parse' in str(annotator_params):
        reminders_util.checkReminder(scriptName, reminders_util.NER_frequencies,
                                     reminders_util.message_NER_frequencies)

        # SIMILAR CODE IS IN Stanford_CoreNLP_util
        # when Stanford_CoreNLP_utils called from parsers_annotators_main,
        # the kwargs do not contain the value['NERs'] the code would break
        try:
            if len(str.split(kwargs['NERs'])) == 1:
                NER_tag = str(kwargs['NERs'])
            elif len(str.split(kwargs['NERs'])) > 10 and len(str.split(kwargs['NERs'])) < 20:
                NER_tag = 'MISC'
            elif len(str.split(kwargs['NERs'])) > 20:
                NER_tag = 'ALL_NER'
            else:
                if 'CITY' in str(kwargs['NERs']) and 'STATE_OR_PROVINCE' and str(kwargs['NERs']) and 'COUNTRY' in str(
                        kwargs['NERs']) and 'LOCATION' in str(kwargs['NERs']):
                    NER_tag = 'SPACE'
                elif 'NUMBER' in str(kwargs['NERs']) and 'ORDINAL' and str(kwargs['NERs']) and 'PERCENT' in str(
                        kwargs['NERs']):
                    outpNER_tag = 'NUMBERS'
                elif 'PERSON' in str(kwargs['NERs']) and 'ORGANIZATION' in str(kwargs['NERs']):
                    NER_tag = 'ACTORS'
                elif 'DATE' in str(kwargs['NERs']) and 'TIME' in str(kwargs['NERs']) and 'DURATION' in str(
                        kwargs['NERs']) and 'SET' in str(kwargs['NERs']):
                    NER_tag = 'DATES'
                else:
                    NER_tag = str(kwargs['NERs'])
        except:
            NER_tag = 'ALL NERs'

        if IO_csv_util.get_csvfile_headers(outputFilename, False)[1] == "NER":
            # plot NER tag (e.g, LOCATION), standard bar and by Doc
            outputFiles = charts_util.plot(outputFilename, outputDir, columns=['NER'], title='Frequency Distribution of NER Tags', x_label='NER tags', file_label='NER-tag', plot_list=['Frequency'], title_label='NER')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Word'], title='Frequency Distribution of NER ' + NER_tag + ' Values', x_label='NER ' + NER_tag + ' expression', file_label='NER-tag-value', title_label='NER Tag Values')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            # plot Form values by NER tag (e.g, Atlanta in LOCATION)
            outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Form'], title='Frequency Distribution of Form Values', x_label='Form values', file_label='Form', group_by=['NER'], plot_list=['Frequency'], title_label='Form')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            # plot Named Entities (merged multi-word expressions, e.g., "New York") - distinct from
            # the per-token 'Form' chart above. Only when the Multi-Word Expression column exists
            # (spaCy / Stanza NER output).
            try:
                import pandas as _pd_mwe
                _mwe_cols = list(_pd_mwe.read_csv(outputFilename, nrows=0, encoding='utf-8').columns)
            except Exception:
                _mwe_cols = []
            if 'Multi-Word Expression' in _mwe_cols:
                outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Multi-Word Expression'], title='Frequency Distribution of Named Entities (Multi-Word Expressions)', x_label='Named entities (multi-word expressions)', file_label='Named-Entity', group_by=['NER'], plot_list=['Frequency'], title_label='Named Entity')
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
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['DepRel'], title='Frequency Distribution of DepRel (Dependency Relations) Values', x_label='DepRel values', file_label='DepRel', plot_list=['Frequency'], title_label='DepRel')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Form'], title='Frequency Distribution of Form Values', x_label='Form values', file_label='Form', group_by=['DepRel'], plot_list=['Frequency'], title_label='Form Values')

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# SPECIAL ANNOTATORS: date, gender, quote, sentiment, SVO, OpenIE
# date ________________________________________________________________
    # dates are extracted by the date annotator, but also as part of SVO and OpenIE
    if (('date' in str(annotator_params) and 'date' in temp_outputFilename)) or \
            ('OpenIE' in str(annotator_params) and 'OpenIE' in temp_outputFilename):
            # (('SVO' in str(annotator_params) and 'SVO' in outputFilename)) or \
            # visualizing normalized-date for SVO is done in SVO_util called in SVO_main
        # Date expressions are in the form yesterday, tomorrow morning, the day before Christmas
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Date expression'], title='Frequency Distribution of Date Expressions', x_label='Date expression', file_label='date-express', plot_list=['Frequency'], title_label='Date Expressions')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

            # normalized dates are in the form PAST_REF, NEXT_IMMEDIATE P1D, ...
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Normalized date'], title='Frequency Distribution of Normalized Dates', x_label='Normalized date', file_label='date', plot_list=['Frequency'], title_label='Normalized Dates')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

            # Date types are in the form PAST, PRESENT, OTHER
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Date type'], title='Frequency Distribution of Date Types', x_label='Date type', file_label='date-types', plot_list=['Frequency'], title_label='Date Types')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# gender ________________________________________________________________

    if 'gender' in str(annotator_params) and 'gender' in temp_outputFilename:
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Gender'], title='Frequency Distribution of Gender Values', x_label='Gender values', file_label='gender-values', plot_list=['Gender'], title_label='Gender')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Word'], title='Frequency Distribution of Gendered Words', x_label='Gender words', file_label='gender-words', group_by=['Gender','Document'], plot_list=['Frequency'], title_label='Gendered Words')
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
        Sankey_limit1_var=5
        Sankey_limit2_var = 10
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

    if 'quote' in str(annotator_params) and 'quote' in temp_outputFilename:
        outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Speakers'], title='Frequency Distribution of Speakers\n(CoreNLP Quote Annotator)', x_label='Speakers', file_label='quote', plot_list=['Frequency'], title_label='Quotes')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # generate visualization output ----------------------------------------------------------------
# sentiment ________________________________________________________________

    if 'sentiment' in str(annotator_params) and 'sentiment' in temp_outputFilename:
        if IO_csv_util.get_csvfile_headers(outputFilename, False)[0] == "Sentiment score":
            outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Sentiment score'], title='Frequency Distribution of Sentiment Scores', x_label='Sentiment score', file_label='score', plot_list=['Sentiment score'], title_label='Sentiment Score Statistics')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if IO_csv_util.get_csvfile_headers(outputFilename, False)[1] == "Sentiment label":
            outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Sentiment label'], title='Frequency Distribution of Sentiment Labels', x_label='Sentiment label', file_label='label', plot_list=['Sentiment label'], title_label='Sentiment Label Statistics')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# generate visualization output ----------------------------------------------------------------
# SVO and OpenIE ________________________________________________________________

    if ('SVO' in str(annotator_params) and 'SVO' in temp_outputFilename) or \
            ('OpenIE' in str(annotator_params) and 'OpenIE' in temp_outputFilename):
        # create an SVO-unfiltered subdirectory of the main output directory
        import IO_files_util
        import os
        outputSVOUnFilterDir = outputDir + os.sep + 'SVO_form'
        if not os.path.isdir(outputSVOUnFilterDir):
            outputSVOUnFilterDir = IO_files_util.make_output_subdirectory('', '', outputDir, label='SVO_form',
                                                                        silent=True)
            if outputSVOUnFilterDir == '':
                return

            Sankey_limit1_var=5
            Sankey_limit2_var = 10
            Sankey_limit3_var = 20
            three_way_Sankey = True

            output_label = 'sankey'
            import IO_files_util
            outputFilename_sankey = IO_files_util.generate_output_file_name(outputFilename, inputDir, outputDir,
                                                                     '.html', output_label)
            outputFiles = charts_util.Sankey(outputFilename, outputFilename_sankey,
                                'Subject (S)', Sankey_limit1_var, 'Verb (V)', Sankey_limit2_var, three_way_Sankey, 'Object (O)', Sankey_limit3_var)

            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            # output_label = 'sunburst'
            # outputFilename_sunburst = IO_files_util.generate_output_file_name(outputFile, inputDir, outputDir,
            #                                                                 '.html', output_label)
            outputFilename_sunburst = ''
            csv_file_categorical_field_list = [['Subject (S)|'], ['Verb (V)|'], ['Object (O)|']]
            suntree = 3
            fixed_param_var = 15
            rate_param_var = None
            base_param_var = None
            filter_options_var = 'Fixed parameter'
            case_sensitive_var = 1
            outputFiles = charts_util.Sunburst_Treemap(outputFilename, outputFilename_sunburst, outputDir, csv_file_categorical_field_list, suntree, fixed_param_var, rate_param_var, base_param_var, filter_options_var, case_sensitive_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# wordclouds of locations, persons, organizations

        # import wordclouds_util
        # # run with all default values;
        # prefer_horizontal = .9
        # doNotListIndividualFiles = True
        # collocation = False
        # transformed_image_mask = []
        # stopwords = ''
        #
        # column_name='Locations'
        #
        # textToProcess = IO_csv_util.get_csv_field_values(outputFilename, column_name, uniqueValues=False, returnList=False)
        #
        # outputFiles = wordclouds_util.display_wordCloud(outputFilename, '', outputDir, textToProcess, doNotListIndividualFiles,
        #                       transformed_image_mask, stopwords, collocation, prefer_horizontal, bg_image=None,
        #                       bg_image_flag=True, font=None, max_words=100)
        #
        # if outputFiles!=None:
        #     if isinstance(outputFiles, str):
        #         # rename outputfile not to be overwritten by the next wordclouds
        #         os.rename(outputFiles,outputFiles[:-4] + "_locations.png")
        #         filesToOpen.append(outputFiles)
        #     else:
        #         filesToOpen.extend(outputFiles)
        #
        # column_name='Persons'
        #
        # textToProcess = IO_csv_util.get_csv_field_values(outputFilename, column_name, uniqueValues=False, returnList=False)
        #
        # outputFiles = wordclouds_util.display_wordCloud(outputFilename, '', outputDir, textToProcess, doNotListIndividualFiles,
        #                       transformed_image_mask, stopwords, collocation, prefer_horizontal, bg_image=None,
        #                       bg_image_flag=True, font=None, max_words=100)
        #
        # if outputFiles!=None:
        #     if isinstance(outputFiles, str):
        #         # rename outputfile not to be overwritten by the next wordclouds
        #         os.rename(outputFiles,outputFiles[:-4] + "_persons.png")
        #         filesToOpen.append(outputFiles)
        #     else:
        #         filesToOpen.extend(outputFiles)
        #
        # column_name='Organizations'
        #
        # textToProcess = IO_csv_util.get_csv_field_values(outputFilename, column_name, uniqueValues=False, returnList=False)
        #
        # outputFiles = wordclouds_util.display_wordCloud(outputFilename, '', outputDir, textToProcess, doNotListIndividualFiles,
        #                       transformed_image_mask, stopwords, collocation, prefer_horizontal, bg_image=None,
        #                       bg_image_flag=True, font=None, max_words=100)
        #
        # if outputFiles!=None:
        #     if isinstance(outputFiles, str):
        #         os.rename(outputFiles,outputFiles[:-4] + "_organizations.png")
        #         filesToOpen.append(outputFiles)
        #     else:
        #         filesToOpen.extend(outputFiles)

# plot Subjects
        outputFiles = charts_util.plot(outputFilename, outputSVOUnFilterDir, columns=['Subject (S)'], title='Frequency Distribution of Subjects (unlemmatized, unfiltered)', x_label='Subjects (unlemmatized, unfiltered)', file_label='S-form', plot_list=['Frequency'], title_label='Subjects (unlemmatized, unfiltered)')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# plot Verbs
        outputFiles = charts_util.plot(outputFilename, outputSVOUnFilterDir, columns=['Verb (V)'], title='Frequency Distribution of Verbs (unlemmatized, unfiltered)', x_label='Verbs (unlemmatized, unfiltered)', file_label='V-form', plot_list=['Frequency'], title_label='Verbs (unlemmatized, unfiltered)')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# plot Objects
        outputFiles = charts_util.plot(outputFilename, outputSVOUnFilterDir, columns=['Object (O)'], title='Frequency Distribution of Objects (unlemmatized, unfiltered)', x_label='Objects (unlemmatized, unfiltered)', file_label='O-form', plot_list=['Frequency'], title_label='Objects (unlemmatized, unfiltered)')
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
        #                          chartPackage, dataTransformation, param, corefed_pronouns, all_pronouns)
        # if len(pronoun_files)>0:
        #     filesToOpen.extend(pronoun_files)

        if "coref table" in str(annotator_params):
            outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Pronoun'], title='Frequency Distribution of Pronouns (Antecedents)', x_label='Pronouns (antecedents)', file_label='pronouns', group_by=None)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            outputFiles = charts_util.plot(outputFilename, outputDir, columns=['Referent'], title='Frequency Distribution of Coreferences (Referents)', x_label='Coreferences (referents)', file_label='referents', group_by=None)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)


            headers=IO_csv_util.get_csvfile_headers(outputFilename)
            Sankey_limit1_var=5
            Sankey_limit2_var = 10
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

