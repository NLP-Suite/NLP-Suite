
import charts_util
import reminders_util
import IO_csv_util

def parsers_annotators_visualization(config_filename, inputFilename, inputDir, outputDir, outputFilename, annotator_params, kwargs, createCharts, chartPackage):
# generate visualization output ----------------------------------------------------------------
# Lemma ________________________________________________________________

    filesToOpen=[]
    if "Lemma" in str(annotator_params) and 'Lemma' in outputFilename:
        # reminders_util.checkReminder(config_filename, reminders_util.lemma_frequencies,
        #                              reminders_util.message_lemma_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Form','Lemma'],
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
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['POStag'],
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
        reminders_util.checkReminder(config_filename, reminders_util.NER_frequencies,
                                     reminders_util.message_NER_frequencies, True)
        if IO_csv_util.get_csvfile_headers(outputFilename, False)[1] == "NER Tag":
            # plot NER tag (e.g, LOCATION)
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                               outputDir,
                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['NER Tag'],
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

            if len(kwargs['NERs'])>1:
                ner_tags = 'Multi-tags'
            else:
                ner_tags = str(kwargs['NERs'][0])
            # plot the words contained in each NER tag (e.g, the word 'Rome' in NER tag LOCATION)
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                       outputDir,
                                       columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Word'],
                                       chartTitle='Frequency Distribution of Words by NER ' + ner_tags,
                                       # count_var = 1 for columns of alphabetic values
                                       count_var=1, hover_label=[],
                                       outputFileNameType='NER-word', #'NER_word_bar',
                                       column_xAxis_label='Word',
                                       groupByList=['Document ID','Document'],
                                       plotList=['Frequency'],
                                       chart_title_label='NER Words')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

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
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Date expression'],
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
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Normalized date'],
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
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Date type'],
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
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Gender'],
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
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Word'],
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

        chart_outputFilename = visualize_html_file(inputFilename, inputDir, outputDir, outputFilename)
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)


# generate visualization output ----------------------------------------------------------------
# parser ________________________________________________________________
    # 'depparse' used for Stanza and spaCy
    elif ('parse' in str(annotator_params) and 'CoNLL' in outputFilename) or ('depparse' in str(annotator_params)):

        # Form & Lemma values
        # reminders_util.checkReminder(config_filename, reminders_util.lemma_frequencies,
        #                              reminders_util.message_lemma_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Form','Lemma'],
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
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Speakers'],
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
# POStag values in CoNLL table
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['POStag'],
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
# NER Tags in CoNLL table _____________________________________________________________________
        reminders_util.checkReminder(config_filename, reminders_util.NER_frequencies,
                                     reminders_util.message_NER_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['NER'],
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
        reminders_util.checkReminder(config_filename, reminders_util.DepRel_frequencies,
                                     reminders_util.message_DepRel_frequencies, True)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['DepRel'],
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
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Sentiment score'], # sentiment score
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
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Sentiment label'],
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
# SVO OpenIE ________________________________________________________________

    elif ('SVO' in str(annotator_params) and 'SVO' in outputFilename) or \
            ('OpenIE' in str(annotator_params) and 'OpenIE' in outputFilename):
        # plot Subjects
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Subject (S)'],
                                                           chartTitle='Frequency Distribution of Subjects (unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='S-unfiltr', #'S_bar',
                                                           column_xAxis_label='Subjects (unfiltered)',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Subjects (unfiltered)')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        # plot Verbs
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Verb (V)'],
                                                           chartTitle='Frequency Distribution of Verbs (unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='V-unfiltr', #'V_bar',
                                                           column_xAxis_label='Verbs (unfiltered)',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Verbs (unfiltered)')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        # plot Objects
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Object (O)'],
                                                           chartTitle='Frequency Distribution of Objects (unfiltered)',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='O-unfiltr', #'O_bar',
                                                           column_xAxis_label='Objects (unfiltered)',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Objects (unfiltered)')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        # if 'SVO' in str(annotator_params):
        #     for key, value in kwargs.items():
        #         if key == "gender_var" and value == True:
        #             chart_outputFilename = visualize_html_file(inputFilename, inputDir, outputDir+os.sep+"gender", kwargs["gender_filename_html"],
        #                                               genderCol=["S Gender", "O Gender"], wordCol=["Subject (S)", "Object (O)"])
        #             if chart_outputFilename!=None:
        #                 if len(chart_outputFilename) > 0:
        #                     filesToOpen.extend(chart_outputFilename)

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
        # pronoun_files = check_pronouns(config_filename, outputFilename,
        #                          outputDir, filesToOpen,
        #                          createCharts,chartPackage, param, corefed_pronouns, all_pronouns)
        # if len(pronoun_files)>0:
        #     filesToOpen.extend(pronoun_files)

        if "coref table" in str(annotator_params):
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Pronoun'],
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
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Referent'],
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
def visualize_html_file(inputFilename, inputDir, outputDir, dictFilename, genderCol=["Gender"], wordCol=[]):
    import html_annotator_dictionary_util
    chart_outputFilename=[]
    for col in genderCol:
        if col not in IO_csv_util.get_csvfile_headers(dictFilename, False):
            return chart_outputFilename
    # annotate the input file(s) for gender values
    csvValue_color_list = [genderCol, '|', 'FEMALE', 'red', '|', 'MALE', 'blue', '|']
    bold_var = True
    tagAnnotations = ['<span style="color: blue; font-weight: bold">', '</span>']
    chart_outputFilename = html_annotator_dictionary_util.dictionary_annotate(inputFilename, inputDir, outputDir,
                                                             dictFilename, wordCol,
                                                             csvValue_color_list, bold_var, tagAnnotations,
                                                             fileType='.txt', fileSubc='gender')
    # the annotator returns a list rather than a string
    return chart_outputFilename

