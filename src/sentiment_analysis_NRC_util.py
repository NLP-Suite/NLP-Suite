import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "sentiment_analysis_NRC", ['os', 'csv', 'tkinter', 'nrclex', 'numpy', 'matplotlib']) == False:
    sys.exit(0)

import os
import csv
import time
import numpy as np
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba
from nrclex import NRCLex
from collections import defaultdict
import math

import GUI_IO_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
import charts_util

from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text

EIGHT_EMOTIONS = ["anger", "anticipation", "disgust", "fear",
                   "joy", "sadness", "surprise", "trust"]

NRC_COLORS = {
    "joy":          "#F9CB42",
    "trust":        "#639922",
    "fear":         "#1D9E75",
    "surprise":     "#378ADD",
    "sadness":      "#534AB7",
    "disgust":      "#D4537E",
    "anger":        "#E24B4A",
    "anticipation": "#BA7517",
}

# Plutchik intensity data
PLUTCHIK_EMOTIONS = [
    {"name": "Joy",          "mild": "Serenity",      "intense": "Ecstasy",    "opposite": "Sadness",      "color": "#F9CB42", "angle": 90},
    {"name": "Trust",        "mild": "Acceptance",    "intense": "Admiration",  "opposite": "Disgust",      "color": "#639922", "angle": 45},
    {"name": "Fear",         "mild": "Apprehension",  "intense": "Terror",      "opposite": "Anger",        "color": "#1D9E75", "angle": 0},
    {"name": "Surprise",     "mild": "Distraction",   "intense": "Amazement",   "opposite": "Anticipation", "color": "#378ADD", "angle": -45},
    {"name": "Sadness",      "mild": "Pensiveness",   "intense": "Grief",       "opposite": "Joy",          "color": "#534AB7", "angle": -90},
    {"name": "Disgust",      "mild": "Boredom",       "intense": "Loathing",    "opposite": "Trust",        "color": "#D4537E", "angle": -135},
    {"name": "Anger",        "mild": "Annoyance",     "intense": "Rage",        "opposite": "Fear",         "color": "#E24B4A", "angle": 180},
    {"name": "Anticipation", "mild": "Interest",      "intense": "Vigilance",   "opposite": "Surprise",     "color": "#BA7517", "angle": 135},
]

INTENSITY_LEVELS = {
    "mild":    (0.35, 0.60),
    "basic":   (0.60, 0.85),
    "intense": (0.85, 1.00),
}


def score_sentence(text):
    emotion_obj = NRCLex(text)
    raw = emotion_obj.raw_emotion_scores
    total = sum(raw.get(e, 0) for e in EIGHT_EMOTIONS) or 1
    return {e: raw.get(e, 0) / total for e in EIGHT_EMOTIONS}


def dominant_emotion(scores):
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "neutral"
    return best


def classify_intensity(score):
    if score >= 0.3:
        return "intense"
    elif score >= 0.1:
        return "basic"
    else:
        return "mild"


def plot_nrc_radar(scores, title, outputFilename):
    emotions = EIGHT_EMOTIONS
    values = [scores.get(e, 0) for e in emotions]
    values += values[:1]

    angles = np.linspace(0, 2 * np.pi, len(emotions), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(30)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], size=8, color="grey")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([e.capitalize() for e in emotions], size=11)

    ax.plot(angles, values, "o-", linewidth=2, color="#378ADD")
    ax.fill(angles, values, alpha=0.25, color="#378ADD")

    ax.set_title(title, size=14, pad=20)
    patches = [mpatches.Patch(color=NRC_COLORS[e], label=e.capitalize()) for e in emotions]
    ax.legend(handles=patches, loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=9)

    plt.tight_layout()
    plt.savefig(outputFilename, dpi=150, bbox_inches="tight")
    plt.close()
    return outputFilename


