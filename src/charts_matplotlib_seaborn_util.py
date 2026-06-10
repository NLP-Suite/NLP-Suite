# Written by Adrian Valencia in Nov 2023; edited it March 2024

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "charts_matplotlib_seaborn_util",
                                                 ['os', 'pandas', 'seaborn', 'matplotlib']) == False:
    sys.exit(0)

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def MALLET_heatmap(composition_file, topics_file, outputDir, fig_set={"figure.figsize": (8, 6), "figure.dpi": 300},
                   show_topics=True):
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

    try:
        topics = pd.read_csv(topics_file, encoding='utf-8', on_bad_lines='skip')
    except:
        topics = pd.read_csv(topics_file, encoding="ISO-8859-1", on_bad_lines='skip')
    topics.columns = ["Topic", "Weight", "Keys"]

    try:
        composition = pd.read_csv(composition_file, encoding='utf-8', on_bad_lines='skip')
    except:
        composition = pd.read_csv(composition_file, encoding="ISO-8859-1", on_bad_lines='skip')
    num_topics = len(composition.columns) - 2
    composition.columns = ["Document ID", "Document"] + [f"Topic {i}" for i in range(1, num_topics + 1)]

    composition.drop(["Document ID"], axis=1, inplace=True)
    composition.reset_index(drop=True, inplace=True)

    composition["Document"] = composition["Document"].apply(
        lambda d: os.path.split(d.replace('file:' + os.sep, ''))[1])

    document_titles = composition["Document"]  # Clean hyperlinks function here

    sns.set(rc=fig_set)  # Set figure dimensions and resolution

    heatmap = sns.heatmap(composition.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').fillna(0),
                          vmin=0, vmax=1,  # Range 0-1
                          annot=True,  # Display values inside heatmap
                          yticklabels=document_titles,  # Document name labels
                          fmt='0.2f',  # Rounding
                          annot_kws={"size": 8})
    plt.suptitle("Topic Composition and Keys", fontsize=18)  # Title

    # Add topics labels to heatmap x-axis
    # if show_topics:
    #     size = plt.gcf().get_size_inches()  # Figure dimensions to align topics under chart
    #     topic_num = 1
    #     for keys in topics["Keys"]:
    #         plt.text(-size[0] * 0.4,  # adjust for left indent
    #                  -size[1] * 0.25 - topic_num * 0.5,  # adjust for vertical position
    #                  f"Topic {topic_num}: {keys}",
    #                  ha="left", va="top", fontsize=8)  # change fontsize
    #         topic_num += 1

    if show_topics:
        size = plt.gcf().get_size_inches()  # Figure dimensions to align topics under chart
        topic_num = 1
        for keys in topics["Keys"]:
            plt.text(min(size) - max(size),  # Left indent
                     max(size) + (topic_num * 0.25),  # 0.25 spacing between topics
                     f"Topic {topic_num}: {keys}",  # Naming topics on x-axis
                     ha="left", va="bottom")  # Align text on left
            topic_num += 1

    outputFilename = os.path.join(outputDir, "MALLET_topics.png")
    plt.savefig(outputFilename, bbox_inches="tight")
    plt.close()
    return outputFilename

# seaborn
# https://seaborn.pydata.org/examples/different_scatter_variables.html