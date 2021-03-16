import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"CoNLL search",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_CoNLL_util
import CoNLL_table_search_util
import statistics_csv_util
import Excel_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import Stanford_CoreNLP_tags_util
from data_manager_main import extract_from_csv
import pandas as pd
# more imports (e.g., import CoNLL_clause_analysis_util) are called below under separate if statements


# RUN section ______________________________________________________________________________________________________________________________________________________


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(inputFilename,outputDir,openOutputFiles,createExcelCharts,
        searchedCoNLLField,searchField_kw,postag,deprel,co_postag,co_deprel,
        clausal_analysis_var,
        noun_analysis_var,
        verb_analysis_var,
        function_words_analysis_var):

    global recordID_position,documentId_position,data, data_divided_sents

    noResults = "No results found matching your search criteria for your input CoNLL file. Please, try different search criteria.\n\nTypical reasons for this warning are:\n   1.  You are searching for a token/word not found in the FORM or LEMMA fields (e.g., 'child' in FORM when in fact FORM contains 'children', or 'children' in LEMMA when in fact LEMMA contains 'child'; the same would be true for the verbs 'running' in LEMMA instead of 'run');\n   2. you are searching for a token that is a noun (e.g., 'children'), but you select the POS value 'VB', i.e., verb, for the POSTAG of searched token."
    filesToOpen = []  # Store all files that are to be opened once finished
    outputFiles = []

    withHeader=True
    recordID_position=8
    documentId_position=10
    data,header=IO_csv_util.get_csv_data(inputFilename,withHeader)
    if len(data)==0:
        return
    data_divided_sents = IO_CoNLL_util.sentence_division(data)
    if data_divided_sents == None:
        return
    if len(data_divided_sents) == 0:
        return

    right_hand_side=False

    if extract_var.get():
        df = pd.read_csv(inputFilename)
        data_files = [df]
        print(csv_file_field_list)
        extracted_files = extract_from_csv(path=[inputFilename], output_path=outputDir, data_files=data_files,
                                           csv_file_field_list=csv_file_field_list)
        filesToOpen.append(extracted_files)

    if clausal_analysis_var:
        import CoNLL_clause_analysis_util
        outputFiles=CoNLL_clause_analysis_util.clause_stats(inputFilename, '', outputDir,
                                                                data,
                                                                data_divided_sents,
                                                                openOutputFiles, createExcelCharts)
        if outputFiles!=None:
            # only open the chart files
            if len(outputFiles)>0:
                filesToOpen.append(outputFiles[1])
            if len(outputFiles)>2:
                filesToOpen.append(outputFiles[2])

        right_hand_side=True

    if noun_analysis_var:
        import CoNLL_noun_analysis_util
        outputFiles=CoNLL_noun_analysis_util.noun_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createExcelCharts)
        if outputFiles!=None:
            # only open the chart files
            filesToOpen.append(outputFiles[6])
            filesToOpen.append(outputFiles[7])
            filesToOpen.append(outputFiles[8])

        right_hand_side=True

    if verb_analysis_var == True:
        import CoNLL_verb_analysis_util

        outputFiles=CoNLL_verb_analysis_util.verb_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createExcelCharts)

        # only open the chart files
        if outputFiles!=None:
            filesToOpen.append(outputFiles[2])
            filesToOpen.append(outputFiles[5])
            filesToOpen.append(outputFiles[7])

        right_hand_side=True


    if function_words_analysis_var==True:
        import CoNLL_function_words_analysis_util

        outputFiles=CoNLL_function_words_analysis_util.function_words_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createExcelCharts)
        # only open the chart files
        if outputFiles!=None:
            filesToOpen.append(outputFiles[2])
            filesToOpen.append(outputFiles[5])
            filesToOpen.append(outputFiles[8])
            filesToOpen.append(outputFiles[11])
            filesToOpen.append(outputFiles[14])

        right_hand_side=True

    if right_hand_side==True:
        if openOutputFiles == True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
            mb.showwarning(title='Output files', message="The analysis of the CoNLL table for clauses, nouns, verbs, and function words opens only the Excel chart files. But the script produces in output many more csv files.\n\nPlease, check your output directory for more file output.")
        filesToOpen = []  # Store all files that are to be opened once finished
        outputFiles = []
        return

    if searchField_kw == 'e.g.: father':
        mb.showwarning(title='No option selected', message="No option has been selected.\n\nPlease, select an option and try again.")
        return  # breaks loop

    if searchedCoNLLField.lower() not in ['lemma','form']:
            searchedCoNLLField = 'FORM'
    if postag!='*':
            postag = str(postag).split(' - ')[0]
            postag = postag.strip()
    else:
            postag = '*'
    if deprel!='*':
            deprel = str(deprel).split(' - ')[0]
            deprel = deprel.strip()
    else:
            deprel = '*'
    if co_postag!='*':
            co_postag = str(co_postag).split(' - ')[0]
            co_postag=co_postag.strip()
    else:
            co_postag = '*'
    if co_deprel!='*':
            co_deprel = str(co_deprel).split(' - ')[0]
            co_deprel = co_deprel.strip()
    else:
            co_deprel = '*'

    POS_tags = ['*', 'JJ*', 'NN*', 'VB*'] + [k for k, v in Stanford_CoreNLP_tags_util.dict_POSTAG.items()]
    POS_descriptions = [v for k, v in Stanford_CoreNLP_tags_util.dict_POSTAG.items()]

    DEPREL_tags = [k for k, v in Stanford_CoreNLP_tags_util.dict_DEPREL.items()]
    DEPREL_descriptions = [v for k, v in Stanford_CoreNLP_tags_util.dict_DEPREL.items()]


    if postag != '*' and postag not in POS_tags:
            postag = '*'
    if deprel!='*' and deprel not in DEPREL_tags: #dict_DEPREL:
            print ("The routine cannot recognize your input. The default value\'*\'(i.e. ANY VALUE) will be used.")
            deprel = '*'

    if co_postag  != '*' and co_postag not in POS_tags: #set_POSTAG: #search_CoNLL_table:
            co_postag = '*'

    if co_deprel!='*' and co_deprel not in DEPREL_tags: #set_DEPREL: #dict_DEPREL:
            print ("The routine cannot recognize your input. The default value\'*\'(i.e. ANY VALUE) will be used.")
            co_deprel = '*'

    if (not os.path.isfile(inputFilename.strip())) and (not inputFilename.strip()[-6:]=='.conll') and (not inputFilename.strip()[-4:]=='.csv'):
            mb.showwarning(title='INPUT File Path Error', message='Please, check INPUT FILE PATH and try again. The file must be a CoNLL table (extension .conll with Stanford CoreNLP no clausal tags, extension .csv with Stanford CoreNLP with clausal tags)')
            return
    if searchField_kw == 'e.g.: father':
            msg="Please, check the \'Searched token\' field and try again.\n\nThe value entered must be different from the default value (e.g.: father)."
            mb.showwarning(title='Searched Token Input Error', message=msg)
            return # breaks loop
    if len(searchField_kw) == 0:
            msg="Please, check the \'Searched token\' field and try again.\n\nThe value entered must be different from blank."
            mb.showwarning(title='Searched Token Input Error', message=msg)
            return # breaks loop

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running CoNLL search at', True)

    withHeader=True
    documentId_position=10
    data,header=IO_csv_util.get_csv_data(inputFilename,withHeader)

    if len(data) <= 1000000:
        try:
            data = sorted(data, key=lambda x: int(x[8]))
        except:
            mb.showwarning(title="CoNLLL table ill formed",
                           message="The CoNLL table is ill formed. You may have tinkered with it. Please, rerun the Stanford CoreNLP parser since many scripts rely on the CoNLL table.")
            return

    if len(data)==0:
        return
    all_sents = IO_CoNLL_util.sentence_division(data)
    if len(all_sents)==0:
        return
    queried_list=CoNLL_table_search_util.search_CoNLL_table(all_sents,searchField_kw,searchedCoNLLField, related_token_POSTAG=co_postag,related_token_DEPREL=co_deprel, _tok_postag_=postag,_tok_deprel_=deprel)

    if len(queried_list) != 0:
        if searchField_kw=='*':
            srcField_kw='astrsk'
        else:
            srcField_kw=searchField_kw
        output_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'QC', srcField_kw, searchedCoNLLField)
        errorFound=IO_csv_util.list_to_csv(GUI_util.window,CoNLL_table_search_util.output_list(queried_list,searchedCoNLLField,documentId_position), output_file_name)
        if errorFound==True:
            return
        filesToOpen.append(output_file_name)

        """
        The 15 indexed items are created in the function query_the_table:
            item[0] form/lemma, item[1] postag, item[2] deprel, item[3] is_head, item[4] Document_ID, 
            item[5] Sentence_ID, item[6] Document, item[7] whole_sent, 
            item[8] keyword[1]/SEARCHED TOKEN, 
            item[9] keyword[3]/SEARCHED TOKEN POSTAG, 
            item[10] keyword[6]/'SEARCHED TOKEN DEPREL'))
        """
        if createExcelCharts==True:

            # line plot by sentence index
            if searchedCoNLLField=='FORM':
                tempFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,output_file_name,'',outputDir,[[11,5],[11,7],[11,9]],['SEARCHED TOKEN POSTAG-DESCRIPTION'],['SEARCHED TOKEN (FORM)','Sentence'], ['Document ID','Sentence ID','Document'], openOutputFiles,createExcelCharts,'QC','line')
            else:
                tempFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,output_file_name,'',outputDir,[[11,5],[11,7],[11,9]],['SEARCHED TOKEN POSTAG-DESCRIPTION'],['SEARCHED TOKEN (LEMMA)','Sentence'], ['Document ID','Sentence ID','Document'], openOutputFiles,createExcelCharts,'QC','line')
            filesToOpen.extend(tempFiles)

            output_file_name_xlsx=IO_files_util.generate_output_file_name(inputFilename, '',  outputDir, '.xlsx', 'QC', 'kw_postag', 'stats_pie_chart')
            column_stats=statistics_csv_util.compute_stats_CoreNLP_tag(queried_list,9,"Searched token Postag Values (" + searchField_kw + ")","POSTAG")
            errorFound=IO_csv_util.list_to_csv(GUI_util.window,column_stats,output_file_name_xlsx)
            if errorFound==True:
                return
            output_file_name_xlsx=Excel_util.create_excel_chart(GUI_util.window,[column_stats],inputFilename, outputDir,"QueryCoNLL_POS","Searched token POStag Values (" + searchField_kw + ")",["pie"])
            filesToOpen.append(output_file_name_xlsx)

            output_file_name_xlsx=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.xlsx', 'QC', 'kw_deprel', 'stats_pie_chart')
            column_stats=statistics_csv_util.compute_stats_CoreNLP_tag(queried_list,10,"Searched token Deprel values (" + searchField_kw + ")","DEPREL")
            errorFound=IO_csv_util.list_to_csv(GUI_util.window,column_stats,output_file_name_xlsx)
            if errorFound==True:
                return
            output_file_name_xlsx=Excel_util.create_excel_chart(GUI_util.window,[column_stats],'', outputDir,"QueryCoNLL_DepRel","Searched token DEPrel Values (" + searchField_kw + ")",["pie"])
            filesToOpen.append(output_file_name_xlsx)

            output_file_name_xlsx=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.xlsx', 'QC', 'co_kw_postag', 'stats_pie_chart')
            column_stats=statistics_csv_util.compute_stats_CoreNLP_tag(queried_list,1,"Co-token Postag values (" + searchField_kw + ")","POSTAG")
            errorFound=IO_csv_util.list_to_csv(GUI_util.window,column_stats,output_file_name_xlsx)
            if errorFound==True:
                return
            output_file_name_xlsx=Excel_util.create_excel_chart(GUI_util.window,[column_stats],'', outputDir,"QueryCoNLL_CoOcc_POS","Co-token POStag Values (" + searchField_kw + ")",["pie"])
            filesToOpen.append(output_file_name_xlsx)

            output_file_name_xlsx=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.xlsx', 'QC', 'co_kw_deprel', 'stats_pie_chart')
            column_stats=statistics_csv_util.compute_stats_CoreNLP_tag(queried_list,2,"Co-token Deprel values (" + searchField_kw + ")","DEPREL")
            errorFound=IO_csv_util.list_to_csv(GUI_util.window,column_stats,output_file_name_xlsx)
            if errorFound==True:
                return

            output_file_name_xlsx=Excel_util.create_excel_chart(GUI_util.window,[column_stats],'', outputDir,"QueryCoNLL_CoOcc_DEP","Co-token DEPrel Values (" + searchField_kw + ")",["pie"])
            filesToOpen.append(output_file_name_xlsx)
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running CoNLL search at',True)

        if openOutputFiles==True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

        # # Gephi network graphs _________________________________________________
        # TODO
        # the CoNLL table search can export a word and related words in a variety of relations to the word (by POS DEPREL etc.)
        # ideally, these sets of related words can be visualized in a network graph in Gephi
        # But... Gephi has been hard coded for SVO, since it has only been used for that so far, but any 2 or 3-terms can be visualized as a network
        # Furthermore, if we cant to create dynamic models that vary ov ertime, wehere we use the sentence index as a proxy for time, we need to pass that variable as well (the saentence index)
        # create_gexf would need to read in the proper column names, rather than S V OA
        # outputFileBase = os.path.basename(output_file_name)[0:-4] # without .csv or .txt
        # gexf_file = Gephi_util.create_gexf(outputFileBase, outputDir, output_file_name)
        # filesToOpen.append(gexf_file)

    else:
        mb.showwarning(title='Empty query results', message=noResults)

