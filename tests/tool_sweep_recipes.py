"""What tool_sweep.py runs: one recipe per tool, and per option where options take different code paths.

A recipe names a GUI (`module`), the widget variables to set (`set`: name -> value, the module-level
tkinter variables the GUI's run() reads), and the input:
    articles   lib/sampleData/newspaperArticles (5 book reviews, the Suite's default input)
    stories    those 5 plus the 5 stories in lib/sampleData (Shape of Stories needs several documents)
    file:<p>   one file, p relative to the bundle's lib/
    from:<recipe>:<pattern>   a file another recipe wrote (that recipe runs first)
`package` switches the NLP package in the recipe's own copy of the Parser & language config.
`needs` names software the zip does not bring: the recipe is SKIPPED, with the reason, when it is missing.
`answers` answers enter_value_widget prompts whose title contains the key (silent mode answers '').
`args` is passed to run() when the GUI's run takes arguments (SVO: run(package)).
`known` notes a failure the baseline already has, so it is not mistaken for news.

Tools not covered yet are in NOT_COVERED with the reason; test_tool_sweep.py checks that every
src/*_main.py is in one or the other.
"""

from dataclasses import dataclass, field


@dataclass
class Recipe:
    name: str
    module: str
    set: dict = field(default_factory=dict)
    input: str = "articles"
    package: str = ""
    needs: tuple = ()
    answers: dict = field(default_factory=dict)
    args: tuple = ()
    timeout_min: int = 30
    known: str = ""


R = Recipe
RECIPES = []


def add(*recipes):
    RECIPES.extend(recipes)


# ------------------------------------------------------------------ sentiment (BERT, Stanza, spaCy, dictionaries)
SA = {
    "BERT_English": "   BERT (English model)",
    "BERT_Multilingual": "   BERT (Multilingual model)",
    "CoreNLP": "   Stanford CoreNLP",
    "Stanza": "   Stanza",
    "spaCy": "   spaCy (TextBlob)",
    "ANEW": "   ANEW",
    "hedonometer": "   hedonometer",
    "NRC": "   NRC (emotion wheel)",
    "SentiWordNet": "   SentiWordNet",
    "VADER": "   VADER",
    "Character_Emotion_Arcs": "   Character Emotion Arcs (NER + NRC)",
}
for key, label in SA.items():
    add(
        R(
            "sentiment_" + key,
            "sentiment_analysis_main",
            set=dict(
                SA_algorithm_var=label, mean_var=1, median_var=1, shape_of_stories_var=0, character_arcs_checkbox_var=0
            ),
            needs=("corenlp",) if key == "CoreNLP" else (),
        )
    )

# ------------------------------------------------------------------ Shape of Stories: scores, HC, SVD, NMF, best k
for key, label in (
    ("BERT", "BERT (English model)"),
    ("spaCy", "spaCy"),
    ("Stanza", "Stanza"),
    ("CoreNLP", "Stanford CoreNLP"),
):
    add(
        R(
            "shape_of_stories_" + key,
            "shape_of_stories_main",
            input="stories",
            set=dict(
                sentiment_analysis_var=1,
                sentiment_analysis_menu_var=label,
                corpus_analysis_var=0,
                hierarchical_clustering_var=1,
                SVD_var=1,
                NMF_var=1,
                best_topic_estimation_var=1,
            ),
            needs=("corenlp",) if key == "CoreNLP" else (),
        )
    )

# ------------------------------------------------------------------ NER
for key, label in (
    ("BERT", "BERT (English language model)"),
    ("spaCy", "spaCy"),
    ("Stanza", "Stanza"),
    ("CoreNLP", "Stanford CoreNLP"),
):
    add(
        R(
            "NER_" + key,
            "NER_main",
            set=dict(NER_packages_var=label, NER_tag_var="All NER tags", NER_entity_timeline_var=0),
            needs=("corenlp",) if key == "CoreNLP" else (),
        )
    )

# ------------------------------------------------------------------ coreference
for key, label in (("BERT_fastcoref", "BERT"), ("Stanza", "Stanza"), ("CoreNLP", "Stanford CoreNLP")):
    add(
        R(
            "coreference_" + key,
            "coreference_main",
            set=dict(CoRef_var=label, manual_Coref_var=0, continue_manual_Coref_var=0, split_coreferenced_files_var=0),
            needs=("corenlp",) if key == "CoreNLP" else (),
        )
    )

# ------------------------------------------------------------------ topic modeling
TM_OFF = dict(BERT_var=0, Gensim_var=0, MALLET_var=0, Gensim_MALLET_var=0)
add(
    R(
        "topics_BERTopic_split",
        "topic_modeling_main",
        set={**TM_OFF, "BERT_var": 1, "split_docs_var": 1, "num_topics_var": 5},
    ),
    R(
        "topics_BERTopic_whole",
        "topic_modeling_main",
        set={**TM_OFF, "BERT_var": 1, "split_docs_var": 0, "num_topics_var": 5},
        known="stops on a small corpus of whole documents (future-work §10)",
    ),
    R("topics_Gensim", "topic_modeling_main", set={**TM_OFF, "Gensim_var": 1, "num_topics_var": 5}),
    R("topics_MALLET", "topic_modeling_main", set={**TM_OFF, "MALLET_var": 1, "num_topics_var": 5}, needs=("mallet",)),
)

# ------------------------------------------------------------------ word embeddings and WSI
W2V_OFF = dict(
    BERT_var=0,
    Gensim_var=0,
    WSI_var=0,
    vis_menu_var="Plot word vectors",
    compute_distances_var=1,
    keywords_var="",
    min_count_var=2,
)
add(
    R("word2vec_BERT", "word2vec_main", set={**W2V_OFF, "BERT_var": 1}),
    R("word2vec_Gensim", "word2vec_main", set={**W2V_OFF, "Gensim_var": 1}),
    R("word2vec_WSI", "word2vec_main", set={**W2V_OFF, "WSI_var": 1, "keywords_var": "book, novel"}),
)

# ------------------------------------------------------------------ parsers (the configured package)
for package in ("Stanza", "spaCy", "Stanford CoreNLP"):
    add(
        R(
            "parser_" + package.split()[-1],
            "parsers_annotators_main",
            package=package,
            # parser_menu_var is left at the GUI's default for the package (CoreNLP: PCFG; Stanza, spaCy:
            # Dependency parser), as a student gets it; a label the package does not offer runs nothing
            set=dict(
                parser_var=1,
                annotators_var=0,
                CoNLL_table_analyzer_var=0,
                quote_var=0,
                manual_Coref_var=0,
                open_GUI_var=0,
            ),
            needs=("corenlp",) if package == "Stanford CoreNLP" else (),
        )
    )

# ------------------------------------------------------------------ SVO
for package in ("Stanza", "spaCy", "Stanford CoreNLP"):
    add(
        R(
            "SVO_" + package.split()[-1],
            "SVO_main",
            set=dict(
                package_var=package,
                coref_var=0,
                manual_coref_var=0,
                SRL_var=0,
                compare_svo_var=0,
                gephi_var=1,
                google_earth_var=0,
                wordcloud_var=1,
                map_characters_var=0,
            ),
            args=(package,),
            needs=("corenlp",) if package == "Stanford CoreNLP" else (),
        )
    )

# ------------------------------------------------------------------ style (each vocabulary option)
STYLE = {
    "unigrams": "Vocabulary (via unigrams) - List of all words/tokens in input document(s)",
    "hapax_words": "Vocabulary (via Hapax legomena, once-occurring words)",
    "Stanza_lemmas": "Vocabulary (via Stanza multilanguage lemmatizer) - List of all words/tokens in input document(s)",
    "NLTK_unusual": "Vocabulary (via NLTK unusual words)",
    "richness": "Vocabulary richness (word type/token ratio or Yule’s K)",
    "abstract_concrete": "Abstract/concrete vocabulary",
    "objectivity_spaCy": "Objectivity/subjectivity (via spaCy)",
    "punctuation_pathos": "Punctuation as figures of pathos (? !)",
    "sentence_length": "Sentence length",
    "word_length": "Word length",
}
for key, label in STYLE.items():
    add(
        R(
            "style_" + key,
            "style_analysis_main",
            set=dict(
                extra_GUIs_var=0,
                complexity_readability_analysis_var=0,
                gender_guesser_var=0,
                vocabulary_analysis_var=1,
                vocabulary_analysis_menu_var=label,
            ),
        )
    )
