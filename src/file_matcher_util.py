import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_Python_packages(GUI_util.window, "file_matcher_util", ['os', 'pathlib']):
    sys.exit(0)

import os
from pathlib import Path
from tkinter import messagebox as mb

import IO_files_util
import IO_csv_util

def get_group_name(stem, separator, number_of_items):
    split_items = stem.split(separator)
    group = ""
    # Add to the group the requested number of items, each separated by the requested separator
    for i in range(number_of_items):
        group = group + split_items[i]
        group = group + separator
    # Trim the last hanging separator
    return group[:-1]

def clean_partial_output(output_list, separator, number_of_items):
    # Clean Column A for partial outputs:
    for row in range(1, len(output_list)):
        # Take the contents of Column A and strip off the extension and only show the number of items requested.
        # Column A currently holds a file name, we need to remove the extension using splitext,
        # then we can use the get_group_name func.
        stem = os.path.splitext(output_list[row][0])[0]
        group_name = get_group_name(stem, separator, number_of_items)
        # Re-write output row with groupname in column A, all other data unchanged
        output_list[row] = [group_name] + output_list[row][1:]

    return output_list

def run_default(window, in_search_path, outputDir, csv_file, openOutputFiles, partial_match, in_ext_1, in_ext_2,
                copy_var, move_var, separator, number_of_items):
    partial_match = partial_match == 0
    star_search = in_ext_1 == '*'

    # Each row in this 2D array contains info about a matched file
    matched_output = []
    # Unmatched files are those which we could not find counterparts of another filetype
    unmatched_output = []
    # Exact duplicate files same name and original extension
    duplicates_output = []
    filesToOpen = []

    matched_output.append(['File_Name', 'Extension', 'File_Name_With_Path', 'Folder', 'Path_To_File', 'Start_Folder'])
    unmatched_output.append(['File_Name', 'Extension', 'File_Name_With_Path', 'Folder', 'Path_To_File', 'Start_Folder'])
    duplicates_output.append(['File_Name', 'Extension', 'File_Name_With_Path', 'Folder', 'Path_To_File', 'Start_Folder'])

    # Dictionary to store all found files in the directory given.
    # Groups based on stem
    # Partial matches requires going through files_found, filtering results by desired # of items, and placing those items in groups with each other
    files_found = {}
    file_groups = {}

    # path = /home/brett/Downloads/Lynching/data_Simplex.xlsx
    # path.name = data_Simplex.xlsx
    # path.stem = data_Simplex
    # path.suffix = .xlsx
    # path.parent = /home/brett/Downloads/Lynching/

    # Search the target directory for ALL files (any type)
    # Force all suffix to be stored as lowercase
    num_files_count = 0
    folder_set = set()
    for path in Path(in_search_path[0]).rglob('*.*'):
        num_files_count += 1
        folder_set.add(path.parent)

    num_folders_count = len(folder_set)
    folder_set = set()
    file_num = 1
    folder_num = 1
    for path in Path(in_search_path[0]).rglob('*.*'):
        folder_set.add(path.parent)
        print("Processing folder ", len(folder_set), "/", num_folders_count, os.path.split(path.parent)[1])
        print("    Processing file ", file_num, "/", num_files_count, path.name)
        file_num += 1
        if path.stem in files_found:
            # This stem exists in files_found, check if this specific stem's extension also exists in the dict
            if path.suffix.lower() in files_found[path.stem]:
                # stem and suffix exist in the dictionary, add this file to the list
                files_found[path.stem][path.suffix.lower()].append(path)
            else:
                # This is a new suffix for the given stem, create a list for this entry
                files_found[path.stem][path.suffix.lower()] = [path]
        else:
            # Stem not yet in the files_found dictionary, add it and the suffix to the dict
            files_found[path.stem] = {}
            files_found[path.stem][path.suffix.lower()] = [path]

    # If we want to search for partial match/unmatch we must use the file_groups dictionary
    if partial_match:
        # Filter files by # of items
        for stem in files_found:
            if len(stem.split(separator)) >= number_of_items:
                # file_groups takes the first n items of the stem as the group name
                head = get_group_name(stem, separator, number_of_items)
                if head in file_groups:
                    # The group already exists, add suffix and paths to this group
                    for suffix in files_found[stem]:
                        if suffix in file_groups[head]:
                            file_groups[head][suffix] = file_groups[head][suffix] + files_found[stem][suffix]
                        else:
                            file_groups[head][suffix] = files_found[stem][suffix]
                else:
                    # The group does not yet exist, create it with suffix and paths from current file
                    file_groups[head] = {}
                    for suffix in files_found[stem]:
                        file_groups[head][suffix] = files_found[stem][suffix]
        target_dict = file_groups
    else:
        target_dict = files_found

    # Find duplicates
    # Duplicates can be detected when the length of a given target_dict[stem][suffix] list is > 1
    # This means there is more than one file with the same exact name and suffix.
    for stem in target_dict:
        for suffix in target_dict[stem]:
            if len(target_dict[stem][suffix]) > 1:
                for path in target_dict[stem][suffix]:
                    if path.match('*.' + in_ext_1):
                        # Only add the duplicates with if the suffix matches our search suffix
                        extension = os.path.splitext(path.name)[1]
                        folder = os.path.basename(os.path.normpath(path.parent))
                        duplicates_output.append([path.name, extension,
                                                  IO_csv_util.dressFilenameForCSVHyperlink(path),
                                                  folder,
                                                  IO_csv_util.dressFilenameForCSVHyperlink(path.parent),
                                                  IO_csv_util.dressFilenameForCSVHyperlink(in_search_path[0])])

    # Matched values are those that have more than one suffix for a given stem
    for stem in target_dict:
        if len(target_dict[stem]) > 1:
            if star_search:
                for suffix in target_dict[stem]:
                    for path in target_dict[stem][suffix]:
                        if path.match('*.' + in_ext_2):
                            extension = os.path.splitext(path.name)[1]
                            folder = os.path.basename(os.path.normpath(path.parent))
                            matched_output.append([path.name, extension,
                                                   IO_csv_util.dressFilenameForCSVHyperlink(path),
                                                   folder,
                                                   IO_csv_util.dressFilenameForCSVHyperlink(path.parent),
                                                   IO_csv_util.dressFilenameForCSVHyperlink(in_search_path[0])])
            else:
                # Since this is not a search from '*', we want to detect files of in_ext_1 and find matches that are of in_ext_2
                if '.' + in_ext_1 in target_dict[stem]:
                    # suffix of the desired type exists, add all in_ext_2 files to output
                    for suffix in target_dict[stem]:
                        for path in target_dict[stem][suffix]:
                            if path.match('*.' + in_ext_2):
                                # Should we remove any files that =in_ext_1?
                                extension = os.path.splitext(path.name)[1]
                                folder = os.path.basename(os.path.normpath(path.parent))
                                matched_output.append([path.name, extension,
                                                       IO_csv_util.dressFilenameForCSVHyperlink(path),
                                                       folder,
                                                       IO_csv_util.dressFilenameForCSVHyperlink(path.parent),
                                                       IO_csv_util.dressFilenameForCSVHyperlink(in_search_path[0])])

    # Unmatched values are those that only have one suffix for a given stem
    for stem in target_dict:
        if len(target_dict[stem]) == 1:
            for suffix in target_dict[stem]:
                for path in target_dict[stem][suffix]:
                    if path.match('*.' + in_ext_1):
                        extension = os.path.splitext(path.name)[1]
                        folder = os.path.basename(os.path.normpath(path.parent))
                        unmatched_output.append([path.name, extension,
                                                 IO_csv_util.dressFilenameForCSVHyperlink(path),
                                                 folder,
                                                 IO_csv_util.dressFilenameForCSVHyperlink(path.parent),
                                                 IO_csv_util.dressFilenameForCSVHyperlink(in_search_path[0])])

    # Clean Column A for partial outputs:
    if partial_match:
        clean_partial_output(matched_output, separator, number_of_items)
        clean_partial_output(unmatched_output, separator, number_of_items)
        clean_partial_output(duplicates_output, separator, number_of_items)

    start_type = "star" if in_ext_1 == '*' else in_ext_1
    end_type = "star" if in_ext_2 == '*' else in_ext_2

    matched_filename= in_search_path[0] + os.sep + os.path.basename(os.path.normpath(in_search_path[0])) + "_matched_" + start_type + "_" + end_type + ".csv"
    unmatched_filename= in_search_path[0] + os.sep + os.path.basename(os.path.normpath(in_search_path[0])) + "_unmatched_" + start_type + "_" + end_type + ".csv"
    duplicates_filename= in_search_path[0] + os.sep + os.path.basename(os.path.normpath(in_search_path[0])) + "_duplicates_" + start_type + "_" + end_type + ".csv"

    IO_csv_util.list_to_csv(0, matched_output, matched_filename, colnum=0)
    IO_csv_util.list_to_csv(0, unmatched_output, unmatched_filename, colnum=0)
    IO_csv_util.list_to_csv(0, duplicates_output, duplicates_filename, colnum=0)

    mb.showwarning(title='OUTPUT folder',message='For easiness of reading, regardless of your selected OUTPUT folder in I/O Configuration, all three output files for matched, unmatched, and duplicate files have been saved to the INPUT folder\n\n' + str(in_search_path[0]))

    if openOutputFiles == True:
        filesToOpen.append(matched_filename)
        filesToOpen.append(unmatched_filename)
        filesToOpen.append(duplicates_filename)
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)
