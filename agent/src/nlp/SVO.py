import logging

# Written by Gabriel Wang 2018
# Modified by Cynthia Dong (Fall 2019-Spring 2020)
# Modified by Matthew Chau (Spring 2021)
# Modified by Roberto Franzosi (Spring-Fall 2021, Fall 2022)
# Modified by Cynthia Dong (Fall 2021)
# https://stackoverflow.com/questions/61121239/how-to-extract-subject-verb-object-using-nlp-java-for-every-sentence
import os

# to install stanfordnlp, first install
#   pip3 install torch===1.4.0 torchvision===0.5.0 -f https://download.pytorch.org/whl/torch_stable.html
#   pip3 install stanfordnlp
import config_util
import GIS_pipeline_util
import GUI_IO_util
import IO_csv_util
import IO_files_util
import IO_libraries_util
import spaCy_util
import Stanford_CoreNLP_coreference_util
import Stanford_CoreNLP_util
import Stanza_util
import SVO_util
from util import collect

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_svo(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    coref_var,
    manual_coref_var,
    normalized_NER_date_extractor_var,
    package_var,
    gender_var,
    quote_var,
    subjects_dict_path_var,
    verbs_dict_path_var,
    objects_dict_path_var,
    filter_subjects,
    filter_verbs,
    filter_objects,
    lemmatize_subjects,
    lemmatize_verbs,
    lemmatize_objects,
    gephi_var,
    google_earth_var,
):
    # Already hard coded below

    """Extract Subject-Verb-Object triples via CoreNLP enhanced dependencies."""
    config_filename = "NLP_default_IO_config.csv"
    # get the NLP package and language options
    (
        error,
        package,
        parsers,
        package_basics,
        language,
        package_display_area_value,
        encoding_var,
        export_json_var,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
    ) = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    config_input_output_numeric_options = [1, 0, 0, 1]
    # get the date options from filename
    filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = (
        config_util.get_date_options(config_filename, config_input_output_numeric_options)
    )
    extract_date_from_text_var = 0

    outputSVODir = ""
    outputLocations = []

    filesToOpen = []

    # # get the NLP package and language options

    # # get the date options from filename
    # filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
    #     config_filename, config_input_output_numeric_options)

    if package_display_area_value == "":
        logger.info(
            "No setup for NLP package and language, the default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again. "
        )
        return

    # the merge option refers to merging the txt files into one

    if not coref_var and package_display_area_value == "":
        logger.info("No option selected, please, select an option and try again. ")

        return

    if inputFilename[-4:] == ".csv":
        if "SVO_" not in inputFilename:
            logger.info(
                "Input file error, the selected input is a csv file, but... not an _svo.csv file.\n\nPlease, select an _svo.csv file (or txt file(s)) and try again."
            )

            return
        if coref_var or manual_coref_var:
            logger.info(
                "Input file/option error, the data analysis option(s) you have selected require in input a txt file, rather than a csv file.\n\nPlease, check your input file and/or algorithm selections and try again."
            )
            return

    annotator = ["SVO"]
    svo_result_list = []
    location_filename = ""
    outputDirSV = outputDir

    if len(inputFilename) > 0:
        save_intermediate_file = False
    else:  # directory input
        save_intermediate_file = False

    if package_var == "Stanford CoreNLP":
        # simplify the name since it is then used in output files/folders
        package_var = "CoreNLP"
    if "OpenIE" in package_var:
        package_var = "OpenIE"

    # the actual directory is created in the CoreNLP_annotator_util
    #   all we need here is the name of the directory
    if inputFilename != "":
        inputBaseName = os.path.basename(inputFilename)[0:-4]  # without .txt
    else:
        inputBaseName = os.path.basename(inputDir)
    if coref_var:
        outputCorefDir = os.path.join(outputDirSV, "coref_" + package_var + "_" + inputBaseName)
        outputSVODir = os.path.join(outputDir, "SVO_coref_" + package_var + "_" + inputBaseName)
    else:
        outputCorefDir = ""
        outputSVODir = os.path.join(outputDir, "SVO_" + package_var + "_" + inputBaseName)

    # create an SVO subdirectory of the output directory
    outputSVODir = IO_files_util.make_output_subdirectory("", "", outputSVODir, label="", silent=True)
    if outputSVODir == "":
        return

    outputDir = (
        outputSVODir  # outputDir is the main subdir inside the main output directory inside which will go gender,
    )
    # the outputDir folder inside the main output folder will contain subdir SVO, gender, GIS, quote, etc.

    if package_var == "OpenIE":
        outputSVOSVODir = outputSVODir + os.sep + package_var
    else:
        outputSVOSVODir = outputSVODir + os.sep + "SVO"

    # CoRef _____________________________________________________

    if coref_var:
        # must be changed
        if language_var != "English" and language_var != "Chinese":
            logger.info(
                "Language, The Stanford CoreNLP coreference resolution annotator is only available for English and Chinese."
            )
            return
        # create a subdirectory of the output directory
        outputCorefDir = IO_files_util.make_output_subdirectory("", "", outputCorefDir, "", silent=True)
        # inputFilename and inputDir are the original txt files to be coreferenced
        # 2 items are returned: filename string and true/False for error
        outputFiles, error_indicator = Stanford_CoreNLP_coreference_util.run(
            config_filename,
            inputFilename,
            inputDir,
            outputCorefDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            language_var,
            memory_var,
            export_json_var,
            manual_coref_var,
        )
        if error_indicator != 0:
            return
        for file in outputFiles:
            # visualize the data produced under coref table
            if "chart" in file or ".csv" in file:
                filesToOpen.append(file)

        # changed the inputDir to the coreferenced dir
        inputDir = outputCorefDir + os.sep + "coref_" + package_var
        # only the inputDir will be used when coreferencing, whether it will contain a set of files or just one file
        inputFilename = ""

    # create an SVO_filtered subdirectory of the main output directory
    if (
        (filter_subjects and not lemmatize_subjects)
        or (filter_verbs and not lemmatize_verbs)
        or (filter_objects and not lemmatize_objects)
    ):
        logger.info(
            "Warning, Filtering for either S or V or O requires lemmatizing the respective object, S or V or O. \n\nFiltering is based on WordNet and all WWordNet entries are lemmatized. "
        )
        return

    if filter_subjects or filter_verbs or filter_objects:
        outputSVODir + os.sep + "SVO_filtered"

    if google_earth_var:
        # create a GIS subdirectory of the output directory
        outputGISDir = IO_files_util.make_output_subdirectory("", "", outputSVODir, label="GIS", silent=True)
        location_filename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputGISDir, ".csv", "SVO_" + package_var + "_LOCATIONS"
        )
        outputLocations.append(location_filename)

    # Stanford CoreNLP Dependencies ++ _____________________________________________________

    if package_var == "CoreNLP" and inputFilename[-4:] != ".csv":
        if language_var == "Arabic" or language_var == "Hungarian":
            logger.info(
                "language, The Stanford CoreNLP dependency parsing is is not available for Arabic and Hungarian."
            )
            return

        if not IO_libraries_util.check_inputPythonJavaProgramFile("Stanford_CoreNLP_util.py"):
            return

        annotator = ["SVO"]
        if gender_var:
            # In Stanford_CoreNLP_util def create_output_directory subdir are created in the form annotator + "_CoreNLP"
            #   must respect this format to avoid error warning
            gender_filename = IO_files_util.generate_output_file_name(
                inputFilename, inputDir, outputSVODir + os.sep + "gender_CoreNLP", ".csv", ""
            )  # SVO_CoreNLP_gender

            gender_filename_html = IO_files_util.generate_output_file_name(
                inputFilename, inputDir, outputSVODir + os.sep + "gender_CoreNLP", ".html", ""
            )  # dict_annotated_gender

            annotator.append("gender")
        else:
            gender_filename = ""
            gender_filename_html = ""
        if quote_var:
            # In Stanford_CoreNLP_util def create_output_directory subdir are created in the form annotator + "_CoreNLP"
            #   must respect this format to avoid error warning
            quote_filename = IO_files_util.generate_output_file_name(
                inputFilename, inputDir, outputSVODir + os.sep + "quote_CoreNLP", ".csv", ""
            )  # SVO_CoreNLP_quote
            annotator.append("quote")
        else:
            quote_filename = ""

        # annotator_params are different from gender_var and quote_var
        # annotator_params will run the annotator for SVO and run the gender and quote placing results inside the SVO output folder
        # gender_var and quote_var are used in CoreNLP_annotate to add gender and quote columns to the SVO csv output file
        # they can be passed independently, but it is useful to have both arguments
        outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputSVODir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            annotator,
            False,
            language_var,
            export_json_var,
            memory_var,
            document_length_var,
            limit_sentence_length_var,
            filter_subjects=filter_subjects,
            extract_date_from_text_var=extract_date_from_text_var,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
            google_earth_var=google_earth_var,
            location_filename=location_filename,
            gender_var=gender_var,
            gender_filename=gender_filename,
            gender_filename_html=gender_filename_html,
            quote_var=quote_var,
            quote_filename=quote_filename,
        )

        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
                SVO_filename = outputFiles
                svo_result_list.append(outputFiles)
            else:
                if len(outputFiles) == 0:
                    return
                filesToOpen.extend(outputFiles)
                SVO_filename = outputFiles[0]
                svo_result_list.append(outputFiles[0])

            # TODO MINO: create normalize_date subdir and outputs
            nDateOutput = SVO_util.normalize_date_svo(SVO_filename, outputSVODir, chartPackage, dataTransformation)
            if nDateOutput is not None:
                if len(nDateOutput) > 0:
                    filesToOpen.extend(nDateOutput)

    # Stanford CoreNLP OpenIE _____________________________________________________
    if "OpenIE" in package_var and inputFilename[-4:] != ".csv":
        if language_var != "English":
            logger.info("language, The Stanford CoreNLP OpenIE annotator is only available for English.")
            return

        outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputSVODir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            "OpenIE",
            False,
            language_var,
            memory_var,
            export_json_var,
            document_length_var,
            limit_sentence_length_var,
            extract_date_from_text_var=extract_date_from_text_var,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
            google_earth_var=google_earth_var,
            location_filename=location_filename,
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
                SVO_filename = outputFiles
                svo_result_list.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
                SVO_filename = outputFiles[0]
                svo_result_list.append(outputFiles[0])

    # removed from the options; way way too slow and with far better options now in spaCy and Stanza
    # SENNA _____________________________________________________
    #   SENNA no longer used
    #     if package_var=='SENNA':
    #         if language_var != 'English':
    #             mb.showwarning(title='Language',
    #                            message='SENNA is only available for English.')
    #         tempOutputFiles = SENNA_util.run_senna(inputFilename, inputDir, outputSVODir, openOutputFiles,
    #                                                                 chartPackage, dataTransformation)
    #         if len(tempOutputFiles)!=0:

    # spaCY _____________________________________________________

    if package_var == "spaCy" and inputFilename[-4:] != ".csv":
        document_length_var = 1
        limit_sentence_length_var = 1000
        annotator = "SVO"
        outputFiles = spaCy_util.spaCy_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputSVODir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            annotator,
            False,
            language,
            memory_var,
            document_length_var,
            limit_sentence_length_var,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
            google_earth_var=google_earth_var,
            location_filename=location_filename,
        )

        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
                SVO_filename = outputFiles
                svo_result_list.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
                # the SVO output file is in outputFiles[1] outputFiles[0] contains the CoNLL parser output
                SVO_filename = outputFiles[1]
                svo_result_list.append(outputFiles[1])

    # Stanza _____________________________________________________

    if package_var == "Stanza" and inputFilename[-4:] != ".csv":
        document_length_var = 1
        limit_sentence_length_var = 1000
        annotator = ["SVO"]
        outputFiles = Stanza_util.Stanza_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputSVODir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            annotator,
            False,
            language_list,
            memory_var,
            document_length_var,
            limit_sentence_length_var,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
            google_earth_var=google_earth_var,
            location_filename=location_filename,
        )

        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
                SVO_filename = outputFiles
                svo_result_list.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
                # the SVO output file is in outputFiles[1] outputFiles[0] contains the CoNLL parser output
                SVO_filename = outputFiles[1]
                svo_result_list.append(outputFiles[1])

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Lemmatizing and Filtering SVO for all packages

    subject_filePath = GUI_IO_util.wordLists_libPath + os.sep + "social-actor-list.csv"
    verb_filePath = GUI_IO_util.wordLists_libPath + os.sep + "social-action-list.csv"
    object_filePath = GUI_IO_util.wordLists_libPath + os.sep + "social-actor-list.csv"
    SVO_lemmatized_filename = ""
    SVO_filtered_filename = ""
    if len(svo_result_list) > 0:
        if (
            lemmatize_subjects
            or lemmatize_verbs
            or lemmatize_objects
            or filter_subjects
            or filter_verbs
            or filter_objects
        ):
            output = SVO_util.lemmatize_filter_svo(
                SVO_filename,
                filter_subjects,
                filter_verbs,
                filter_objects,
                subject_filePath,
                verb_filePath,
                object_filePath,
                lemmatize_subjects,
                lemmatize_verbs,
                lemmatize_objects,
                outputSVOSVODir,
                chartPackage,
                dataTransformation,
            )
            if output is not None:
                if "English" in language:  # SVO filtered by WordNet are available for English only
                    if lemmatize_subjects or lemmatize_verbs or lemmatize_objects:
                        SVO_lemmatized_filename = output[0]
                    if filter_subjects or filter_verbs or filter_objects:
                        SVO_filtered_filename = output[1]
                else:
                    SVO_lemmatized_filename = output[0]
                if SVO_lemmatized_filename != "":
                    svo_result_list.append(SVO_lemmatized_filename)
                if SVO_filtered_filename != "":
                    svo_result_list.append(SVO_filtered_filename)

        # WordNet is only available for English
        if language_var == "English" and (lemmatize_subjects or lemmatize_verbs or lemmatize_objects):
            # outputFiles[0] is the filename with lemmatized SVO values
            # we want to aggregate with WordNet the verbs in column 'V'
            # check that SVO output file contains records
            nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(
                SVO_lemmatized_filename, encodingValue="utf-8"
            )
            if nRecords > 1:
                # outputWNDir is created in SVO_util
                # # create a subdirectory of the output SVO directory for filtered SVOs
                # # filtered SVOs are stored in the WordNet directory
                outputWNDir = IO_files_util.make_output_subdirectory("", "", outputSVODir, label="WordNet", silent=True)
                outputFilename = IO_csv_util.extract_from_csv(
                    SVO_lemmatized_filename, outputSVODir, "", ["Subject (S)", "Object (O)"]
                )
                # the WordNet installation directory, WordNetDir,  is now checked in aggregate_GoingUP
                # output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir, outputFilename, outputWNDir,
                #                                                          config_filename, 'NOUN',
                #                                                          openOutputFiles,
                #                                                          chartPackage, dataTransformation, language_var)
                output = None
                os.remove(outputFilename)
                if output is not None and output != "":
                    filesToOpen.extend(output)
                if lemmatize_verbs:
                    outputFilename = IO_csv_util.extract_from_csv(
                        SVO_lemmatized_filename, outputWNDir, "", ["Verb (V)"]
                    )
                    output = None
                    # output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir, outputFilename, outputWNDir,
                    #                                                          config_filename, 'VERB',
                    #                                                          openOutputFiles,
                    #                                                          chartPackage, dataTransformation, language_var)
                    os.remove(outputFilename)
                    if output is not None and output != "":
                        filesToOpen.extend(output)

        # reminders_util.checkReminder(scriptName, reminders_util.title_options_no_SVO_records,
        #                              reminders_util.message_no_SVO_records, True)

    # reminders_util.checkReminder(scriptName, reminders_util.title_options_SVO_Inferred_Subject_Passive,
    #                             #  reminders_util.message_SVO_Inferred_Subject_Passive, True)
    # the SVO script can take in input a csv SVO file previously computed (in which case the filename will contain SVO_): inputFilename
    # results currently produced are in svo_result_list

    if inputFilename[-4:] == ".csv":
        svo_result_list.append(inputFilename)
        SVO_filename = inputFilename
    if ("SVO_" in inputFilename) or (len(svo_result_list) > 0):
        i = 0
        for f in svo_result_list:
            head, tail = os.path.split(svo_result_list[i])
            tempOutputDir = head
            # Gephi network graphs _________________________________________________
            if gephi_var:
                import charts_util
                import Gephi_util

                # previous svo csv files can be entered in input to display networks, wordclouds or GIS maps
                if inputFilename[-4:] == ".csv":
                    fileBase = os.path.basename(inputFilename)[0:-4]
                    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(
                        inputFilename, encodingValue="utf-8"
                    )
                    if nRecords > 1:  # including headers; file is empty
                        gexf_file = Gephi_util.create_gexf(
                            fileBase,
                            tempOutputDir,
                            inputFilename,
                            "Subject (S)",
                            "Verb (V)",
                            "Object (O)",
                            "Sentence ID",
                        )
                        if gexf_file is not None and gexf_file != "":
                            filesToOpen.append(gexf_file)
                    else:
                        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_result_list[0])
                        if nRecords > 1:  # including headers; file is empty
                            gexf_file = Gephi_util.create_gexf(
                                fileBase,
                                inputFilename,
                                svo_result_list[0],
                                "Subject (S)",
                                "Verb (V)",
                                "Object (O)",
                                "Sentence ID",
                            )
                            if gexf_file is not None and gexf_file != "":
                                filesToOpen.append(gexf_file)

                    Sankey_limit1_var = 5
                    Sankey_limit2_var = 10
                    Sankey_limit3_var = 20
                    three_way_Sankey = True

                    output_label = "sankey"
                    outputFilename_sankey = IO_files_util.generate_output_file_name(
                        inputFilename, inputDir, tempOutputDir, ".html", output_label
                    )

                    outputFiles = charts_util.Sankey(
                        inputFilename,
                        outputFilename_sankey,
                        "Subject (S)",
                        Sankey_limit1_var,
                        "Verb (V)",
                        Sankey_limit2_var,
                        three_way_Sankey,
                        "Object (O)",
                        Sankey_limit3_var,
                    )

                    if outputFiles is not None:
                        collect(filesToOpen, outputFiles)

                else:  # txt input file
                    # for f in svo_result_list:
                    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(f)
                    if nRecords > 1:  # including headers; file is empty
                        # keep separate in case you want to export the 3 Gephi files
                        #   (normal, lemma, filtered) to different folders
                        #   now exported to the main SVO subdir
                        # if 'SVO_lemma' in svo_result_list[i]:
                        # using Sentence ID as a proxy of a date variable to create a dynamic network graph
                        gexf_file = Gephi_util.create_gexf(
                            os.path.basename(f)[:-4],
                            tempOutputDir,
                            f,
                            "Subject (S)",
                            "Verb (V)",
                            "Object (O)",
                            "Sentence ID",
                        )
                        if "CoreNLP" in f or "SENNA_SVO" in f or "spaCy" in f or "Stanza" in f:
                            if gexf_file is not None and gexf_file != "":
                                filesToOpen.append(gexf_file)
                        if not save_intermediate_file:
                            inputDocs = IO_files_util.getFileList(
                                inputFilename, inputDir, fileType=".txt", silent=False, configFileName=config_filename
                            )

                            # gexf_files = [os.path.join(outputDir, f) for f in os.listdir(tempOutputDir) if
                            gexf_files = [os.path.join(outputDir, f) for f in inputDocs if f.endswith(".gexf")]
                            for f in gexf_files:
                                if (
                                    "CoreNLP" not in f
                                    and "SENNA_SVO" not in f
                                    and "spaCy" not in f
                                    and "Stanza" not in f
                                ):  # CoreNLP accounts for both ++ and OpenIE
                                    os.remove(f)

                        output_label = "sankey"
                        Sankey_limit1_var = 5
                        Sankey_limit2_var = 10
                        Sankey_limit3_var = 20
                        three_way_Sankey = True

                        outputFilename_sankey = IO_files_util.generate_output_file_name(
                            f, inputDir, tempOutputDir, ".html", output_label
                        )
                        outputFiles = charts_util.Sankey(
                            f,
                            outputFilename_sankey,
                            "Subject (S)",
                            Sankey_limit1_var,
                            "Verb (V)",
                            Sankey_limit2_var,
                            three_way_Sankey,
                            "Object (O)",
                            Sankey_limit3_var,
                        )

                        if outputFiles is not None:
                            collect(filesToOpen, outputFiles)

            i += 1

        # GIS maps _____________________________________________________

        if google_earth_var:
            # SENNA locations are not really geocodable locations
            # if (package_var=='SENNA') and os.path.isfile(location_filename):
            #     reminders_util.checkReminder(scriptName, reminders_util.title_options_GIS_OpenIE_SENNA,
            #                                  reminders_util.message_GIS_OpenIE_SENNA, True)
            #     if (package_var != 'SENNA') and os.path.isfile(location_filename):
            #         reminders_util.checkReminder(scriptName, reminders_util.title_options_geocoder,
            #                                      reminders_util.message_geocoder, True)
            # locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
            date_present = (extract_date_from_text_var) or (filename_embeds_date_var)
            country_bias = ""
            area_var = ""
            restrict = False
            for location_filename in outputLocations:
                outputFiles = GIS_pipeline_util.GIS_pipeline(
                    config_filename,
                    location_filename,
                    inputDir,
                    outputGISDir,
                    "Nominatim",
                    "Google Earth Pro & Google Maps",
                    chartPackage,
                    dataTransformation,
                    date_present,
                    country_bias,
                    area_var,
                    restrict,
                    "Location",
                    "utf-8",
                    0,
                    1,
                    [""],
                    [""],  # group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                    ["Pushpins"],
                    ["red"],  # icon_var_list, specific_icon_var_list,
                    [0],
                    ["1"],
                    [0],
                    [""],  # name_var_list, scale_var_list, color_var_list, color_style_var_list,
                    [1],
                    [1],
                )  # bold_var_list, italic_var_list

                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)

    # generate subset of files to be opened

    if openOutputFiles and len(filesToOpen) > 0:
        filesToOpenSubset = []
        # add the SVO main files
        filesToOpenSubset.append(SVO_filename)
        for file in filesToOpen:
            # open all charts, all Google Earth and Google Maps maps, Gephi gexf network graph, html files, and wordclouds png files
            if file[-4:] == ".kml" or file[-5:] == ".html" or file[-4:] == ".png" or file[-5:] == ".gexf":  # or \
                # file[-5:] == '.xlsx':
                filesToOpenSubset.append(file)

        filesToOpenSubset_string = ", \n   ".join(filesToOpenSubset)
        logger.info(
            "Subset of the "
            + str(len(filesToOpenSubset))
            + " SVO files from the different subfolders to be opened:\n   "
            + str(filesToOpenSubset_string)
        )
        # SVO can produce a very large number of files including the subset files
        #   when even the subset is greater then 10, open a least the SVO file
        if len(filesToOpenSubset) > 10:
            if package_var == "Stanza" or package_var == "spaCy":
                filesToOpenSubset = [filesToOpen[0]]
                filesToOpenSubset.append(filesToOpen[1])
            else:
                filesToOpenSubset = [filesToOpen[0]]

    return filesToOpen