add(
    R(
        "style_complexity_readability",
        "style_analysis_main",
        set=dict(
            extra_GUIs_var=0,
            complexity_readability_analysis_var=1,
            complexity_readability_analysis_menu_var="*",
            gender_guesser_var=0,
            vocabulary_analysis_var=0,
        ),
    ),
)

# ------------------------------------------------------------------ wordclouds
add(
    R(
        "wordclouds_Python",
        "wordclouds_main",
        set=dict(wordclouds_var="Python WordCloud", lemmatize_var=1, exclude_stopwords_var=1, max_words_var="100"),
    ),
)

# ------------------------------------------------------------------ GIS (geocoding needs the internet)
add(
    R(
        "GIS_folium_Stanza",
        "GIS_main",
        set=dict(
            NER_extractor_var=1,
            NER_package_var="Stanza",
            geocode_locations_var=1,
            geocoder_var="Nominatim",
            map_locations_var=1,
            GIS_package_var="Python folium pin map & heatmap",
            Google_Earth_OpenGUI=0,
        ),
        needs=("internet",),
        timeout_min=40,
    ),
)

# Tools without a recipe yet, and why. test_tool_sweep.py fails when a *_main.py is in neither list.
NOT_COVERED = {
    "NLP_menu_main": "the menu: bundle_gate.py starts it",
    "NLP_welcome_main": "the welcome screen: bundle_gate.py builds it",
    "NLP_setup_IO_main": "setup GUI, no RUN",
    "NLP_setup_package_language_main": "setup GUI, no RUN",
    "NLP_setup_external_software_main": "setup GUI, no RUN",
    "file_handler_ALL_main": "opens other GUIs only",
    "file_search_ALL_main": "opens other GUIs only",
    "semantic_analysis_ALL_main": "opens other GUIs only",
    "sentiments_emotions_ALL_main": "opens other GUIs only",
    "DB_PCACE_data_analysis_main": "needs a PC-ACE SQLite database",
    "DB_PCACE_data_validation_main": "needs a PC-ACE SQLite database",
    "DB_SQL_main": "needs a PC-ACE SQLite database",
    "corpus_checker_PCACE_data_main": "needs PC-ACE data",
    "SRL_main": "SRL runs in its own Python 3.8 env, not in the zip",
    # not written yet (next batch)
    "charts_Excel_main": "next batch",
    "CoNLL_table_analyzer_main": "next batch (from: a parser recipe's CoNLL table)",
    "corpus_profiler_main": "next batch",
    "data_manipulation_main": "next batch",
    "data_visualization_main": "next batch",
    "file_checker_converter_cleaner_main": "next batch",
    "file_checker_pre_processing_pipeline_main": "next batch",
    "file_classifier_main": "next batch",
    "file_manager_main": "next batch",
    "file_matcher_main": "next batch",
    "file_merger_main": "next batch",
    "file_search_byWord_main": "next batch",
    "file_spell_checker_main": "next batch",
    "file_splitter_main": "next batch",
    "GIS_distance_main": "next batch (from: the GIS recipe's locations)",
    "GIS_Google_Earth_main": "next batch (from: the GIS recipe's locations)",
    "GIS_symbolic_main": "next batch",
    "html_annotator_gender_main": "next batch",
    "html_annotator_main": "next batch",
    "knowledge_graphs_main": "next batch (needs the internet)",
    "narrative_analysis_ALL_main": "next batch",
    "NGrams_CoOccurrences_main": "next batch",
    "nominalization_main": "next batch",
    "sample_corpus_main": "next batch",
    "semantic_aggregation_main": "next batch (from: a parser recipe's CoNLL table)",
    "semantic_analysis_main": "next batch",
    "sentence_analysis_main": "next batch",
    "statistics_csv_main": "next batch",
    "statistics_txt_main": "next batch",
    "syntactic_analysis_ALL_main": "next batch",
}


def by_name():
    return {r.name: r for r in RECIPES}