def plot_plutchik_wheel(scores, title, outputFilename):
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    max_r = 1.0
    n = len(PLUTCHIK_EMOTIONS)
    width = (2 * math.pi) / n

    shades = {"intense": 1.00, "basic": 0.72, "mild": 0.45}

    for e in PLUTCHIK_EMOTIONS:
        theta_center = math.radians(e["angle"])
        base_color = np.array(to_rgba(e["color"]))
        emotion_name = e["name"].lower()
        emotion_score = scores.get(emotion_name, 0)
        intensity = classify_intensity(emotion_score)

        for level, (r_in, r_out) in INTENSITY_LEVELS.items():
            shade = shades[level]
            alpha = 1.0
            if level == "intense" and intensity != "intense":
                alpha = 0.2
            elif level == "basic" and intensity == "mild":
                alpha = 0.3

            color = tuple(base_color[:3] * shade) + (alpha,)
            ax.bar(theta_center, r_out - r_in, width=width - 0.02,
                   bottom=r_in, color=color, edgecolor="white",
                   linewidth=0.8, align="center")

            r_mid = (r_in + r_out) / 2
            label_map = {"mild": e["mild"], "basic": e["name"], "intense": e["intense"]}
            lbl = label_map[level]
            text_alpha = 1.0 if alpha > 0.5 else 0.4
            ax.text(theta_center, r_mid, lbl, ha="center", va="center",
                    fontsize=6.5 if level != "basic" else 7.5,
                    fontweight="bold" if level == "basic" else "normal",
                    color=(0, 0, 0, text_alpha))

        if emotion_score > 0:
            ax.text(theta_center, 1.08, f"{emotion_score:.0%}",
                    ha="center", va="center", fontsize=8,
                    fontweight="bold", color=e["color"])

    ax.set_ylim(0, 1.15)
    fig.suptitle(title, fontsize=14, y=0.97)

    plt.tight_layout()
    plt.savefig(outputFilename, dpi=150, bbox_inches="tight")
    plt.close()
    return outputFilename


def analyzefile(inputFilename, outputDir, writer, Document_ID, Document):
    with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as f:
        fulltext = f.read()

    if len(fulltext) < 1:
        mb.showerror(title='File empty',
                     message='The file ' + inputFilename + ' is empty.\n\nPlease, use another file and try again.')
        return

    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

    for i, s in enumerate(sentences, 1):
        scores = score_sentence(s)
        dom = dominant_emotion(scores)

        row = {'Sentence ID': i, 'Sentence': s,
               'Dominant emotion': dom,
               'Document ID': Document_ID,
               'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)}
        for e in EIGHT_EMOTIONS:
            row[e.capitalize()] = round(scores[e], 4)

        writer.writerow(row)


def main(inputFilename, inputDir, outputDir, chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='sentiment_NRC', silent=True)
    if outputDir == '':
        return

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'NRC_emotions', '', '', '', '', False, True)

    fieldnames = ['Sentence ID', 'Sentence', 'Dominant emotion'] + \
                 [e.capitalize() for e in EIGHT_EMOTIONS] + \
                 ['Document ID', 'Document']

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if len(inputFilename) > 0:
            if os.path.exists(inputFilename):
                analyzefile(inputFilename, outputDir, writer, 1, inputFilename)
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                return
        elif len(inputDir) > 0:
            if os.path.isdir(inputDir):
                documentID = 0
                for file in sorted(os.listdir(inputDir)):
                    filename = os.path.join(inputDir, file)
                    if filename.endswith(".txt"):
                        documentID += 1
                        analyzefile(filename, outputDir, writer, documentID, filename)
            else:
                print('Input directory "' + inputDir + '" is invalid.')
                return

    filesToOpen.append(outputFilename)

    # aggregate scores across all sentences for the wheel visualizations
    import pandas as pd
    df = pd.read_csv(outputFilename)
    emotion_cols = [e.capitalize() for e in EIGHT_EMOTIONS]
    avg_scores = {e.lower(): df[e].mean() for e in emotion_cols}

    if inputFilename:
        base_name = os.path.basename(inputFilename)[:-4]
    else:
        base_name = os.path.basename(inputDir)

    radar_file = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                          '.png', 'NRC_radar', '', '', '', '', False, True)
    plot_nrc_radar(avg_scores, f"NRC Emotion Wheel — {base_name}", radar_file)
    filesToOpen.append(radar_file)

    plutchik_file = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                             '.png', 'Plutchik_wheel', '', '', '', '', False, True)
    plot_plutchik_wheel(avg_scores, f"Plutchik Emotion Wheel — {base_name}", plutchik_file)
    filesToOpen.append(plutchik_file)

    if chartPackage != 'No charts':
        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilename, outputDir,
                                                   columns_to_be_plotted_xAxis=[],
                                                   columns_to_be_plotted_yAxis=emotion_cols,
                                                   chart_title='NRC Emotion Scores by Sentence',
                                                   count_var=0, hover_label=[],
                                                   outputFileNameType='NRC',
                                                   column_xAxis_label='Sentence ID',
                                                   column_yAxis_label='Emotion Score',
                                                   groupByList=['Document'],
                                                   plotList=emotion_cols,
                                                   chart_title_label='NRC Emotion Scores')
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen
