import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def MALLET_heatmap(composition_file, topics_file, outputDir, fig_set=None, show_topics=True):
    if fig_set is None:
        fig_set = {"figure.figsize": (8, 6), "figure.dpi": 300}
    try:
        topics = pd.read_csv(
            topics_file,
            names=["Topic", "Weight", "Keys"],
            encoding="utf-8",
            on_bad_lines="skip",
        )
    except Exception:
        topics = pd.read_csv(
            topics_file,
            names=["Topic", "Weight", "Keys"],
            encoding="ISO-8859-1",
            on_bad_lines="skip",
        )

    composition_names = ["Document ID", "Document"]
    for topic_num in range(1, len(topics.index) + 1):
        composition_names.append(f"Topic {topic_num}")
    composition = pd.read_csv(composition_file, names=composition_names, encoding="utf-8", on_bad_lines="skip")

    for index, row in composition.iterrows():
        try:
            int(row["Document ID"])
        except Exception:
            composition.drop(index=index, inplace=True)

    composition.drop(["Document ID"], axis=1, inplace=True)
    composition.reset_index(drop=True, inplace=True)

    document_titles = composition["Document"]

    sns.set_theme(style="whitegrid", rc=fig_set)

    sns.heatmap(
        composition.iloc[:, 1:].map(float),
        vmin=0,
        vmax=1,
        annot=True,
        yticklabels=document_titles,
        fmt="0.2f",
        annot_kws={"size": 8},
    )
    plt.suptitle("Topic Composition and Keys", fontsize=18)

    if show_topics:
        size = plt.gcf().get_size_inches()
        topic_num = 1
        for keys in topics["Keys"]:
            plt.text(
                min(size) - max(size),
                max(size) + (topic_num * 0.25),
                f"Topic {topic_num}: {keys}",
                ha="left",
                va="bottom",
            )
            topic_num += 1

    outputFilename = os.path.join(outputDir, "MALLET_topics.png")
    plt.savefig(outputFilename, bbox_inches="tight")
    return outputFilename
