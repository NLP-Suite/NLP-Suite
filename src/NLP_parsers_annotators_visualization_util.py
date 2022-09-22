
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
                                                           groupByList=['Document ID','Document'],
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
                                                           groupByList=['Document ID','Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='POS Tag Values')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# date ________________________________________________________________

    elif 'date' in str(annotator_params) and 'date' in outputFilename:
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
                                                           outputFileNameType='gender', #'gender_bar',
                                                           column_xAxis_label='Gender values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Statistical Measures for Gender')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = visualize_html_file(inputFilename, inputDir, outputDir, outputFilename)
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

# generate visualization output ----------------------------------------------------------------
# quote ________________________________________________________________

    elif 'quote' in str(annotator_params) and 'quote' in outputFilename:
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Speakers'],
                                                           chartTitle='Frequency Distribution of Speakers',
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
# parser ________________________________________________________________

    elif 'parse' in str(annotator_params) and 'CoNLL' in outputFilename:

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
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Sentiment label'], # sentiment score
                                                               chartTitle='Frequency Distribution of Sentiment Scores',
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='sent', #'senti_bar',
                                                               column_xAxis_label='Sentiment score',
                                                               groupByList=['Document ID', 'Document'],
                                                               plotList=['Sentiment score'],
                                                               chart_title_label='Sentiment Statistics')
            if chart_outputFilename != None:
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
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
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
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
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
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        if 'SVO' in str(annotator_params):
            for key, value in kwargs.items():
                if key == "gender_var" and value == True:
                    chart_outputFilename = visualize_html_file(inputFilename, inputDir, outputDir, kwargs["gender_filename"],
                                                      genderCol=["S Gender", "O Gender"], wordCol=["Subject (S)", "Object (O)"])
                    if chart_outputFilename!=None:
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
        # pronoun_files = check_pronouns(config_filename, outputFilename,
        #                          outputDir, filesToOpen,
        #                          createCharts,chartPackage, param, corefed_pronouns, all_pronouns)
        # if len(pronoun_files)>0:
        #     filesToOpen.extend(pronoun_files)

        if "coref table" in str(annotator_params):
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Pronoun'],
                                                               chartTitle='Frequency Distribution of Pronouns',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='pron',  # 'O_bar',
                                                               column_xAxis_label='Pronoun',
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Reference'],
                                                               chartTitle='Frequency Distribution of Coreferences',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='coref',  # 'O_bar',
                                                               column_xAxis_label='Coreferences',
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

def count_pronouns(json):
    result = 0
    for sentence in json['sentences']:
        # sentenceID = sentenceID + 1
        for token in sentence['tokens']:
            if token["pos"] == "PRP$" or token["pos"] == "PRP":
                result += 1
    return result


def check_pronouns(config_filename, inputFilename, outputDir, filesToOpen, createCharts,chartPackage, option, corefed_pronouns, all_pronouns: int):
    return_files = []
    df = pd.read_csv(inputFilename)
    if df.empty:
        return return_files
    # pronoun cases:
    #   nominative: I, you, he/she, it, we, they
    #   objective: me, you, him, her, it, them
    #   possessive: my, mine, his/her(s), its, our(s), their, your, yours
    #   reflexive: myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves
    pronouns = ["i", "you", "he", "she", "it", "we", "they", "me", "her", "him", "us", "them", "my", "mine", "hers", "his", "its", "our", "ours", "their", "your", "yours", "myself", "yourself", "himself", "herself", "oneself", "itself", "ourselves", "yourselves", "themselves"]
    total_count = 0
    pronouns_count = {"i": 0, "you": 0, "he": 0, "she": 0, "it": 0, "we": 0, "they": 0, "me": 0, "her": 0, "him": 0, "us": 0, "them": 0, "my": 0, "mine": 0, "hers": 0, "his": 0, "its": 0, "our": 0, "ours": 0, "their": 0, "your": 0, "yours": 0, "myself": 0, "yourself": 0, "himself": 0, "herself": 0, "oneself": 0, "itself": 0, "ourselves": 0, "yourselves": 0, "themselves": 0}
    for _, row in df.iterrows():
        if option == "SVO":
            if (not pd.isna(row["Subject (S)"])) and (str(row["Subject (S)"]).lower() in pronouns):
                total_count+=1
                pronouns_count[str(row["Subject (S)"]).lower()] += 1
            if (not pd.isna(row["Object (O)"])) and (str(row["Object (O)"]).lower() in pronouns):
                total_count+=1
                pronouns_count[str(row["Object (O)"]).lower()] += 1
        elif option == "CoNLL":
            if (not pd.isna(row["Form"])) and (row["Form"].lower() in pronouns):
                total_count+=1
                pronouns_count[row["Form"].lower()] += 1
        elif option == "coref table":
            if (not pd.isna(row["Pronoun"])):
                total_count += 1
                try:
                    # some pronouns extracted by CoreNLP coref as such may not be in the list
                    #   e.g., "we both" leading to error
                    pronouns_count[row["Pronoun"].lower()] += 1
                except:
                    continue
        else:
            print ("Wrong Option value!")
            return []
    pronouns_count["I"] = pronouns_count.pop("i")
    if total_count > 0:
        if option != "coref table":
            reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_pronouns,
                                         reminders_util.message_CoreNLP_pronouns, True)
            return return_files
        else:
            #for coref, total count = number of resolved pronouns, the all_pronouns in the input is the number
            #   of all pronouns in the text
            coref_rate = round((corefed_pronouns / all_pronouns) * 100, 2)
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Coreference results',
                "Number of pronouns: " + str(
                all_pronouns) + "\nNumber of coreferenced pronouns: " + str(
                corefed_pronouns) + "\nPronouns coreference rate: " + str(coref_rate))
            # save to csv file and run visualization
            outputFilename= IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv','coref-sum')
            with open(outputFilename, "w", newline="", encoding='utf-8', errors='ignore') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(
                    ["Number of Pronouns", "Number of Coreferenced Pronouns", "Pronouns Coreference Rate"])
                writer.writerow([all_pronouns, corefed_pronouns, coref_rate])
                csvFile.close()
            # no need to display since the chart will contain the values
            # return_files.append(outputFilename)

            if createCharts:
                columns_to_be_plotted_xAxis=[]
                columns_to_be_plotted_yAxis=["Number of Pronouns", "Number of Coreferenced Pronouns", "Pronouns Coreference Rate"]
                chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                                   outputDir,
                                                                   columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                                   chartTitle='Coreferenced Pronouns',
                                                                   # count_var = 1 for columns of alphabetic values
                                                                   count_var=0, hover_label=[],
                                                                   outputFileNameType='', #'pronouns_bar',
                                                                   column_xAxis_label='Coreference values',
                                                                   groupByList=[],
                                                                   plotList=[],
                                                                   chart_title_label='')
                if chart_outputFilename != None:
                    if len(chart_outputFilename) > 0:
                        return_files.extend(chart_outputFilename)
    return return_files
