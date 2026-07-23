import numpy as np
import pandas as pd
# from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text, tokenize_stanza_text, lemmatize_stanza_word
import os

import IO_files_util
import IO_user_interface_util
import charts_util
import IO_csv_util

# notSure = set()
# added = set()
#
# # svo_CoreNLP_single_file is the individual file when processing a directory;
# # svo_CoreNLP_merged_file is the merged svo csv file
# # TODO NOT USED
# #   output with Document ID as first field is wrong according to new standard NLP Suite output layout
# def extract_CoreNLP_SVO(svo_triplets, svo_CoreNLP_single_file, svo_CoreNLP_merged_file, field_names, document_index, Document):
#     """
#     Extract SVO triplets form a Sentence object.
#     """
#     import csv
#
#     global notSure
#     global added
#
#     result = IO_files_util.openCSVFile(svo_CoreNLP_single_file, 'w')
#     if not result:
#         return
#     svo_writer = csv.DictWriter(result, fieldnames=field_names)
#     svo_writer.writeheader()
#     if svo_CoreNLP_merged_file:
#         merge_result = IO_files_util.openCSVFile(svo_CoreNLP_merged_file, 'a')
#         if not merge_result:
#             return
#         svo_CoreNLP_writer = csv.DictWriter(merge_result, fieldnames=field_names)
#     for svo in svo_triplets:
#         # RF if len(svo[2]) == 0 or len(svo[3]) == 0:
#         if not (svo[2] and svo[3] and svo[4]):
#             continue
#         # check if the triple needs to be included
#
#         if svo[2] == "Inferred_Subject_Passive" and (svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]) not in added:
#             notSure.add((svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]))
#             continue
#         if svo[2] != "Inferred_Subject_Passive":
#             if (svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]) in notSure:
#                 notSure.remove((svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]))
#             # before writing row, split location
#             if " " in svo[5]:
#                 location_list = svo[5].split(" ")
#                 for each_location in location_list:
#                     svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
#                                          'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
#                                          'S': svo[2], 'V': svo[3], 'O': svo[4],
#                                          'Time': svo[6], 'Location': each_location, 'Person': svo[7],
#                                          'Time stamp': svo[8], field_names[10]: svo[1]
#                                          })
#                     if svo_CoreNLP_merged_file:
#                         svo_CoreNLP_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
#                                                     'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
#                                                     'S': svo[2], 'V': svo[3], 'O': svo[4],
#                                                     'Time': svo[6], 'Location': each_location, 'Person': svo[7],
#                                                     'Time stamp': svo[8], field_names[10]: svo[1]
#                                                     })
#             else:
#                 svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
#                                      'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
#                                      'S': svo[2], 'V': svo[3], 'O': svo[4],
#                                      'Time': svo[6], 'Location': svo[5], 'Person': svo[7],
#                                      'Time stamp': svo[8], field_names[10]: svo[1]
#                                      })
#                 if svo_CoreNLP_merged_file:
#                     svo_CoreNLP_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
#                                                 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
#                                                 'S': svo[2], 'V': svo[3], 'O': svo[4],
#                                                 'Time': svo[6], 'Location': svo[5], 'Person': svo[7],
#                                                 'Time stamp': svo[8],
#                                                 field_names[10]: svo[1]
#                                                 })
#             added.add((svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]))


def visualize_SVOs(fileName, outputDir, chartPackage, dataTransformation, filesToOpen, openFiles):
    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(fileName)
    if nRecords==0:
        return
    if 'lemma' in fileName:
        label = 'lemmatized'
        label1 = 'lemma'
    elif 'filter' in fileName:
        label = 'filtered'
        label1 = 'filter'
    outputFiles = charts_util.plot(fileName, outputDir, columns=['Subject (S)'], title='Frequency Distribution of Subjects (' + label + ')', x_label='Subjects (' + label + ')', file_label='S-' + label1, plot_list=['Frequency'], title_label='Subjects (' + label + ')')

    if openFiles and outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    outputFiles = charts_util.plot(fileName, outputDir, columns=['Verb (V)'], title='Frequency Distribution of Verbs (' + label + ')', x_label='Verbs (' + label + ')', file_label='V-' + label1, plot_list=['Frequency'], title_label='Verbs (' + label + ')')
    if openFiles and outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    outputFiles = charts_util.plot(fileName, outputDir, columns=['Object (O)'], title='Frequency Distribution of Objects (' + label + ')', x_label='Objects (' + label + ')', file_label='O-' + label1, plot_list=['Frequency'], title_label='Objects (' + label + ')')

    if openFiles and outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    return filesToOpen

# def lemmatize_filter_svo(window, svo_file_name, filter_s, filter_v, filter_o, filter_s_fileName, filter_v_fileName, filter_o_fileName,
#                lemmatize_s, lemmatize_v, lemmatize_o, outputSVODir,  chartPackage='Excel', dataTransformation='No transformation'):
#     filesToOpen = []
#     from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text, tokenize_stanza_text, lemmatize_stanza_word
#     from functools import lru_cache
#
#     @lru_cache(maxsize=10000)
#     def memoized_lemmatize(token):
#         return lemmatize_stanza_word(stanzaPipeLine(token))
#
#
#     startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
#                                                    'Started running the lemma/filter algorithm for Subject-Verb-Object (SVO) at',
#                                                    True, '', True)
#
#     df = pd.read_csv(svo_file_name, encoding='utf-8',on_bad_lines='skip')
#     df = df.replace(np.nan, '', regex=True)  # replace NaNs with empty strings
#     num_rows = df.shape[0]
#     if lemmatize_s or lemmatize_v or lemmatize_o:
#         head, tail = os.path.split(outputSVODir)
#         # create an SVO-lemma subdirectory of the main output directory
#         outputSVOLemmaDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO_lemma',
#                                                                     silent=True)
#         if outputSVOLemmaDir == '':
#             return
#
#         # create the lemma dict
#         if filter_s or filter_v or filter_o:
#             head, tail = os.path.split(outputSVODir)
#             outputSVOFilterDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO_filter',
#                                                                         silent=True)
#             if outputSVOFilterDir == '':
#                 return
#
#     # Creating filtered sets from WordNet verbose lists; use only the first column 'Term'
#     if not filter_s:
#         s_filtered_set = set()
#     else:
#         # convert all WordNet categories to lower case to make comparison easier
#         temp_pd = pd.read_csv(filter_s_fileName)['Term']
#         temp_pd = temp_pd.astype(str).str.lower()
#         s_filtered_set = set(temp_pd)
#         sorted(s_filtered_set)
#         # s_filtered_set = set(pd.read_csv(filter_s_fileName)['Term'])
#     if not filter_v:
#         v_filtered_set = set()
#     else:
#         # convert all WordNet categories to lower case to make comparison easier
#         temp_pd = pd.read_csv(filter_v_fileName)['Term']
#         temp_pd = temp_pd.astype(str).str.lower()
#         v_filtered_set = set(temp_pd)
#         sorted(v_filtered_set)
#         # v_filtered_set = set(pd.read_csv(filter_v_fileName)['Term'])
#     if not filter_o:
#         o_filtered_set = set()
#     else:
#         # convert all WordNet categories to lower case to make comparison easier
#         temp_pd = pd.read_csv(filter_o_fileName)['Term']
#         temp_pd = temp_pd.astype(str).str.lower()
#         o_filtered_set = set(temp_pd)
#         sorted(o_filtered_set)
#         # o_filtered_set = set(pd.read_csv(filter_o_fileName)['Term'])
#     # should add any PERSON or ORGANIZATION or LOCATION to the list, if these PERSON or ORGANIZATION or LOCATION values are not in the WordNet social-actor-list
#     # multi name S & O (e.g., Mao Zedong) in WordNet are listed with underscores (Mao_Zedong); we must do the same for multi-word names
#     # to recognize mwe expressions that are tagged as PERSON or ORGANIZATION or LOCATION '@#'
#     # Create DataFrames for lemmatized and filtered SVOs
#     lemmatized_svo = df.copy()
#     filtered_svo = df.copy()
#
#     df = df.fillna('')
#     df = df.replace(to_replace='None', value='', regex=False)
#
#     lemmatize_s_SV = lemmatize_s
#     for idx, row in df.iterrows():
#         print('Processing SVO record '+ str(idx) + '/' + str(len(df)))
#         if lemmatize_s_SV == True:
#             lemmatize_s = True
#         # the tag suffix @# will have been added in the Stanford_CoreNLP_util function process_json_SVO_enhanced_dependencies
#         #   to identify any mwe (multi-word expression) that is a NER PERSON, ORGANIZATION, or LOCATION
#         #   (e.g., Christopher Columbus, United States of America) which should always be treated as social actors independently of the WordNet list
#         if '@#' in row['Subject (S)']:
#             lemmatize_s = False
#             keep_record = True
#         if lemmatize_s:
#             if row['Subject (S)'].count(' ')==0:
#                 row['Subject (S)'] = memoized_lemmatize(row['Subject (S)'])
#             else:
#                 if filter_s:
#                     if not '@#' in row['Subject (S)']:
#                         # WordNet multi-word expressions are all _ separated (e.g., Christopher_Columbus)
#                         # convert string to list
#                         temp_list = row['Subject (S)'].split(' ')
#                         temp_lemma = ''
#                         for i in range(len(temp_list)):
#                             if temp_lemma=='':
#                                 temp_lemma = memoized_lemmatize(temp_list[i])
#                             else:
#                                 temp_lemma = temp_lemma + ' ' + memoized_lemmatize(temp_list[i])
#                         row['Subject (S)'] = temp_lemma.replace('  ', ' ') # temp_lemma will have 2 blanks when lemmatizing a blank token
#                         row['Subject (S)'] = temp_lemma.replace(' ', '_')
#         if lemmatize_v:
#             if row['Verb (V)'].count(' ')==0:
#                 row['Verb (V)'] = lemmatize_stanza_word(stanzaPipeLine(row['Verb (V)']))
#             else:
#                 if filter_v:
#                     # WordNet multi-word expressions are all _ separated (e.g., add_on)
#                     # convert string to list
#                     temp_list = row['Verb (V)'].split(' ')
#                     temp_lemma = ''
#                     for i in range(len(temp_list)):
#                         if temp_lemma=='':
#                             temp_lemma = memoized_lemmatize(temp_list[i])
#                         else:
#                             temp_lemma = temp_lemma + ' ' + memoized_lemmatize(temp_list[i])
#                     row['Verb (V)'] = temp_lemma.replace('  ', ' ') # temp_lemma will have 2 blanks when lemmatizing  a blank token
#                     row['Verb (V)'] = temp_lemma.replace(' ', '_')
#         if lemmatize_o:
#             if row['Object (O)'].count(' ')==0:
#                 row['Object (O)'] = memoized_lemmatize(row['Object (O)'])
#             else:
#                 if filter_o:
#                     # WordNet multi-word expressions are all _ separated (e.g., Christopher_Columbus)
#                     # convert string to list
#                     temp_list = row['Object (O)'].split(' ')
#                     temp_lemma = ''
#                     for i in range(len(temp_list)):
#                         if temp_lemma=='':
#                             temp_lemma = memoized_lemmatize(temp_list[i])
#                         else:
#                             temp_lemma = temp_lemma + ' ' + memoized_lemmatize(temp_list[i])
#                     row['Object (O)'] = temp_lemma.replace('  ', ' ') # temp_lemma will have 2 blanks when lemmatizing  a blank token
#                     row['Object (O)'] = temp_lemma.replace(' ', '_')
#
#         # # Assign lemmatized rows back to the lemmatized_svo DataFrame
#         # lemmatized_svo.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']] = row[
#         #     ['Subject (S)', 'Verb (V)', 'Object (O)']]
#
#         filter_byNER = set([row['Person']]).union(set([row['Organization']]).union(set([row['Location']])))
#         # add unstated passive subjects as Inferred_Subject_Passive
#         filter_byNER.add('Inferred_Subject_Passive')
#
#         keep_record = False
#
#
#
# # S-V-O filter ALL -----------------------------------------------------------------------------------
# # When multiple filters are applied (for S, V, and O) all conditions must be met
#         if row['Object (O)'] and row['Subject (S)'] and row['Verb (V)']:
#             if filter_s and filter_v and filter_o:
#                 if ((row['Subject (S)'].lower() in s_filtered_set) or \
#                     (str(row['Subject (S)']).lower() in filter_byNER)) and \
#                     (row['Verb (V)'].lower() in v_filtered_set) and \
#                     ((row['Object (O)'].lower() in o_filtered_set) and \
#                     (row['Object (O)'].lower() in filter_byNER)):
#                     keep_record=True
#                 # the tag @# is added to mwe that are classified in NER as PERSON, ORGANIZATION, or LOCATION
#                 #   which can be social actors that should not be lemmatized (e.g., 'Christopher Columbus discovered America')
#                 if '@#' in row['Subject (S)']:
#                     keep_record = True
#
#     # S-V filter ONLY NO O -----------------------------------------------------------------------------------
#     # When multiple filters are applied (for S, V, and O) all conditions must be met
#
#             # filter_byNER is typically capitalized, e.g., United States of America;
#             #   should not use row['Subject (S)'].lower()
#             if filter_s and filter_v and not filter_o:
#                 if row['Subject (S)'].lower() == 'sufficient':
#                     print()
#                 if ((row['Subject (S)'].lower() in s_filtered_set) or \
#                     (str(row['Subject (S)']) in filter_byNER)) and \
#                     (row['Verb (V)'].lower() in v_filtered_set):
#                     keep_record = True
#                 # the tag @# is added to mwe that are classified in NER as PERSON, ORGANIZATION, or LOCATION
#                 #   which can be social actors that should not be lemmatized (e.g., 'Christopher Columbus discovered America')
#                 if '@#' in row['Subject (S)']:
#                     keep_record = True
#
#     # S filter ONLY NO V & O -----------------------------------------------------------------------------------
#     # When multiple filters are applied (for S, V, and O) all conditions must be met
#     # filter_byNER is typically capitalized, e.g., United States of America;
#     #   should not use row['Subject (S)'].lower()
#
#             if filter_s and not filter_v and not filter_o:
#                 if ((row['Subject (S)'].lower() in s_filtered_set) or \
#                     (str(row['Subject (S)']) in filter_byNER)):
#                     keep_record = True
#                 # the tag @# is added to mwe that are classified in NER as PERSON, ORGANIZATION, or LOCATION
#                 #   which can be social actors that should not be lemmatized (e.g., 'Christopher Columbus discovered America')
#                 if '@#' in row['Subject (S)']:
#                     keep_record = True
#
#     # V filter ONLY NO S & O -----------------------------------------------------------------------------------
#     # When multiple filters are applied (for S, V, and O) all conditions must be met
#
#             if filter_v and not filter_s and not filter_o:
#                 if (row['Verb (V)'].lower() in v_filtered_set):
#                     keep_record = True
#
#
#     # O filter ONLY NO S & V -------------------------------------------------------------------------------
#     # When multiple filters are applied (for S, V, and O) all conditions must be met
#     # filter_byNER is typically capitalized, e.g., United States of America;
#     #   should not use row['Subject (S)'].lower()
#             if filter_o and not filter_s and not filter_v:
#                 if ((row['Object (O)'].lower() in o_filtered_set) or \
#                     (str(row['Object (O)']) in filter_byNER)):
#                     keep_record = True
#         else:
#             print(f"Skipping incomplete SVO at row {idx}: S={row['Subject (S)']}, V={row['Verb (V)']}, O={row['Object (O)']}")
#             continue
#
# # ----------------------------------------------------------------------------------------------------------
#         # rewrite the original df record if @# was added as a tag to recognize the record as a
#         #   PERSON, ORGANIZATION, or LOCATION
#         #   which can be social actors that should not be lemmatized
#         #   this would keep such mwe as 'United States of America' and preserve such sentences as 'United States of America fought Germany in WWII'
#
#         if '@#' in row['Subject (S)']:
#             row['Subject (S)'] = row['Subject (S)'].replace('@#', '')
#             # update the original df dataframe with @# tags with the new cleaned values
#             df.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']] = row[
#                 ['Subject (S)', 'Verb (V)', 'Object (O)']]
#
#
#
#         if keep_record: # export the filtered record
#             filtered_svo.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']] = row[
#                 ['Subject (S)', 'Verb (V)', 'Object (O)']]
#             print(filtered_svo.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']])
#             keep_record = False
#         else:
#             # Drop rows from filtered_svo DataFrame that do not meet the filter condition
#             filtered_svo.drop(idx, inplace=True)
#
#         # Assign lemmatized rows back to the lemmatized_svo DataFrame
#         lemmatized_svo.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']] = row[
#             ['Subject (S)', 'Verb (V)', 'Object (O)']]
#
#         # reset the row, replacing the _ back to " "
#         if not "inferred_subject_passive" in row['Subject (S)']:
#             df.loc[idx, ['Subject (S)']] = row['Subject (S)'].replace('_', ' ')
#         df.loc[idx, ['Verb (V)']] = row['Verb (V)'].replace('_', ' ')
#         df.loc[idx, ['Object (O)']] = row['Object (O)'].replace('_', ' ')
#     # save the edited df to the svo file
#     df.to_csv(svo_file_name, encoding='utf-8', index=False)
#
#     # print(lemmatized_svo,filtered_svo)
#     # Continue with your code, now working with filtered and lemmatized DataFrames
#
#     # filtering for WordNet social actors/actions requires lemmatizing
#     nRecords_lemma = 0
#     nRecords_filter = 0
#     if lemmatize_s or lemmatize_v or lemmatize_o:
#         head, tail = os.path.split(svo_file_name)
#         tail = tail.replace('NLP_SVO_', 'NLP_SVO_lemma_')
#         svo_lemma_file_name = os.path.join(outputSVOLemmaDir, tail)
#         filesToOpen.append(svo_lemma_file_name)
#         # save lemmatized file
#         lemmatized_svo.to_csv(svo_lemma_file_name, encoding='utf-8', index=False)
#         nRecords_lemma, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_lemma_file_name)
#
#         # filtering for WordNet social actors/actions requires lemmatizing
#         if filter_s or filter_v or filter_o:
#             if filter_s and filter_v and filter_o:
#                 label='SVO_'
#             elif filter_s and filter_v:
#                 label='SV_'
#             elif filter_s and filter_o:
#                 label='SO_'
#             elif filter_s:
#                 label = 'S_'
#             elif filter_v and filter_o:
#                 label='VO_'
#             elif filter_v:
#                 label='V_'
#             elif filter_o:
#                 label='O_'
#
#             outputDir, tail = os.path.split(svo_lemma_file_name)
#             tail = tail.replace('NLP_SVO_lemma_', 'NLP_SVO_filter_'+ label)
#             svo_filter_file_name = os.path.join(outputSVOFilterDir, tail)
#             # save filtered file
#             filesToOpen.append(svo_filter_file_name)
#
#             # save filtered file
#             filtered_svo.to_csv(svo_filter_file_name, encoding='utf-8', index=False)
#
#             # if filter_s or filter_v or filter_o:
#             # pd.DataFrame.from_dict(filtered_svo, orient='index').to_csv(svo_filter_file_name, encoding='utf-8', index=False)
#
#             nRecords_filter, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_filter_file_name)
#             filtered_records = num_rows - nRecords_filter
#             IO_user_interface_util.timed_alert(window,6000,'Filtered records', 'The filter algorithms have filtered out ' + str(filtered_records) + \
#                 ' records.\n\nNumber of original SVO records: ' + str(num_rows) + '\nNumber of filtered SVO records: ' + str(nRecords_filter))
#
#             # save filtered records info
#             svo_filter_records = []
#             svo_filter_records_file_name = os.path.join(outputSVOFilterDir, tail[:-4]+'_records.csv')
#             filesToOpen.append(svo_filter_records_file_name)
#             headers = ['Number of original unfiltered SVO records', 'Number of filtered SVO records', 'Difference']
#             row = [str(num_rows), str(nRecords_filter), str(num_rows - nRecords_filter)]
#             svo_filter_records.append(headers)
#             svo_filter_records.append(row)
#             IO_csv_util.list_to_csv(1, svo_filter_records, svo_filter_records_file_name)
#     else:
#         svo_lemma_file_name= ''
#
#     IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running the lemma/filter algorithm for Subject-Verb-Object (SVO) at', True, '', True,
#                                        startTime, True)
#
#     if nRecords_lemma > 1 or nRecords_filter >1:
#         openFiles = False # way too many files to open; but this can be changed at any time
#         if lemmatize_s or lemmatize_v or lemmatize_o:
#             filesToOpen = visualize_SVOs(svo_lemma_file_name, outputSVOLemmaDir, chartPackage, dataTransformation,filesToOpen, openFiles)
#         if filter_s or filter_v or filter_o:
#             filesToOpen = visualize_SVOs(svo_filter_file_name, outputSVOFilterDir, chartPackage, dataTransformation,filesToOpen, openFiles)
#
#     # rewrite the original df file in case @# were added as a tag to recognize the record as a PERSON, ORGANIZATION, or LOCATION
#     df.to_csv(svo_file_name, encoding='utf-8', index=False)
#
#     return filesToOpen

def lemmatize_filter_svo(window, svo_file_name, filter_s, filter_v, filter_o, filter_s_fileName, filter_v_fileName, filter_o_fileName,
               lemmatize_s, lemmatize_v, lemmatize_o, outputSVODir,  chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []
    from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text, tokenize_stanza_text, lemmatize_stanza_word
    from functools import lru_cache

    @lru_cache(maxsize=10000)
    def memoized_lemmatize(token):
        return lemmatize_stanza_word(stanzaPipeLine(token))


    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running the lemma/filter algorithm for Subject-Verb-Object (SVO) at',
                                                   True, '', True)

    df = pd.read_csv(svo_file_name, encoding='utf-8',on_bad_lines='skip')
    df = df.replace(np.nan, '', regex=True)  # replace NaNs with empty strings
    num_rows = df.shape[0]
    if lemmatize_s or lemmatize_v or lemmatize_o:
        head, tail = os.path.split(outputSVODir)
        # create an SVO-lemma subdirectory of the main output directory
        outputSVOLemmaDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO_lemma',
                                                                    silent=True)
        if outputSVOLemmaDir == '':
            return

        # create the lemma dict
        if filter_s or filter_v or filter_o:
            head, tail = os.path.split(outputSVODir)
            outputSVOFilterDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO_filter',
                                                                        silent=True)
            if outputSVOFilterDir == '':
                return

    # Creating filtered sets from WordNet verbose lists; use only the first column 'Term'
    if not filter_s:
        s_filtered_set = set()
    else:
        # convert all WordNet categories to lower case to make comparison easier
        temp_pd = pd.read_csv(filter_s_fileName)['Term']
        temp_pd = temp_pd.astype(str).str.lower()
        s_filtered_set = set(temp_pd)
        sorted(s_filtered_set)
        # s_filtered_set = set(pd.read_csv(filter_s_fileName)['Term'])
    if not filter_v:
        v_filtered_set = set()
    else:
        # convert all WordNet categories to lower case to make comparison easier
        temp_pd = pd.read_csv(filter_v_fileName)['Term']
        temp_pd = temp_pd.astype(str).str.lower()
        v_filtered_set = set(temp_pd)
        sorted(v_filtered_set)
        # v_filtered_set = set(pd.read_csv(filter_v_fileName)['Term'])
    if not filter_o:
        o_filtered_set = set()
    else:
        # convert all WordNet categories to lower case to make comparison easier
        temp_pd = pd.read_csv(filter_o_fileName)['Term']
        temp_pd = temp_pd.astype(str).str.lower()
        o_filtered_set = set(temp_pd)
        sorted(o_filtered_set)
        # o_filtered_set = set(pd.read_csv(filter_o_fileName)['Term'])
    # should add any PERSON or ORGANIZATION or LOCATION to the list, if these PERSON or ORGANIZATION or LOCATION values are not in the WordNet social-actor-list
    # multi name S & O (e.g., Mao Zedong) in WordNet are listed with underscores (Mao_Zedong); we must do the same for multi-word names
    # to recognize mwe expressions that are tagged as PERSON or ORGANIZATION or LOCATION '@#'
    # Create DataFrames for lemmatized and filtered SVOs
    lemmatized_svo = df.copy()
    filtered_svo = df.copy()

    df = df.fillna('')
    df = df.replace(to_replace='None', value='', regex=False)

    lemmatize_s_SV = lemmatize_s

    #_1 is Subject (S), _2 is Verb (V) and _3 is Object (O)