run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            searchedCoNLLField.get(),
                            searchField_kw.get(),
                            postag_field.get(),
                            deprel_field.get(),
                            co_postag_field.get(),
                            co_deprel_field.get(),
                            clausal_analysis_var.get(),
                            noun_analysis_var.get(),
                            verb_analysis_var.get(),
                            function_words_analysis_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1260x590'
GUI_label='Graphical User Interface (GUI) for CoNLL Table Analyzer'
config_filename='conll-table-analyzer-config.txt' # filename used in Stanford_CoreNLP_main
# The 6 values of config_option refer to:
#   software directory
#   input file 1 for CoNLL file 2 for TXT file 3 for csv file 4 for any type of file
#   input dir
#   input secondary dir
#   output file
#   output dir
config_option=[0,1,0,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +1 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+1
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename)

searchField_kw = tk.StringVar()
searchedCoNLLField = tk.StringVar()
postag_field= tk.StringVar()
deprel_field = tk.StringVar()
searchField_co_postag = tk.StringVar()
co_postag_field = tk.StringVar()
co_deprel_field = tk.StringVar()
SVO_var=tk.IntVar()
csv_file_field_list = []

clausal_analysis_var=tk.IntVar()

noun_analysis_var = tk.IntVar()
verb_analysis_var = tk.IntVar()
function_words_analysis_var = tk.IntVar()

