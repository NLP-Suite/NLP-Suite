# file_manager_service.py
from __future__ import annotations

import csv
import logging
import os

import file_filename_util

logger = logging.getLogger(__name__)


def run_file_manager(
    inputDir,
    outputDir,
    chartPackage,
    dataTransformation,
    selectedCsvFile_var,
    selectedCsvFile_colName,
    utf8_var,
    ASCII_var,
    list_var,
    rename_var,
    copy_var,
    move_var,
    delete_var,
    count_file_manager_var,
    split_var,
    rename_new_entry,
    by_file_type_var,
    file_type_menu_var,
    by_creation_date_var,
    by_author_var,
    before_date_var,
    after_date_var,
    by_prefix_var,
    by_substring_var,
    string_entry_var,
    by_foldername_var,
    folder_character_separator_var,
    by_embedded_items_var,
    comparison_var,
    number_of_items_var,
    embedded_item_character_value_var,
    include_exclude_var,
    character_count_file_manager_var,
    character_entry_var,
    include_subdir_var,
    fileName_embeds_date,
    date_format,
    date_separator,
    date_position,
):
    # if inputDir == outputDir and list_var ==False:
    # Frontend Implementation

    """List, rename, copy, move, delete, or split corpus files per the selected options."""
    filesToOpen = []
    fileList = []

    outputFilename = ""
    options = 0
    i = 0
    msg = ""
    operation = ""
    fieldnames = []
    currentSubfolder = os.path.basename(os.path.normpath(inputDir))
    hasFullPath = False

    # if utf8_var==1 or ASCII_var==1:
    #     mb.showwarning(title='Option not available',
    #                    message='The utf-8 and ASCII options are not available yet.\n\nSorry!')

    if list_var:
        options = options + 1
        operation = "listed"
        outputFilename = "List_files_" + currentSubfolder + ".csv"
    if rename_var:
        options = options + 1
        operation = "renamed"
        outputFilename = "List_renamed_files_" + currentSubfolder + ".csv"
    if copy_var:
        options = options + 1
        operation = "copied"
        outputFilename = "List_copied_files_" + currentSubfolder + ".csv"
    if move_var:
        options = options + 1
        operation = "moved"
        outputFilename = "List_moved_files_" + currentSubfolder + ".csv"
    if delete_var:
        options = options + 1
        operation = "deleted"
        outputFilename = "List_deleted_files_" + currentSubfolder + ".csv"
        # if command==False:
        # Frontend Implementation
    if count_file_manager_var:
        i = 1
        options = options + 1
        operation = "counted"
        outputFilename = "Count_files_" + currentSubfolder + ".csv"

    if split_var:
        i = 1
        options = options + 1
        operation = "split"
        outputFilename = "split_files_" + currentSubfolder + ".csv"

    if options == 0:
        logger.info(
            "No file manager option has been selected.\n\nPlease, select one option (list, rename, copy, move, delete, count, split) and try again."
        )
        return

    if options == 1:
        if count_file_manager_var:
            if not list_var and not by_file_type_var and not by_prefix_var and not by_substring_var:
                logger.info(
                    "You have selected a file manager option, but no specific criteria for managing the files: By file type, By prefix value, or By substring value.\n\nPlease, select the file criteria to use and try again."
                )
                return

    if options > 1:
        logger.info(
            "Only one option at a time can be selected. You have selected "
            + str(options)
            + " options.\n\nPlease, deselect some options and try again."
        )
        return

    if by_embedded_items_var:
        if embedded_item_character_value_var == "":
            logger.info(
                "You have selected the option 'By number of embedded items' but you have not entered the 'Separator character(s)'.\n\nPlease, enter the character(s) and try again."
            )
            return

    # -------------------------------------------------------------------------------------------------
    # setup the field names of the output csv file
    fieldnames = ["File_Name", "Path_To_File", "File_Name_With_Path", "File_Type"]

    if by_creation_date_var:
        # if file_type_menu_var!='' and file_type_menu_var!='doc' and by_file_type_var!='docx':
        # frontend implementation
        fieldnames = fieldnames + ["Creation_date", "Modification_date"]

    if by_author_var:
        # if file_type_menu_var!='' and file_type_menu_var!='doc' and by_file_type_var!='docx':
        # frontend implementation
        fieldnames = fieldnames + ["Author"]

    if by_embedded_items_var:
        if number_of_items_var > 0:
            fieldnames = fieldnames + ["Embedded items count (" + embedded_item_character_value_var + ")"]
            fieldnames = fieldnames + ["Count by document"]
    if fileName_embeds_date:
        fieldnames = fieldnames + ["Date"]

    if character_count_file_manager_var:
        fieldnames = fieldnames + ["Character count (" + character_entry_var + ")"]

    if split_var:
        first_filename = None
        for _root, _subdirs, files in os.walk(inputDir):
            if files:
                first_filename = files[0]
                break

        if not first_filename:
            logger.info("No files found for split operation.")
            return

        filename_items = first_filename.split(embedded_item_character_value_var)
        ID = 1
        for _item in filename_items:
            fieldnames = fieldnames + ["Split item" + str(ID)]
            ID = ID + 1

    # _________________________________________________________________________________________________________________________________________________

    if list_var:
        # extract the last subfolder of the path to be displayed as part of the output filename
        os.path.basename(os.path.normpath(inputDir))

    if count_file_manager_var:
        i = file_filename_util.get_count(inputDir, outputDir, outputFilename)
    else:
        with open(outputDir + os.sep + outputFilename, "w", errors="ignore", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()

    if rename_var:
        # You can in fact have a blank entry
        # if rename_new_entry=='' and string_entry_var=='':
        # if rename_new_entry=='':
        if not by_prefix_var and not by_substring_var and not by_foldername_var and not by_embedded_items_var:
            logger.info(
                "You have selected the option to Rename files but you have not selected any of the available options for renaming the files.\n\nPlease, make a selection and enter the appropriate values and try again."
            )
            return
        if (by_prefix_var or by_substring_var) and string_entry_var == "":
            logger.info(
                "You have selected the option to Rename files by prefix/sub-string value but you have not entered the values necessary for renaming the filename.\n\nPlease, enter the missing values in the fields 'Enter value' and/or 'New renaming value' and try again."
            )
            return
        if by_foldername_var and folder_character_separator_var == "":
            logger.info(
                "You have selected the option to Rename files by Folder name but you have not entered the Separator character(s).\n\nPlease, enter appropriate values in the 'Separator character(s)' field and try again."
            )
            return

    if len(file_type_menu_var) > 0:
        msg = 'of type "' + file_type_menu_var + '" '

    if by_prefix_var and by_substring_var:
        logger.info(
            'Only one option at a time, "By prefix value" or "By sub-string value," can be selected.\n\nPlease, deselect one option and try again.'
        )
        return

    if by_prefix_var:
        if len(string_entry_var) == 0:
            logger.info(
                'You have selected the option "By prefix value" but no string value has been entered.\n\nPlease, enter the prefix value in the "Enter value" field and try again.'
            )
            return
        if len(msg) > 0:
            msg = msg + ' and with string prefix "' + string_entry_var + '" '
        else:
            msg = 'with string prefix "' + string_entry_var + '" '

    if by_substring_var == 1:
        if len(string_entry_var) == 0:
            logger.info(
                'You have selected the option "By sub-string value" but no string value has been entered.\n\nPlease, enter the sub-string value in the "Enter value" field and try again.'
            )
            return
        if len(msg) > 0:
            msg = msg + ' and containing the substring "' + string_entry_var + '" '
        else:
            msg = 'containing the substring "' + string_entry_var + '" '

    # For cases where matching files beginning with a dot (.); like files in the current directory or hidden files on Unix based system, use the os.walk
    # include_subdir_var
    # for filename in glob.iglob(inputDir + os.sep+ '*.'+by_file_type_var, recursive=True):

    # root: Current path which is "walked through"
    # subdirs: Files in root of type directory
    # files: Files in current root (not in subdirs) of type other than directory

    # must handle the case in which we use a csv file
    # _________________________________________________________________________________________________________________________________________________

    # implemented noHeaders and headers here as it was in GUI section
    # no need!!
    # if selectedCsvFile_var != '':
    #     if headers_result == '':

    #     if noHeaders==False:
    #         # No headers, we assume the first column

    # if there are variables declared in frontend, just take them from frontend

    # with open(selectedCsvFile_var, 'r', encoding="utf-8", errors='ignore') as read_obj:
    #     if noHeaders==False:
    #         # skip first row since it has headers
    #     for row in csv_reader:
    #         if row[selectedCsvFile_colNum][:10] == "=hyperlink":
    #         if head != '':

    # _________________________________________________________________________________________________________________________________________________

    # processFile returns: fileFound, characterCount,creation_date,modification_date,author,date, dateStr
    if include_subdir_var == 1:
        for current_dir, _subdirs, files in os.walk(inputDir):
            for filename in files:
                logger.info(f"Processing file: {filename}")
                (
                    fileFound,
                    characterCount,
                    creation_date,
                    modification_date,
                    author,
                    date,
                    dateStr,
                ) = file_filename_util.processFile(
                    current_dir,
                    outputDir,
                    filename,
                    outputFilename,
                    fieldnames,
                    selectedCsvFile_var,
                    hasFullPath,
                    utf8_var,
                    ASCII_var,
                    list_var,
                    rename_var,
                    copy_var,
                    move_var,
                    delete_var,
                    split_var,
                    rename_new_entry,
                    file_type_menu_var,
                    by_creation_date_var,
                    by_author_var,
                    by_prefix_var,
                    by_substring_var,
                    string_entry_var,
                    by_foldername_var,
                    folder_character_separator_var,
                    by_embedded_items_var,
                    comparison_var,
                    number_of_items_var,
                    embedded_item_character_value_var,
                    include_exclude_var,
                    character_count_file_manager_var,
                    character_entry_var,
                    include_subdir_var,
                    fileName_embeds_date,
                    date_format,
                    date_separator,
                    date_position,
                )
                if fileFound:
                    i = i + 1
    else:
        if hasFullPath:  # This is used when full paths are present in the CSV file, we ignore the input directory
            logger.info("Full path present, processing regardless of existence in input directory")
            for filename in fileList:
                (
                    fileFound,
                    characterCount,
                    creation_date,
                    modification_date,
                    author,
                    date,
                    dateStr,
                ) = file_filename_util.processFile(
                    inputDir,
                    outputDir,
                    filename,
                    outputFilename,
                    fieldnames,
                    selectedCsvFile_var,
                    hasFullPath,
                    # utf8_var, ASCII_var,
                    list_var,
                    rename_var,
                    copy_var,
                    move_var,
                    delete_var,
                    split_var,
                    rename_new_entry,
                    file_type_menu_var,
                    by_creation_date_var,
                    by_author_var,
                    by_prefix_var,
                    by_substring_var,
                    string_entry_var,
                    by_foldername_var,
                    folder_character_separator_var,
                    by_embedded_items_var,
                    comparison_var,
                    number_of_items_var,
                    embedded_item_character_value_var,
                    include_exclude_var,
                    character_count_file_manager_var,
                    character_entry_var,
                    include_subdir_var,
                    fileName_embeds_date,
                    date_format,
                    date_separator,
                    date_position,
                )
                if fileFound:
                    i = i + 1
        elif not count_file_manager_var:  # list, copy, move, delete
            for filename in os.listdir(inputDir):
                if not os.path.isdir(os.path.join(inputDir, filename)):
                    logger.info(f"Processing file: {filename}")
                    if selectedCsvFile_var != "":
                        if filename in fileList:
                            processFile = True
                        else:
                            processFile = False
                    else:
                        processFile = True
                    if processFile:
                        (
                            fileFound,
                            characterCount,
                            creation_date,
                            modification_date,
                            author,
                            date,
                            dateStr,
                        ) = file_filename_util.processFile(
                            inputDir,
                            outputDir,
                            filename,
                            outputFilename,
                            fieldnames,
                            selectedCsvFile_var,
                            hasFullPath,
                            utf8_var,
                            ASCII_var,
                            list_var,
                            rename_var,
                            copy_var,
                            move_var,
                            delete_var,
                            split_var,
                            rename_new_entry,
                            file_type_menu_var,
                            by_creation_date_var,
                            by_author_var,
                            by_prefix_var,
                            by_substring_var,
                            string_entry_var,
                            by_foldername_var,
                            folder_character_separator_var,
                            by_embedded_items_var,
                            comparison_var,
                            number_of_items_var,
                            embedded_item_character_value_var,
                            include_exclude_var,
                            character_count_file_manager_var,
                            character_entry_var,
                            include_subdir_var,
                            fileName_embeds_date,
                            date_format,
                            date_separator,
                            date_position,
                        )
                        if fileFound:
                            i = i + 1

    import charts_util

    columns_to_be_plotted_xAxis = []
    columns_to_be_plotted_yAxis = ["File_Type"]
    outputFiles = charts_util.visualize_chart(
        chartPackage,
        dataTransformation,
        outputDir + os.sep + outputFilename,
        outputDir,
        columns_to_be_plotted_xAxis,
        columns_to_be_plotted_yAxis,
        chart_title="Frequency Distribution of File Types",
        outputFileNameType="File_Types",
        column_xAxis_label="File type",
        count_var=1,
        hover_label=[],
        groupByList=[],
        plotList=["Frequency"],
        chart_title_label="",
    )
    if outputFiles:
        filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

    if i > 0:
        if rename_var == 1:
            logger.info(
                str(i)
                + " files "
                + msg
                + operation
                + ".\n\n"
                + operation
                + " files have been renamed in the input directory "
                + inputDir
                + "."
            )
        elif copy_var == 1:
            logger.info(
                str(i)
                + " files "
                + msg
                + operation
                + ".\n\n"
                + operation
                + " files have been saved in the output directory "
                + outputDir
                + "."
            )
        else:
            logger.info(str(i) + " files " + msg + operation + ".")
            filesToOpen.append(os.path.join(outputDir, outputFilename))
    else:
        logger.info(
            "No files "
            + msg
            + operation
            + '.\n\nPlease, check the following information:\n  1. INPUT files directory;\n  2. selected file type (if you ticked the By file type option);\n  3. Include subdirectory option;\n  4. the correct "Number of items" when you are using the option "By number of embedded items".'
        )