#     for row in df.itertuples():
#         idx = row.Index
#         print("THIS IS ROW        ", row)
#         print("THIS IS ROW FIELDS      ", row._fields)
#         print('Processing SVO record ' + str(idx) + '/' + str(len(df)))
#         if lemmatize_s_SV == True:
#             lemmatize_s = True
#         # the tag suffix @# will have been added in the Stanford_CoreNLP_util function process_json_SVO_enhanced_dependencies
#         #   to identify any mwe (multi-word expression) that is a NER PERSON, ORGANIZATION, or LOCATION
#         #   (e.g., Christopher Columbus, United States of America) which should always be treated as social actors independently of the WordNet list
#         if '@#' in row._1:
#             lemmatize_s = False
#             keep_record = True
#         if lemmatize_s:
#             if row.count(' ') == 0:
#                 row._1= memoized_lemmatize(row._1)
#             else:
#                 if filter_s:
#                     if not '@#' in row._1:
#                         # WordNet multi-word expressions are all _ separated (e.g., Christopher_Columbus)
#                         # convert string to list
#                         temp_list = row._1.split(' ')
#                         temp_lemma = ''
#                         for i in range(len(temp_list)):
#                             if temp_lemma == '':
#                                 temp_lemma = memoized_lemmatize(temp_list[i])
#                             else:
#                                 temp_lemma = temp_lemma + ' ' + memoized_lemmatize(temp_list[i])
#                         row._1 = temp_lemma.replace('  ',
#                                                                 ' ')  # temp_lemma will have 2 blanks when lemmatizing a blank token
#                         row._1 = temp_lemma.replace(' ', '_')
#         if lemmatize_v:
#             if row._2.count(' ') == 0:
#                 rowVerb__V_ = lemmatize_stanza_word(stanzaPipeLine(row._2))
#             else:
#                 if filter_v:
#                     # WordNet multi-word expressions are all _ separated (e.g., add_on)
#                     # convert string to list
#                     temp_list = row._2.split(' ')
#                     temp_lemma = ''
#                     for i in range(len(temp_list)):
#                         if temp_lemma == '':
#                             temp_lemma = memoized_lemmatize(temp_list[i])
#                         else:
#                             temp_lemma = temp_lemma + ' ' + memoized_lemmatize(temp_list[i])
#                     row._2 = temp_lemma.replace('  ',
#                                                          ' ')  # temp_lemma will have 2 blanks when lemmatizing  a blank token
#                     row._2 = temp_lemma.replace(' ', '_')
#         if lemmatize_o:
#             if row._3.count(' ') == 0:
#                 row._3 = memoized_lemmatize(row._3)
#             else:
#                 if filter_o:
#                     # WordNet multi-word expressions are all _ separated (e.g., Christopher_Columbus)
#                     # convert string to list
#                     temp_list = row._3.split(' ')
#                     temp_lemma = ''
#                     for i in range(len(temp_list)):
#                         if temp_lemma == '':
#                             temp_lemma = memoized_lemmatize(temp_list[i])
#                         else:
#                             temp_lemma = temp_lemma + ' ' + memoized_lemmatize(temp_list[i])
#                     row._3= temp_lemma.replace('  ',
#                                                            ' ')  # temp_lemma will have 2 blanks when lemmatizing  a blank token
#                     row._3= temp_lemma.replace(' ', '_')
#
#         # # Assign lemmatized rows back to the lemmatized_svo DataFrame
#         # lemmatized_svo.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']] = row[
#         #     ['Subject (S)', 'Verb (V)', 'Object (O)']]
#
#         filter_byNER = {row.Person, row.Organization, row.Location}
#         # add unstated passive subjects as Inferred_Subject_Passive
#         filter_byNER.add('Inferred_Subject_Passive')
#
#         keep_record = False
#
#         # S-V-O filter ALL -----------------------------------------------------------------------------------
#         # When multiple filters are applied (for S, V, and O) all conditions must be met
#         if filter_s and filter_v and filter_o:
#             if row._3 and row._1 and row._2:
#                 if ((row._1.lower() in s_filtered_set) or \
#                     (str(row._1).lower() in filter_byNER)) and \
#                         (row._2.lower() in v_filtered_set) and \
#                         ((row._3.lower() in o_filtered_set) and \
#                          (row._3.lower() in filter_byNER)):
#                     keep_record = True
#                 # the tag @# is added to mwe that are classified in NER as PERSON, ORGANIZATION, or LOCATION
#                 #   which can be social actors that should not be lemmatized (e.g., 'Christopher Columbus discovered America')
#                 if '@#' in row._1:
#                     keep_record = True
#             else:
#                 print(
#                     f"Skipping incomplete SVO at row {idx}: S={row._1}, V={row._2}, O={row._3}")
#                 filtered_svo.drop(index=idx, inplace=True)
#                 continue
#
#         # S-V filter ONLY NO O -----------------------------------------------------------------------------------
#         # When multiple filters are applied (for S, V, and O) all conditions must be met
#
#         # filter_byNER is typically capitalized, e.g., United States of America;
#         #   should not use row._1.lower()
#         elif filter_s and filter_v and not filter_o:
#             if row._2 and row._1:
#                 if ((row._1.lower() in s_filtered_set) or \
#                     (str(row._1) in filter_byNER)) and \
#                         (row._2.lower() in v_filtered_set):
#                     keep_record = True
#                 # the tag @# is added to mwe that are classified in NER as PERSON, ORGANIZATION, or LOCATION
#                 #   which can be social actors that should not be lemmatized (e.g., 'Christopher Columbus discovered America')
#                 if '@#' in row._1:
#                     keep_record = True
#             else:
#                 print(
#                     f"Skipping incomplete SVO at row {idx}: S={row._1}, V={row._2}, O={row._3}")
#                 filtered_svo.drop(index=idx, inplace=True)
#                 continue
#
#         # S filter ONLY NO V & O -----------------------------------------------------------------------------------
#         # When multiple filters are applied (for S, V, and O) all conditions must be met
#         # filter_byNER is typically capitalized, e.g., United States of America;
#         #   should not use row._1.lower()
#
#         elif filter_s and not filter_v and not filter_o:
#             if row._1:
#                 if ((row._1.lower() in s_filtered_set) or \
#                         (str(row._1) in filter_byNER)):
#                     keep_record = True
#                 # the tag @# is added to mwe that are classified in NER as PERSON, ORGANIZATION, or LOCATION
#                 #   which can be social actors that should not be lemmatized (e.g., 'Christopher Columbus discovered America')
#                 if '@#' in row._1:
#                     keep_record = True
#             else:
#                 print(
#                     f"Skipping incomplete SVO at row {idx}: S={row._1}, V={row._2}, O={row._3}")
#                 filtered_svo.drop(index=idx, inplace=True)
#                 continue
#
#         # V filter ONLY NO S & O -----------------------------------------------------------------------------------
#         # When multiple filters are applied (for S, V, and O) all conditions must be met
#
#         elif filter_v and not filter_s and not filter_o:
#             if (row._2):
#                 if (row._2.lower() in v_filtered_set):
#                     keep_record = True
#             else:
#                 print(
#                     f"Skipping incomplete SVO at row {idx}: S={row._1}, V={row._2}, O={row._3}")
#                 filtered_svo.drop(index=idx, inplace=True)
#                 continue
#
#
#         # O filter ONLY NO S & V -------------------------------------------------------------------------------
#         # When multiple filters are applied (for S, V, and O) all conditions must be met
#         # filter_byNER is typically capitalized, e.g., United States of America;
#         #   should not use row._1.lower()
#         elif filter_o and not filter_s and not filter_v:
#             if row._3:
#                 if ((row._3.lower() in o_filtered_set) or \
#                         (str(row._3) in filter_byNER)):
#                     keep_record = True
#             else:
#                 print(
#                     f"Skipping incomplete SVO at row {idx}: S={row._1}, V={row._2}, O={row._3}")
#                 filtered_svo.drop(index=idx, inplace=True)
#                 continue
#
#         # ----------------------------------------------------------------------------------------------------------
#         # rewrite the original df record if @# was added as a tag to recognize the record as a
#         #   PERSON, ORGANIZATION, or LOCATION
#         #   which can be social actors that should not be lemmatized
#         #   this would keep such mwe as 'United States of America' and preserve such sentences as 'United States of America fought Germany in WWII'
#         subject = row[0]
#         verb = row[1]
#         obj = row[2]
#
#         # Clean subject if it contains '@#'
#         if '@#' in subject:
#             subject = subject.replace('@#', '')
#             # Update the original df at idx for Subject (S)
#             df.loc[idx, 'Subject (S)'] = subject
#
#         # Similarly update verb and object in df (replacing '_' with ' ')
#         df.loc[idx, 'Verb (V)'] = verb.replace('_', ' ')
#         df.loc[idx, 'Object (O)'] = obj.replace('_', ' ')
#
#         # Example updating filtered_svo DataFrame conditionally
#         if keep_record:
#             filtered_svo.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']] = [subject, verb, obj]
#             keep_record = False
#         else:
#             filtered_svo.drop(idx, inplace=True)
#
#         # Assign lemmatized rows back
#         lemmatized_svo.loc[idx, ['Subject (S)', 'Verb (V)', 'Object (O)']] = [subject, verb, obj]
#
#         # If you want to reset underscores in Subject only if condition met
#         if "inferred_subject_passive" not in subject:
#             df.loc[idx, 'Subject (S)'] = subject.replace('_', ' ')
#         # save the edited df to the svo file
#     df.to_csv(svo_file_name, encoding='utf-8', index=False)


    def process_svo_row(row, lemmatize_s, lemmatize_v, lemmatize_o, lemmatize_s_SV,
                        filter_s, filter_v, filter_o, s_filtered_set, v_filtered_set, o_filtered_set):
        lemmatize_s_local = lemmatize_s
        if lemmatize_s_SV:
            lemmatize_s_local = True
        # the tag suffix @# is added upstream to flag a mwe that is a NER PERSON, ORGANIZATION, or
        # LOCATION (e.g., Christopher Columbus, United States of America); those are social actors
        # that must NOT be lemmatized regardless of the WordNet list
        if '@#' in str(row['Subject (S)']):
            lemmatize_s_local = False

        if lemmatize_s_local and row['Subject (S)'].count(' ') == 0:
            row['Subject (S)'] = memoized_lemmatize(row['Subject (S)'])
        elif lemmatize_s_local and filter_s and '@#' not in row['Subject (S)']:
            words = row['Subject (S)'].split(' ')
            row['Subject (S)'] = '_'.join([memoized_lemmatize(w) for w in words])

        if lemmatize_v and row['Verb (V)'].count(' ') == 0:
            row['Verb (V)'] = memoized_lemmatize(row['Verb (V)'])
        elif lemmatize_v and filter_v:
            words = row['Verb (V)'].split(' ')
            row['Verb (V)'] = '_'.join([memoized_lemmatize(w) for w in words])

        if lemmatize_o and row['Object (O)'].count(' ') == 0:
            row['Object (O)'] = memoized_lemmatize(row['Object (O)'])
        elif lemmatize_o and filter_o:
            words = row['Object (O)'].split(' ')
            row['Object (O)'] = '_'.join([memoized_lemmatize(w) for w in words])

        return row

    df = df.apply(lambda row: process_svo_row(row, lemmatize_s, lemmatize_v, lemmatize_o,
                                              lemmatize_s_SV, filter_s, filter_v, filter_o,
                                              s_filtered_set, v_filtered_set, o_filtered_set), axis=1)

    # df now holds the LEMMATIZED SVO. Build the two derived outputs FROM it (previously lemmatized_svo /
    # filtered_svo were copied BEFORE processing and never updated -> the "filtered" file was an unfiltered
    # copy, so 0 records were ever filtered).
    lemmatized_svo = df.copy()
    # Filtered SVO: keep a row only when EACH ENABLED filter's field is in its actor/action list (AND across
    # the enabled filters; a disabled filter imposes no constraint). A field tagged '@#' is a NER
    # PERSON/ORGANIZATION/LOCATION -- a genuine social actor -- and is kept regardless of the list.
    # Object is typically NOT filtered (default), so non-actor objects survive (e.g. 'terrorists blow up
    # railroad' -- railroad is not a social actor, but the row is kept).
    if filter_s or filter_v or filter_o:
        def _row_passes(row):
            if filter_s:
                s = str(row['Subject (S)'])
                if '@#' not in s and s.lower() not in s_filtered_set:
                    return False
            if filter_v and str(row['Verb (V)']).lower() not in v_filtered_set:
                return False
            if filter_o:
                o = str(row['Object (O)'])
                if '@#' not in o and o.lower() not in o_filtered_set:
                    return False
            return True
        filtered_svo = df[df.apply(_row_passes, axis=1)].copy()
    else:
        filtered_svo = df.copy()

    # '@#' is an internal-only flag prepended upstream to Subjects that are NER PERSON/ORGANIZATION/
    # LOCATION; it was needed by the lemmatize/filter logic above but must NOT leak into any output
    # file or chart (it was showing up as '@#He', '@#United States', etc.). Strip it from all three
    # dataframes now that filtering is done.
    for _svo_df in (df, lemmatized_svo, filtered_svo):
        _svo_df['Subject (S)'] = _svo_df['Subject (S)'].astype(str).str.replace('@#', '', regex=False)

    # save the edited df to the svo file
    df.to_csv(svo_file_name, encoding='utf-8', index=False)

    # print(lemmatized_svo,filtered_svo)
    # Continue with your code, now working with filtered and lemmatized DataFrames

    # filtering for WordNet social actors/actions requires lemmatizing
    nRecords_lemma = 0
    nRecords_filter = 0
    if lemmatize_s or lemmatize_v or lemmatize_o:
        head, tail = os.path.split(svo_file_name)
        tail = tail.replace('NLP_SVO_', 'NLP_SVO_lemma_')
        svo_lemma_file_name = os.path.join(outputSVOLemmaDir, tail)
        filesToOpen.append(svo_lemma_file_name)
        # save lemmatized file
        lemmatized_svo.to_csv(svo_lemma_file_name, encoding='utf-8', index=False)
        nRecords_lemma, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_lemma_file_name)

        # filtering for WordNet social actors/actions requires lemmatizing
        if filter_s or filter_v or filter_o:
            if filter_s and filter_v and filter_o:
                label='SVO_'
            elif filter_s and filter_v:
                label='SV_'
            elif filter_s and filter_o:
                label='SO_'
            elif filter_s:
                label = 'S_'
            elif filter_v and filter_o:
                label='VO_'
            elif filter_v:
                label='V_'
            elif filter_o:
                label='O_'

            outputDir, tail = os.path.split(svo_lemma_file_name)
            tail = tail.replace('NLP_SVO_lemma_', 'NLP_SVO_filter_'+ label)
            svo_filter_file_name = os.path.join(outputSVOFilterDir, tail)
            # save filtered file
            filesToOpen.append(svo_filter_file_name)

            # save filtered file
            filtered_svo.to_csv(svo_filter_file_name, encoding='utf-8', index=False)

            # if filter_s or filter_v or filter_o:
            # pd.DataFrame.from_dict(filtered_svo, orient='index').to_csv(svo_filter_file_name, encoding='utf-8', index=False)

            nRecords_filter, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_filter_file_name)
            filtered_records = num_rows - nRecords_filter
            IO_user_interface_util.timed_alert(window,6000,'Filtered records', 'The filter algorithms have filtered out ' + str(filtered_records) + \
                ' records.\n\nNumber of original SVO records: ' + str(num_rows) + '\nNumber of filtered SVO records: ' + str(nRecords_filter))

            # save filtered records info
            svo_filter_records = []
            svo_filter_records_file_name = os.path.join(outputSVOFilterDir, tail[:-4]+'_records.csv')
            filesToOpen.append(svo_filter_records_file_name)
            headers = ['Number of original unfiltered SVO records', 'Number of filtered SVO records', 'Difference']
            row = [str(num_rows), str(nRecords_filter), str(num_rows - nRecords_filter)]
            svo_filter_records.append(headers)
            svo_filter_records.append(row)
            IO_csv_util.list_to_csv(1, svo_filter_records, svo_filter_records_file_name)
    else:
        svo_lemma_file_name= ''

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running the lemma/filter algorithm for Subject-Verb-Object (SVO) at', True, '', True,
                                       startTime, True)

    if nRecords_lemma > 1 or nRecords_filter >1:
        openFiles = False # way too many files to open; but this can be changed at any time
        if lemmatize_s or lemmatize_v or lemmatize_o:
            filesToOpen = visualize_SVOs(svo_lemma_file_name, outputSVOLemmaDir, chartPackage, dataTransformation,filesToOpen, openFiles)
        if filter_s or filter_v or filter_o:
            filesToOpen = visualize_SVOs(svo_filter_file_name, outputSVOFilterDir, chartPackage, dataTransformation,filesToOpen, openFiles)

    # rewrite the original df file in case @# were added as a tag to recognize the record as a PERSON, ORGANIZATION, or LOCATION
    df.to_csv(svo_file_name, encoding='utf-8', index=False)

    return filesToOpen