extract_var = tk.IntVar()
selected_fields_var = tk.StringVar()
select_csv_field_extract_var = tk.StringVar()

all_analyses_var = tk.IntVar()

buildString = ''
menu_values=[]


def clear(e):
    searchField_kw.set('e.g.: father')
    postag_field.set('*')
    deprel_field.set('*')
    searchField_co_postag.set('*')
    co_postag_field.set('*')
    co_deprel_field.set('*')
    activate_options()
    activate_csv_fields_selection(extract_var.get(), False, False)
    reset_all_values()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

# custom sorter to place non alpha strings later while custom sorting
def custom_sort(s):
    if s:
        if s[0].isalpha():
            return 0
        else:
            return 10
    else:
        return 10

tk.Label(window, text='Searched token').place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

searchField_kw.set('e.g.: father')

# used to place noun/verb checkboxes starting at the top level
y_multiplier_integer_top=y_multiplier_integer

entry_searchField_kw = tk.Entry(window, textvariable=searchField_kw)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,entry_searchField_kw)

# Search type var (FORM/LEMMA)
searchedCoNLLField.set('FORM')
searchedCoNLLdescription_csv_field_menu_lb = tk.Label(window, text='CoNLL search field')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,searchedCoNLLdescription_csv_field_menu_lb,True)

searchedCoNLLdescription_csv_field_menu_lb = tk.OptionMenu(window,searchedCoNLLField,'FORM','LEMMA')
searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,searchedCoNLLdescription_csv_field_menu_lb)

# POSTAG variable

