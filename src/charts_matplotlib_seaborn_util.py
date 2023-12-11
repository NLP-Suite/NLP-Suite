# Written by Adrian Valencia in Nov 2023

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"charts_matplotlib_seaborn_util",['os','pandas','seaborn','matplotlib'])==False:
    sys.exit(0)

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def MALLET_heatmap(composition_file, topics_file, outputDir, fig_set={"figure.figsize": (8, 6), "figure.dpi": 300},
                   show_topics=True, exclude_empty_keys=True, empty_keys=" "):
    """
    Uses Seaborn to create a heatmap of topics generated using MALLET topic modeling

    Args:
        composition_file r(str): File name and directory of MALLET topic composition file. Usually NLP-MALLET_Output_Keys.csv.
        topics_file r(str): File name and directory of MALLET topic keys file. Usually NLP-MALLET_Output_Composition.csv.
        fig_set{} (rcParams): Matplotlib figure size parameters. 8in by 6in at 300 DPI by default. Warning: changing dimension values could impact readability of topics.
        show_topics (bool): Controls if topic keys should be displayed under heatmap. True by default. Useful to set as false when using many topics.

    Returns:
        heatmap (object): Seaborn heatmap plot object.
    """

    # Try-except for encoding error with scientific notation
    try:
        topics = pd.read_csv(topics_file, names=["Topic", "Weight", "Keys"], encoding='utf-8',
                             on_bad_lines='skip')  # Topic keys file
    except:
        topics = pd.read_csv(topics_file, names=["Topic", "Weight", "Keys"], encoding="ISO-8859-1",
                             on_bad_lines='skip')  # Topic keys file

    # Add column names to topic composition file before reading
    composition_names = ["Document ID", "Document"]
    for topic_num in range(1, len(topics.index) + 1):
        composition_names.append(f"Topic {topic_num}")
    composition = pd.read_csv(composition_file, names=composition_names, encoding='utf-8', on_bad_lines='skip')
    composition.drop(["Document ID"], axis=1, inplace=True)  # Drop ID, DataFrames are already indexed

    document_titles = composition["Document"].apply(
        lambda x: os.path.split(x)[1].split('_')[0][:10] + "...")  # Clean hyperlinks function here

    sns.set(rc=fig_set)  # Set figure dimensions and resolution

    data = composition.iloc[:, 1:].round(2)
    if exclude_empty_keys:
        print(data.size)
        data = data.loc[:, (data != 0).any(axis=0)]
        print(data.size)

    heatmap = sns.heatmap(data,  # Select all columns excluding index column
                          vmin=0, vmax=1,  # Range 0-1
                          annot=True,  # Display values inside heatmap
                          yticklabels=document_titles,  # Document name labels
                          annot_kws={"size": 8})
    plt.suptitle("Topic Weight Distribution by Document", fontsize=18)  # Title

    # Add topics labels to heatmap x-axis
    if show_topics:
        size = plt.gcf().get_size_inches()  # Figure dimensions to align topics under chart
        topic_num = 1
        for keys in topics["Keys"]:
            keys_topics = keys
            if type(keys) is float:  # Check for empty keys
                keys_topics = empty_keys
            plt.text(min(size) - max(size),  # Left indent. Fixed due to trimming of document names
                     max(size) + (topic_num * 0.25) + 0.1,  # 0.25 spacing between topics
                     f"Topic {topic_num}: {keys_topics}",  # Naming topics on x-axis
                     ha="left", va="bottom")  # Align text on left

            topic_num += 1
    print(f"{topic_num - 1}  height : {len(data.index)}")
    print(f"ratio: {(topic_num - 1) / len(data.index)}")
    outputFilename = outputDir + os.sep + "MALLET_topics.png"
    plt.savefig(outputFilename, bbox_inches="tight")
    # should return the saved filename
    return outputFilename  # heatmap

#
# # Example:
#
# t = r"NLP-MALLET_Output_Keys_1.csv"
# c = r"NLP-MALLET_Output_Composition_1.csv"
#
# MALLET_heatmap(c, t, r"C:\Users\Adrian Valencia\Desktop", {"figure.figsize": (8, 6), "figure.dpi": 300}, True,
#                exclude_empty_keys=True)
# seaborn
# https://seaborn.pydata.org/examples/different_scatter_variables.html