def lemmatize_filter_svo_old(window,svo_file_name, filter_s, filter_v, filter_o, filter_s_fileName, filter_v_fileName, filter_o_fileName,
               lemmatize_s, lemmatize_v, lemmatize_o, outputSVODir,  chartPackage='Excel', dataTransformation='No transformation'):
    """
    Filters a svo csv file based on the dictionaries given, and replaces the original output csv file
    :param svo_file_name: the name of the svo csv file
    :param filter_s_fileName: the subject dict file path
    :param filter_v_fileName: the verb dict file path
    :param filter_o_fileName: the object dict file path
    """

    filesToOpen = []
    s_filtered_set = {}
    v_filtered_set = {}
    o_filtered_set = {}

    from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text, tokenize_stanza_text, lemmatize_stanza_word

    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running the lemma/filter algorithm for Subject-Verb-Object (SVO) at',
                                                   True, '', True)

    df = pd.read_csv(svo_file_name, encoding='utf-8',on_bad_lines='skip')
    num_rows = df.shape[0]

    unfiltered_svo = df.to_dict('index')
    # values updated below when lemmatizing or filtering
    lemmatized_svo = {}
    filtered_svo = {}
    # lemmatized_filtered_svo = {}

    if lemmatize_s or lemmatize_v or lemmatize_o:
        head, tail = os.path.split(outputSVODir)
        # create an SVO-lemma subdirectory of the main output directory
        outputSVOLemmaDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO_lemma',
                                                                    silent=True)
        if outputSVOLemmaDir == '':
            return

        # create the lemma dict
        lemmatized_svo = dict(unfiltered_svo)
        if filter_s or filter_v or filter_o:
            # create the filtered dict
            # lemmatized_filtered_svo = dict(unfiltered_svo)
            filtered_svo = dict(unfiltered_svo)
            # place the filtered SVO files in a subdir under the main output directory,
            #   rather than inside the SVO subdir
            head, tail = os.path.split(outputSVODir)
            # create an SVO-filtered subdirectory of the main output directory
            outputSVOFilterDir = IO_files_util.make_output_subdirectory('', '', head, label='SVO_filter',
                                                                        silent=True)
            if outputSVOFilterDir == '':
                return

            # Generating filter dicts from filter files
            if filter_s:
                s_filtered_set = open(filter_s_fileName, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
                s_filtered_set = set(s_filtered_set)
            if filter_v:
                v_filtered_set = open(filter_v_fileName, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
                v_filtered_set = set(v_filtered_set)
            if filter_o:
                o_filtered_set = open(filter_o_fileName, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
                o_filtered_set = set(o_filtered_set)

# update LEMMATIZED dict and FILTERED dict
    for i in range(num_rows): # num_rows in the unfiltered SVO
        deleted = False
        if not pd.isna(unfiltered_svo[i]['Subject (S)']):
            if lemmatize_s:
                lemmatized_svo[i]['Subject (S)'] = lemmatize_stanza_word(stanzaPipeLine(unfiltered_svo[i]['Subject (S)']))
                # lemmatized_svo.add(i,lemmatize_stanza_word(stanzaPipeLine(unfiltered_svo[i]['Subject (S)'])))
                if (filter_s and filter_s_fileName!='') and (not unfiltered_svo[i]['Subject (S)'] in s_filtered_set):
                    del filtered_svo[i]
                    # del lemmatized_filtered_svo[i]
                    deleted = True
                else:
                    # if lemmatize_s and lemmatized_filtered_svo != {}:
                    # if lemmatize_s and lemmatized_filtered_svo != {}:
                    #     lemmatized_filtered_svo[i]['Subject (S)'] = lemmatize_stanza_word(
                    #         stanzaPipeLine(filtered_svo[i]['Subject (S)']))
                    if lemmatize_s and filtered_svo != {}:
                        filtered_svo[i]['Subject (S)'] = lemmatize_stanza_word(
                            stanzaPipeLine(filtered_svo[i]['Subject (S)']))

        if not pd.isna(unfiltered_svo[i]['Verb (V)']):
            if lemmatize_v:
                lemmatized_svo[i]['Verb (V)'] = lemmatize_stanza_word(stanzaPipeLine(unfiltered_svo[i]['Verb (V)']))
                if (filter_v and filter_v_fileName!='') and (not unfiltered_svo[i]['Verb (V)'] in v_filtered_set):
                    if not deleted:
                        del filtered_svo[i]
                        # del lemmatized_filtered_svo[i]
                        deleted = True
                else:
                    # if not deleted and lemmatize_v and lemmatized_filtered_svo!={}:
                    #     lemmatized_filtered_svo[i]['Verb (V)'] = lemmatize_stanza_word(stanzaPipeLine(filtered_svo[i]['Verb (V)']))
                    if not deleted and lemmatize_v and filtered_svo!={}:
                        filtered_svo[i]['Verb (V)'] = lemmatize_stanza_word(stanzaPipeLine(filtered_svo[i]['Verb (V)']))

        if not pd.isna(unfiltered_svo[i]['Object (O)']):
            if lemmatize_o:
                lemmatized_svo[i]['Object (O)'] = lemmatize_stanza_word(stanzaPipeLine(unfiltered_svo[i]['Object (O)']))
                if (filter_o and filter_o_fileName!='') and (not unfiltered_svo[i]['Object (O)'] in o_filtered_set):
                    if not deleted:
                        del filtered_svo[i]
                        # del lemmatized_filtered_svo[i]
                else:
                    # if not deleted and lemmatize_o and lemmatized_filtered_svo!={}:
                    #     lemmatized_filtered_svo[i]['Object (O)'] = lemmatize_stanza_word(stanzaPipeLine(filtered_svo[i]['Object (O)']))
                    if not deleted and lemmatize_o and filtered_svo!={}:
                        filtered_svo[i]['Object (O)'] = lemmatize_stanza_word(stanzaPipeLine(filtered_svo[i]['Object (O)']))
    # print(filter_s,filter_v,filtered_svo)

    # filtering for WordNet social actors/actions requires lemmatizing
    nRecords_lemma = 0
    nRecords_filter = 0
    if lemmatize_s or lemmatize_v or lemmatize_o:
        head, tail = os.path.split(svo_file_name)
        tail = tail.replace('NLP_SVO_', 'NLP_SVO_lemma_')
        svo_lemma_file_name = os.path.join(outputSVODir, tail)
        filesToOpen.append(svo_lemma_file_name)
        # save lemmatized file
        pd.DataFrame.from_dict(lemmatized_svo, orient='index').to_csv(svo_lemma_file_name, encoding='utf-8', index=False)
        nRecords_lemma, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_lemma_file_name)

        # filtering for WordNet social actors/actions requires lemmatizing
        if filter_s or filter_v or filter_o:
            if filter_s and filter_v and filter_o:
                label='SVO_'
            elif filter_s and filter_v:
                label='SV_'
            elif filter_s and filter_o:
                label='SO_'
            elif filter_s:
                label = 'S_'
            elif filter_v and filter_o:
                label='VO_'
            elif filter_v:
                label='V_'
            elif filter_o:
                label='O_'

            # # create a subdirectory of the output SVO directory for filtered SVOs
            # # filtered SVOs are stored in the WordNet directory
            # outputWNDir = IO_files_util.make_output_subdirectory('', '', outputDir,
            #                                                      label='WordNet',
            #                                                      silent=True)
            outputDir, tail = os.path.split(svo_lemma_file_name)
            tail = tail.replace('NLP_SVO_lemma_', 'NLP_SVO_filter_'+ label)
            # svo_filtered_file_name = os.path.join(outputWNDir, tail)
            svo_filter_file_name = os.path.join(outputSVODir, tail)
            # save filtered file
            filesToOpen.append(svo_filter_file_name)
            # pd.DataFrame.from_dict(lemmatized_filtered_svo, orient='index').to_csv(svo_filter_file_name, encoding='utf-8',
            #                                                               index=False)
            # save filtered file
            pd.DataFrame.from_dict(filtered_svo, orient='index').to_csv(svo_filter_file_name, encoding='utf-8',
                                                                          index=False)

            # if filter_s or filter_v or filter_o:
            # pd.DataFrame.from_dict(filtered_svo, orient='index').to_csv(svo_filter_file_name, encoding='utf-8', index=False)

            nRecords_filter, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_filter_file_name)
            filtered_records = num_rows - nRecords_filter
            IO_user_interface_util.timed_alert(window,6000,'Filtered records', 'The filter algorithms have filtered out ' + str(filtered_records) + \
                ' records.\n\nNumber of original SVO records: ' + str(num_rows) + '\nNumber of filtered SVO records: ' + str(nRecords_filter))
        # else:
        #     svo_filter_file_name=''
        #     nRecords = 0

    else:
        svo_lemma_file_name= ''
        svo_filtered_file_name = ''
        # nRecords = 0

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running the lemma/filter algorithm for Subject-Verb-Object (SVO) at', True, '', True,
                                       startTime, True)

    if nRecords_lemma > 1 or nRecords_filter >1:
        openFiles = False # way too many files to open; but this can be changed at any time
        if lemmatize_s or lemmatize_v or lemmatize_o:
            filesToOpen = visualize_SVOs(svo_lemma_file_name, outputSVOLemmaDir, chartPackage, dataTransformation, filesToOpen, openFiles)
        if filter_s or filter_v or filter_o:
            filesToOpen = visualize_SVOs(svo_filter_file_name, outputSVOFilterDir, chartPackage, dataTransformation, filesToOpen, openFiles)

    return filesToOpen