postag_field.set('*')
tk.Label(window, text='POSTAG of searched token').place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
postag_description_csv_field_menu_lb = tk.Label(window, text='POSTAG')
#postag_menu = tk.OptionMenu(window,postag_field,'*','CC - Coordinating conjunction','CD - Cardinal number', 'DT - Determinant', 'EX - Existential there', 'FW - Foreign word', 'IN - Preposition or subordinating conjunction', 'JJ* - Any adjective','JJ - Adjective', 'JJR - Adjective, comparative', 'JJS - Adjective, superlative', 'LS - List marker','MD - Modal verb', 'NN* - Any noun','NN - Noun, singular or mass', 'NNS - Noun, plural', 'NNP - Proper noun, singluar', 'NNPS - Proper noun, plural', 'PDT - Predeterminer', 'POS - Possessive ending', 'PRP - Personal pronoun', 'RB* - Any adverb','RB - Adverb', 'RBR - Adverb, comparative', 'RBS - Adverb, superlative','RP - Particle', 'SYM - Symbol', 'TO - To', 'UH - Interjection', 'VB* - Any verb','VB - Verb, base form', 'VBD - Verb, past tense', 'VBG - Verb, gerundive or present participle', 'VBN - Verb, past participle', 'VBP - Verb, non-3rd person singular present', 'VBZ - Verb, 3rd person singular present','WDT - Wh-determiner (what, which, whose)', 'WP - Wh-pronoun (how, what, which, where, when, who, whom, whose, whether', 'WP - Possessive wh-pronoun', 'WRB - Wh-adverb (when, where, how, and why)','( - (',') - )','. - .',', - ,',': - :','\' - \'','\" - \"','# - #')
postag_menu_lb = tk.OptionMenu(window,postag_field,'*','JJ* - Any adjective', 'NN* - Any noun', 'VB* - Any verb', *sorted([k+ " - " +v for k, v in Stanford_CoreNLP_tags_util.dict_POSTAG.items()], key=lambda s: (custom_sort(s), s)))
postag_menu_lb.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,postag_menu_lb)

# DEPREL variable

deprel_field.set('*')
tk.Label(window, text='DEPREL of searched token').place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
#deprel_description_csv_field_menu_lb = tk.OptionMenu(window,deprel_field,'*','acl - clausal modifier of noun (adjectival clause)', 'acl:relcl - relative clause modifier', 'acomp - adjectival complement', 'advcl - adverbial clause modifier', 'advmod - adverbial modifier', 'agent - agent', 'amod - adjectival modifier', 'appos - appositional modifier', 'arg - argument', 'aux - auxiliary', 'auxpass - passive auxiliary', 'case - case marking', 'cc - coordinating conjunction', 'ccomp - clausal complement with internal subject', 'cc:preconj - preconjunct','compound - compound','compound:prt - phrasal verb particle','conj - conjunct','cop - copula conjunction','csubj - clausal subject','csubjpass - clausal passive subject','dep - unspecified dependency','det - determiner','det:predet - predeterminer','discourse - discourse element','dislocated - dislocated element','dobj - direct object','expl - expletive','foreign - foreign words','goeswith - goes with','iobj - indirect object','list - list','mark - marker','mod - modifier','mwe - multi-word expression','name - name','neg - negation modifier','nn - noun compound modifier','nmod - nominal modifier','nmod:npmod - noun phrase as adverbial modifier','nmod:poss - possessive nominal modifier','nmod:tmod - temporal modifier','nummod - numeric modifier','npadvmod - noun phrase adverbial modifier','nsubj - nominal subject','nsubjpass - passive nominal subject','num - numeric modifier','number - element of compound number','parataxis - parataxis','pcomp - prepositional complement','pobj - object of a preposition','poss - possession modifier', 'possessive - possessive modifier','preconj - preconjunct','predet - predeterminer','prep - prepositional modifier','prepc - prepositional clausal modifier','prt - phrasal verb particle','punct - punctuation','quantmod - quantifier phrase modifier','rcmod - relative clause modifier','ref - referent','remnant - remnant in ellipsis','reparandum - overridden disfluency','ROOT - root','sdep - semantic dependent','subj - subject','tmod - temporal modifier','vmod - reduced non-finite verbal modifier','vocative - vocative','xcomp - clausal complement with external subject','xsubj - controlling subject','# - #')
deprel_description_csv_field_menu_lb = tk.OptionMenu(window,deprel_field,'*', *sorted([k+ " - " +v for k, v in Stanford_CoreNLP_tags_util.dict_DEPREL.items()], key=lambda s: (custom_sort(s), s)))
deprel_description_csv_field_menu_lb.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,deprel_description_csv_field_menu_lb)

# Co-Occurring POSTAG menu

searchField_co_postag.set('*')

co_postag_field.set('*')
tk.Label(window, text='POSTAG of co-occurring tokens').place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
#co_postag_description_csv_field_menu_lb = tk.OptionMenu(window,co_postag_field,'*','CC - Coordinating conjunction','CD - Cardinal number', 'DT - Determinant', 'EX - Existential there', 'FW - Foreign word', 'IN - Preposition or subordinating conjunction', 'JJ* - Any adjective', 'JJ - Adjective', 'JJR - Adjective, comparative', 'JJS - Adjective, superlative', 'LS - List marker','MD - Modal verb', 'NN* - Any noun', 'NN - Noun, singular or mass', 'NNS - Noun, plural', 'NNP - Proper noun, singluar', 'NNPS - Proper noun, plural', 'PDT - Predeterminer', 'POS - Possessive ending', 'PRP - Personal pronoun', 'RB* - Any adverb','RB - Adverb', 'RBR - Adverb, comparative', 'RBS - Adverb, superlative','RP - Particle', 'SYM - Symbol', 'TO - To', 'UH - Interjection', 'VB* - Any verb', 'VB - Verb, base form', 'VBD - Verb, past tense', 'VBG - Verb, gerundive or present participle', 'VBN - Verb, past participle', 'VBP - Verb, non-3rd person singular present', 'VBZ - Verb, 3rd person singular present','WDT - Wh-determiner (what, which, whose)', 'WP - Wh-pronoun (how, what, which, where, when, who, whom, whose, whether', 'WP - Possessive wh-pronoun', 'WRB - Wh-adverb (when, where, how, and why)','( - (',') - )','. - .',', - ,',': - :','\' - \'','\" - \"','# - #')
#postag_menu = tk.OptionMenu(window,postag_field,'*',*IO_CoNLL_util.dict_POSTAG)
co_postag_description_csv_field_menu_lb = tk.OptionMenu(window,co_postag_field,'*','JJ* - Any adjective', 'NN* - Any noun', 'VB* - Any verb', *sorted([k+ " - " +v for k, v in Stanford_CoreNLP_tags_util.dict_POSTAG.items()], key=lambda s: (custom_sort(s), s)))
co_postag_description_csv_field_menu_lb.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,co_postag_description_csv_field_menu_lb)

