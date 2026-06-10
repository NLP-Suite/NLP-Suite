import pandas as pd
from collections import Counter
import CoNLL_util


def compute_word_class_frequencies(inputFilename, outputDir, data, all_CoNLL_records, openOutputFiles, chartPackage,
                                   dataTransformation):
    # Define POS tag categories
    content_words = {
        "Nouns": ['NN', 'NNS', 'NNP', 'NNPS'],
        "Verbs": ['VB', 'VBN', 'VBD', 'VBG', 'VBP', 'VBZ'],
        "Adjectives": ['JJ', 'JJR', 'JJS'],
        "Adverbs": ['RB', 'RBR', 'RBS']
    }

    junk_words = {
        "Pronouns": ['PRP', 'PRP$', 'WP', 'WP$'],
        "Conjunctions": ['CC', 'IN'],
        "Prepositions": ['IN'],
        "Modal Verbs": ['MD'],
        "Auxiliaries": ['aux'],
        "Determinants": ['DT']
    }

    # Read data into DataFrame — data is normalized to canonical column order
    column_count = len(data[0])
    if column_count == 14:
        column_names = CoNLL_util.CANONICAL_COLUMNS + ["Year"]
    else:
        column_names = list(CoNLL_util.CANONICAL_COLUMNS)

    df = pd.DataFrame(data, columns=column_names)

    # Ensure POS column exists
    if "POS" not in df.columns:
        raise ValueError("Missing POS column in the CoNLL data")

    # Count total words in the document
    total_words = len(df)

    # Compute frequencies for each class
    pos_counts = Counter(df["POS"])
    deprel_counts = Counter(df["DepRel"])

    # Compute frequencies for content and junk words
    content_frequencies = {category: sum(pos_counts[tag] for tag in tags if tag in pos_counts) for category, tags in
                           content_words.items()}
    junk_frequencies = {category: sum(pos_counts[tag] for tag in tags if tag in pos_counts) for category, tags in
                        junk_words.items()}

    # Include DepRel 'aux' in junk words
    junk_frequencies["Auxiliaries"] = deprel_counts.get("aux", 0)

    # Compute total content and junk words
    total_content_words = sum(content_frequencies.values())
    total_junk_words = sum(junk_frequencies.values())

    # Compute ratios
    content_ratios = {category: freq / total_content_words if total_content_words > 0 else 0 for category, freq in
                      content_frequencies.items()}
    junk_ratios = {category: freq / total_junk_words if total_junk_words > 0 else 0 for category, freq in
                   junk_frequencies.items()}

    overall_ratios = {
        "Total Content Words Ratio": total_content_words / total_words if total_words > 0 else 0,
        "Total Junk Words Ratio": total_junk_words / total_words if total_words > 0 else 0
    }

    # Create a summary DataFrame
    summary_data = {
        "Category": list(content_frequencies.keys()) + ["Total Content Words"] + list(junk_frequencies.keys()) + [
            "Total Junk Words"],
        "Frequency": list(content_frequencies.values()) + [total_content_words] + list(junk_frequencies.values()) + [
            total_junk_words],
        "Ratio to Class": list(content_ratios.values()) + [1.0] + list(junk_ratios.values()) + [1.0],
        "Ratio to Total Words": [freq / total_words if total_words > 0 else 0 for freq in
                                 list(content_frequencies.values())] +
                                [overall_ratios["Total Content Words Ratio"]] +
                                [freq / total_words if total_words > 0 else 0 for freq in
                                 list(junk_frequencies.values())] +
                                [overall_ratios["Total Junk Words Ratio"]]
    }

    summary_df = pd.DataFrame(summary_data)

    # Define output filename
    output_filename = f"{outputDir}/word_class_frequencies.csv"

    # Save output to a CSV file
    summary_df.to_csv(output_filename, index=False)
    # Return the file path instead of the DataFrame
    return [output_filename]