def normalize_date_svo(inputFilename, outputDir,  chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []


    # read the file to make sure there are dates to visualize
    data = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    # col='Date expression'
    if data['Date expression'].empty or data['Date expression'].isna().all():
        print("There are no NER normalized dates for the extracted SVOs")
        return

    nEmtyCells=str(int(data['Date expression'].isna().sum()))
    outputNormalizedDateDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                                     label='normalized-date_CoreNLP',
                                                                     silent=True)

    # Date expressions are in the form yesterday, tomorrow morning, the day before Christmas
    outputFiles = charts_util.plot(inputFilename, outputNormalizedDateDir, columns=['Date expression'], title='Frequency Distribution of Date Expressions', x_label='Date expression (includes '+nEmtyCells+' SVOs with no date)', file_label='date-express', plot_list=['Frequency'], title_label='Date Expressions')
    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    # normalized dates are in the form PAST_REF, NEXT_IMMEDIATE P1D, ...
    outputFiles = charts_util.plot(inputFilename, outputNormalizedDateDir, columns=['Normalized date'], title='Frequency Distribution of Normalized Dates', x_label='Normalized date (includes '+nEmtyCells+' SVOs with no date)', file_label='date', plot_list=['Frequency'], title_label='Normalized Dates')
    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    # Date types are in the form PAST, PRESENT, OTHER
    outputFiles = charts_util.plot(inputFilename, outputNormalizedDateDir, columns=['Date type'], title='Frequency Distribution of Date Types', x_label='Date type', file_label='date-types', plot_list=['Frequency'], title_label='Date Types (includes '+nEmtyCells+' SVOs with no date)')
    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    return filesToOpen