# Co-Occurring DEPREL menu
co_deprel_field.set('*')
tk.Label(window, text='DEPREL of co-occurring tokens').place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
#co_deprel_description_csv_field_menu_lb = tk.OptionMenu(window,co_deprel_field,'*','acl - clausal modifier of noun (adjectival clause)', 'acl:relcl - relative clause modifier', 'acomp - adjectival complement', 'advcl - adverbial clause modifier', 'advmod - adverbial modifier', 'agent - agent', 'amod - adjectival modifier', 'appos - appositional modifier', 'arg - argument', 'aux - auxiliary', 'auxpass - passive auxiliary', 'case - case marking', 'cc - coordinating conjunction', 'ccomp - clausal complement with internal subject', 'cc:preconj - preconjunct','compound - compound','compound:prt - phrasal verb particle','conj - conjunct','cop - copula conjunction','csubj - clausal subject','csubjpass - clausal passive subject','dep - unspecified dependency','det - determiner','det:predet - predeterminer','discourse - discourse element','dislocated - dislocated element','dobj - direct object','expl - expletive','foreign - foreign words','goeswith - goes with','iobj - indirect object','list - list','mark - marker','mod - modifier','mwe - multi-word expression','name - name','neg - negation modifier','nn - noun compound modifier','nmod - nominal modifier','nmod:npmod - noun phrase as adverbial modifier','nmod:poss - possessive nominal modifier','nmod:tmod - temporal modifier','nummod - numeric modifier','npadvmod - noun phrase adverbial modifier','nsubj - nominal subject','nsubjpass - passive nominal subject','num - numeric modifier','number - element of compound number','parataxis - parataxis','pcomp - prepositional complement','pobj - object of a preposition','poss - possession modifier', 'possessive - possessive modifier','preconj - preconjunct','predet - predeterminer','prep - prepositional modifier','prepc - prepositional clausal modifier','prt - phrasal verb particle','punct - punctuation','quantmod - quantifier phrase modifier','rcmod - relative clause modifier','ref - referent','remnant - remnant in ellipsis','reparandum - overridden disfluency','ROOT - root','sdep - semantic dependent','subj - subject','tmod - temporal modifier','vmod - reduced non-finite verbal modifier','vocative - vocative','xcomp - clausal complement with external subject','xsubj - controlling subject','# - #')
co_deprel_description_csv_field_menu_lb = tk.OptionMenu(window,co_deprel_field,'*', *sorted([k+ " - " +v for k, v in Stanford_CoreNLP_tags_util.dict_DEPREL.items()], key=lambda s: (custom_sort(s), s)))
co_deprel_description_csv_field_menu_lb.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,co_deprel_description_csv_field_menu_lb)

# selected_fields_var = tk.StringVar()
# selected_fields_var.set('')
# selected_fields = tk.Entry(window, width=100, textvariable=selected_fields_var)
# selected_fields.configure(state="disabled")
# y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
#                                                selected_fields)

def reset_all_values():
    buildString=''
    selected_fields_var.set('')

    extract_checkbox.config(state='normal')

    comparator_menu.configure(state="disabled")
    where_entry.configure(state="disabled")
    and_or_menu.configure(state="disabled")

    selected_fields_var.set('')

    where_entry_var.set("")
    comparator_var.set("")
    and_or_var.set("")

    select_csv_field_extract_menu.config(state='disabled')

    extract_var.set(0)


def changed_filename(tracedInputFile):
    menu_values = []
    if tracedInputFile != '':
        numColumns = IO_csv_util.get_csvfile_numberofColumns(tracedInputFile)
        if numColumns == 0 or numColumns == None:
            return False
        if IO_csv_util.csvFile_has_header(tracedInputFile) == False:
            menu_values = range(1, numColumns + 1)
        else:
            data, headers = IO_csv_util.get_csv_data(tracedInputFile, True)
            menu_values = headers
    else:
        menu_values.clear()
        return
    m = select_csv_field_extract_menu["menu"]
    m.delete(0, "end")

    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: select_csv_field_extract_var.set(value))
    clear("<Escape>")
GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

extract_var.set(0)
extract_checkbox = tk.Checkbutton(window, text='Extract from CoNLL', variable=extract_var, onvalue=1,
                                  offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               extract_checkbox, True)

select_csv_field_lb = tk.Label(window, text='Select field')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 200, y_multiplier_integer,
                                               select_csv_field_lb, True)

if len(menu_values) > 0:
    select_csv_field_extract_menu = tk.OptionMenu(window, select_csv_field_extract_var, *menu_values)
else:
    select_csv_field_extract_menu = tk.OptionMenu(window, select_csv_field_extract_var, menu_values)
select_csv_field_extract_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 280, y_multiplier_integer,
                                               select_csv_field_extract_menu, True)

comparator_var = tk.StringVar()
comparator_menu = tk.OptionMenu(window, comparator_var, '<', '<=', '==', '>=', '>', '<>')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 410, y_multiplier_integer,
                                               comparator_menu, True)

where_lb = tk.Label(window, text='Enter value (WHERE)')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 485, y_multiplier_integer,
                                               where_lb, True)

where_entry_var = tk.StringVar()
where_entry = tk.Entry(window, width=25, textvariable=where_entry_var)
where_entry.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 610, y_multiplier_integer,
                                               where_entry, True)

and_or_lb = tk.Label(window, text='and/or')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 790, y_multiplier_integer,
                                               and_or_lb, True)

and_or_var = tk.StringVar()
and_or_menu = tk.OptionMenu(window, and_or_var, 'and', 'or')
and_or_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 840, y_multiplier_integer,
                                               and_or_menu, True)
def build_extract_string(comingFrom_Plus, comingFrom_OK):
    add_field_to_list(select_csv_field_extract_var.get(), comingFrom_OK)
    activate_csv_fields_selection(extract_var.get(), comingFrom_Plus, comingFrom_OK)

add_extract_options_var = tk.IntVar()
add_extract_options = tk.Button(window, text='+', width=2, height=1, state='disabled',
                                command=lambda: build_extract_string(True, False))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 905, y_multiplier_integer,
                                               add_extract_options, True)

OK_extract_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                              command=lambda: build_extract_string(False, True))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 955, y_multiplier_integer,
                                               OK_extract_button, True)

def add_field_to_list(menu_choice, visualizeBuildString=True):

    global buildString
    # skip empty values and csv fields already selected
    if select_csv_field_extract_var.get() == '':
        return

    if selected_fields_var.get() != '' and menu_choice not in selected_fields_var.get():
        selected_fields_var.set(selected_fields_var.get() + "," + str(menu_choice))
    else:
        selected_fields_var.set(menu_choice)

    buildString=buildString+menu_choice

    if comparator_var.get() != '' and where_entry_var.get() == '':
        mb.showwarning(title='Warning',
                       message='You have selected the comparator value ' + comparator_var.get() + '\n\nYou MUST enter a WHERE value or press ESC to cancel.')
        return
    # always enter the value even if empty to ensure a similarly formatted string
    if comparator_var.get() != '':
        buildString = buildString + "," + comparator_var.get()
    else:
        buildString = buildString + "," + "''"
    if where_entry_var.get() != '':
        buildString = buildString + "," + where_entry_var.get()
    else:
        buildString = buildString + "," + "''"
    if and_or_var.get() != '':
        buildString = buildString + "," + and_or_var.get()
    else:
        buildString = buildString + "," + "''"
    csv_file_field_list.append(buildString)


def show_values():
    mb.showwarning(title='Information',message=buildString)

show_button = tk.Button(window, width=7, text='Show', state='normal', command=lambda: show_values())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+1005, y_multiplier_integer,
                                               show_button,True)

reset_all_button = tk.Button(window, width=6, text='Reset', state='normal', command=lambda: reset_all_values())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+1075, y_multiplier_integer,
                                               reset_all_button)


def extractSelection(*args):
    # if extract_var.get():
    #     mb.showwarning(title='Warning',
    #                    message='The routine to extract fields an field values from the CoNLL table is under '
    #                            'construction.')
    activate_csv_fields_selection(extract_var.get(), False, False)


extract_var.trace('w', extractSelection)

SVO_var.set(0)
SVO_checkbox = tk.Checkbutton(window, text="Automatic extraction of Subject-Verb-Object from CoNLL table", variable=SVO_var, onvalue=1, offvalue=0)
SVO_checkbox.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,SVO_checkbox)

# Here rowspan=3 is necessary to make the separator span all 3 rows (the header, player 1 and player2).
# The sticky='ns' is there to stretch the separator from the top to the bottom of the window.
# Separators are only 1 pixel long per default, so without the sticky it would hardly be visible.
# tk.ttk.Separator(window, orient=tk.VERTICAL).grid(column=1, row=0, rowspan=3, sticky='ns')
# When you specify rowspan, it means that the widget will span its row and any rows below it
#ttk.Separator(window, orient=tk.VERTICAL).grid(column=1, row=0, rowspan=3, sticky='ns')
# without tk. VERTICAL is not defined; see GUI_IO_util slider_widget function
#ttk.Separator(window, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=3)

# used to place noun/verb checkboxes starting at the bottom level
y_multiplier_integer_bottom=y_multiplier_integer

y_multiplier_integer=y_multiplier_integer_top

clausal_analysis_var.set(0)
clausal_analysis_checkbox = tk.Checkbutton(window, text='CLAUSE analyses', variable=clausal_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+610,y_multiplier_integer,clausal_analysis_checkbox)

noun_analysis_var.set(0)
noun_analysis_checkbox = tk.Checkbutton(window, text='NOUN analyses', variable=noun_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+610,y_multiplier_integer,noun_analysis_checkbox)

verb_analysis_var.set(0)
verb_analysis_checkbox = tk.Checkbutton(window, text='VERB analyses', variable=verb_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+610,y_multiplier_integer,verb_analysis_checkbox)

function_words_analysis_var.set(0)
function_words_analysis_checkbox = tk.Checkbutton(window, text='FUNCTION WORDS analyses', variable=function_words_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+610,y_multiplier_integer,function_words_analysis_checkbox)

all_analyses_var.set(0)
all_analyses_checkbox = tk.Checkbutton(window, text="ALL anayses: Clauses, nouns, verbs, function words ('junk/stop' words)", variable=all_analyses_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+610,y_multiplier_integer,all_analyses_checkbox)

# -------------------------------------------------------------------------------------------------------

y_multiplier_integer=y_multiplier_integer_bottom

#
def activate_options(*args):
    if searchField_kw.get()!='e.g.: father':

        all_analyses_var.set(0)
        clausal_analysis_var.set(0)

        noun_analysis_var.set(0)
        verb_analysis_var.set(0)
        function_words_analysis_var.set(0)

        searchedCoNLLdescription_csv_field_menu_lb.configure(state='normal')
        postag_menu_lb.configure(state='normal')
        deprel_description_csv_field_menu_lb.configure(state='normal')
        co_postag_description_csv_field_menu_lb.configure(state='normal')
        co_deprel_description_csv_field_menu_lb.configure(state='normal')

        all_analyses_checkbox.configure(state='disabled')
        clausal_analysis_checkbox.configure(state='disabled')
        noun_analysis_checkbox.configure(state='disabled')
        verb_analysis_checkbox.configure(state='disabled')
        function_words_analysis_checkbox.configure(state='disabled')
    else:
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
        postag_menu_lb.configure(state='disabled')
        deprel_description_csv_field_menu_lb.configure(state='disabled')
        co_postag_description_csv_field_menu_lb.configure(state='disabled')
        co_deprel_description_csv_field_menu_lb.configure(state='disabled')

        all_analyses_checkbox.configure(state='normal')
        clausal_analysis_checkbox.configure(state='normal')
        noun_analysis_checkbox.configure(state='normal')
        verb_analysis_checkbox.configure(state='normal')
        function_words_analysis_checkbox.configure(state='normal')

        if all_analyses_var.get():
            entry_searchField_kw.configure(state='disabled')

            clausal_analysis_var.set(1)
            noun_analysis_var.set(1)
            verb_analysis_var.set(1)
            function_words_analysis_var.set(1)

            searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
            postag_menu_lb.configure(state='disabled')
            deprel_description_csv_field_menu_lb.configure(state='disabled')
            co_postag_description_csv_field_menu_lb.configure(state='disabled')
            co_deprel_description_csv_field_menu_lb.configure(state='disabled')

            clausal_analysis_checkbox.configure(state='normal')
            noun_analysis_checkbox.configure(state='normal')
            verb_analysis_checkbox.configure(state='normal')
            function_words_analysis_checkbox.configure(state='normal')
        else:
            entry_searchField_kw.configure(state='normal')
            clausal_analysis_var.set(0)
            noun_analysis_var.set(0)
            verb_analysis_var.set(0)
            function_words_analysis_var.set(0)
searchField_kw.trace('w',activate_options)
all_analyses_var.trace('w',activate_options)
#
#
activate_options()
#
def activate_CoNLL_options(*args):
    if clausal_analysis_var.get() == True or \
        noun_analysis_var.get() == True or \
        verb_analysis_var.get() == True or \
        function_words_analysis_var.get() == True:

                entry_searchField_kw.configure(state='disabled')
                searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
                postag_menu_lb.configure(state='disabled')
                deprel_description_csv_field_menu_lb.configure(state='disabled')
                co_postag_description_csv_field_menu_lb.configure(state='disabled')
                co_deprel_description_csv_field_menu_lb.configure(state='disabled')
    else:
        entry_searchField_kw.configure(state='normal')
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='normal')
        postag_menu_lb.configure(state='normal')
        deprel_description_csv_field_menu_lb.configure(state='normal')
        co_postag_description_csv_field_menu_lb.configure(state='normal')
        co_deprel_description_csv_field_menu_lb.configure(state='normal')
clausal_analysis_var.trace('w',activate_CoNLL_options)
noun_analysis_var.trace('w',activate_CoNLL_options)
verb_analysis_var.trace('w',activate_CoNLL_options)
function_words_analysis_var.trace('w',activate_CoNLL_options)


def activate_csv_fields_selection(checkButton, comingFrom_Plus, comingFrom_OK):
    if extract_var.get():
        select_csv_field_extract_menu.configure(state='normal')

    if not checkButton:
        extract_checkbox.config(state='normal')
        select_csv_field_extract_var.set('')
        select_csv_field_extract_menu.config(state='disabled')

        comparator_menu.configure(state="disabled")
        where_entry.configure(state="disabled")
        and_or_menu.configure(state="disabled")
        OK_extract_button.config(state='disabled')

        where_entry_var.set("")
        comparator_var.set("")
        and_or_var.set("")
    if checkButton:
        reset_all_button.config(state='normal')
        if select_csv_field_extract_var.get() != '':
            if comingFrom_Plus:
                select_csv_field_extract_menu.configure(state='normal')
            else:
                select_csv_field_extract_menu.configure(state='disabled')

            if where_entry_var.get() != '':
                and_or_menu.configure(state='normal')
            else:
                and_or_menu.configure(state='disabled')

            if comingFrom_OK:
                comparator_menu.configure(state="disabled")
                where_entry.configure(state="disabled")
                and_or_menu.configure(state='disabled')
                add_extract_options.config(state='disabled')
                OK_extract_button.config(state='disabled')
            else:
                add_extract_options.config(state='normal')
                OK_extract_button.config(state='normal')
                comparator_menu.configure(state="normal")
                where_entry.configure(state="normal")
        else:
            select_csv_field_extract_menu.configure(state='normal')
            extract_checkbox.config(state='normal')
            comparator_menu.configure(state="normal")
            where_entry.configure(state="normal")
            and_or_menu.configure(state="normal")
            OK_extract_button.config(state='normal')



select_csv_field_extract_var.trace('w', lambda x, y, z: extract_var.get())

activate_csv_fields_selection(extract_var.get(), False, False)

TIPS_lookup = {'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf", 'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf", 'DEPREL (Stanford Dependency Relations)': "TIPS_NLP_DEPREL (Dependency Relations) Stanford CoreNLP.pdf", 'English Language Benchmarks':'TIPS_NLP_English Language Benchmarks.pdf','Style Analysis':'TIPS_NLP_Style Analysis.pdf','Clause Analysis':'TIPS_NLP_Clause Analysis.pdf','Noun Analysis':'TIPS_NLP_Noun Analysis.pdf','Verb Analysis':'TIPS_NLP_Verb Analysis.pdf','Function Words Analysis':'TIPS_NLP_Function Words Analysis.pdf','Nominalization':'TIPS_NLP_Nominalization.pdf','NLP Searches': "TIPS_NLP_NLP Searches.pdf",'Excel Charts':'TIPS_NLP_Excel Charts.pdf','Excel Enabling Macros':'TIPS_NLP_Excel Enabling macros.pdf','Network Graphs (via Gephi)':'TIPS_NLP_Gephi network graphs.pdf'}
TIPS_options='CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)','English Language Benchmarks','Style Analysis','Clause Analysis','Noun Analysis','Verb Analysis','Function Words Analysis','Nominalization','NLP Searches','Excel Charts','Excel Enabling Macros','Network Graphs (via Gephi)'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
right_msg="\n\nON THE RIGHT-HAND SIDE, please, tick any of the checkboxes to obtain frequency distributions of specific linguistic objects."
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    resetAll = "\n\nPress the RESET ALL button to clear all values, including csv files and fields, and start fresh."
    plusButton = "\n\nPress the + buttons, when available, to add either a new field from the same csv file (the + button at the end of this line) or a new csv file (the + button next to File at the top of this GUI). Multiple csv files can be used with any of the operations."
    OKButton = "\n\nPress the OK button, when available, to accept the selections made, then press the RUN button to process the query."
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_CoNLL )
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help","ON THE LEFT-HAND SIDE, please, enter the token (i.e., word) to be searched. ENTER * TO SEARCH FOR ANY TOKEN/WORD.\n\nTHE SELECT OUTPUT BUTTON IS DISABLED UNTIL A SEARCHED TOKEN HAS BEEN ENTERED.\n\nThe program will search all the tokens related to this token in the CoNLL table. For example, if “father” is entered, the program will search in each dependency tree (i.e., each sentence) all the tokens whose head is the token “father”, and the head of the token “father”."+right_msg+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help","ON THE LEFT-HAND SIDE, please, select the CoNLL field to be used for the search (FORM or LEMMA).\n\nFor example, if “brother” is entered as the searched token, and “FORM” is entered as search field, the program will first search all occurrences of the FORM “brother”. Note that in this case “brothers” will NOT be considered. Otherwise, if “LEMMA” is entered as search field, the program will search all occurences of the LEMMA “brother”. In this case, tokens with form “brother” and “brothers” will all be considered."+right_msg+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help","ON THE LEFT-HAND SIDE, please, select POSTAG value for searched token (e.g., NN for noun; RETURN for ANY POSTAG value)."+right_msg+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help","ON THE LEFT-HAND SIDE, please, select DEPREL value for searched token (e.g., nsubjpass for passive nouns that are subjects; RETURN for ANY DEPREL value)."+right_msg+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help","ON THE LEFT-HAND SIDE, please, select POSTAG value for token co-occurring in the same sentence (e.g., NN for noun; RETURN for ANY POSTAG value)."+right_msg+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help","ON THE LEFT-HAND SIDE, please, select DEPREL value for token co-occurring in the same sentence (e.g., DEPREL nsubjpass for passive nouns that are subjects; RETURN for ANY DEPREL value)."+right_msg+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 8, "Help",
                                  "The EXTRACT option allows you to select specific fields, even by specific values, from one or more csv files and save the output as a new file.\n\nStart by ticking the Extract checkbox, then selecting the csv field from the current csv file. To filter the field by specific values, select the comparator character to be used (e.g., =), enter the desired value, and select and/or if you want to add another filter.\n\nOptions become available in succession.\n\nPress the + button to register your choices (these will be displayed in command line in the form: filename and path, field, comparator, WHERE value, and/or selection; empty values will be recorded as ''. ). PRESSING THE + BUTTON TWICE WITH NO NEW CHOICES WILL CLEAR THE CURRENT CHOICES. PRESS + AGAIN TO RE-INSERT THE CHOICES. WATCH THIS IN COMMAND LINE.\n\nIF YOU DO NOT WISH TO FILTER FIELDS, PRESS THE + BUTTON AFTER SELECTING THE FIELD." + plusButton + OKButton + GUI_IO_util.msg_Esc + resetAll)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help","ON THE LEFT-HAND SIDE, please, tick the checkbox if you wish to extract SVOs from the CoNLL table.\n\nON THE RIGHT-HAND SIDE, tick the 'All analyses: clauses, nouns, verbs, function words (\'junk/stop\' words)' to select and deselect all options, allowing you to select specific options."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*10,"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script will allo you to analyze in depth the contents of the CoNLL table, the table produced by Stanford CoreNLP parser. You can do two things in this GUI, depending upon whether you use the tools on the left-hand side (a search tool) or the tools on the right-hand side (statistical frequency tools).\n\nON THE LEFT-HAND SIDE, you can search all the tokens (i.e., words) related to a user-supplied keyword, found in either FORM or LEMMA of a user-supplied CoNLL table.\n\nYou can filter results by specific POSTAG and DEPREL values for both searched and co-occurring tokens (e.g., POSTAG ‘NN for nouns, DEPREL nsubjpass for passive nouns that are subjects.)\n\nIn INPUT the script expects a CoNLL table generated by the python script StanfordCoreNLP.py. \n\nIn OUTPUT the script creates a tab-separated csv file with a user-supplied filename and path.\n\nThe script also displays the same infomation in the command line.\n\nON THE RIGHT-HAND SIDE, the tools provide frequency distributions of various types of linguistic objects: clauses, nouns, verbs, and function words." + GUI_IO_util.msg_multipleDocsCoNLL
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

GUI_util.window.mainloop()

