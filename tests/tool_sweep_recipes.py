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
`yes` answers Yes to a yes/no question whose title or text contains one of these strings (silent mode
answers No unless the question's default is Yes); every question is recorded either way.
`args` is passed to run() when the GUI's run takes arguments (SVO: run(package)).
`call` names the function RUN calls when it is not run() (the spell checker's run_similarity_command).
`csv` is a second input, 'from:<recipe>:<pattern>' like `input`, for GUIs that take a csv in a widget of
their own; in a `set` value '{csv}' becomes its path ('{input}' the I/O input file, '{articles}' the
input folder, '{lib}' the bundle's lib/).
`own_input` gives the recipe its own copy of the input folder, for tools that write into it (the file
splitter, cleaners, sample corpus); files they add there are moved to the recipe's _written_in_input/.
`set` also takes module-level lists and strings (ngrams_options_list = [...]), which have no .set().
`tab` selects that tab of a GUI's notebook before RUN (Data visualization runs the selected tab).
`known` notes a failure the baseline already has, so it is not mistaken for news.
Inputs also include `docs`: one article as .docx, .pdf, .rtf and .csv (tests/fixtures/sweep_docs).

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
    yes: tuple = ()
    args: tuple = ()
    timeout_min: int = 30
    known: str = ""
    call: str = "run"
    csv: str = ""
    own_input: bool = False
    tab: int = -1

    def deps(self):
        """The recipes whose outputs this one reads."""
        return [spec.split(":")[1] for spec in (self.input, self.csv) if spec.startswith("from:")]


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
            yes=("TOO FEW",),  # 10 documents; it recommends 50 and asks whether to go on
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
        known="5 documents are fewer than BERTopic's 10: FAILED up to 1.6.45, EMPTY with a warning from #1772 on",
    ),
    R("topics_Gensim", "topic_modeling_main", set={**TM_OFF, "Gensim_var": 1, "num_topics_var": 5}),
    R("topics_MALLET", "topic_modeling_main", set={**TM_OFF, "MALLET_var": 1, "num_topics_var": 5}, needs=("mallet",)),
)

# ------------------------------------------------------------------ word embeddings and WSI
W2V_YES = ("t-SNE",)  # asks whether to go on with the (slow) plot of word vectors
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
    R("word2vec_BERT", "word2vec_main", set={**W2V_OFF, "BERT_var": 1}, yes=W2V_YES),
    R("word2vec_Gensim", "word2vec_main", set={**W2V_OFF, "Gensim_var": 1}, yes=W2V_YES),
)

# word sense induction lives in Semantic analysis (word2vec_main no longer offers it)
add(
    R(
        "semantic_WSI_BERT",
        "semantic_analysis_main",
        set=dict(
            WSI_var=1,
            WSI_keywords_var="book",
            WSD_var=0,
            SSC_var=0,
            SRL_var=0,
            vocabulary_analysis_var=0,
            extra_GUIs_var=0,
        ),
    ),
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

# ================================================================== second batch (23 Nov)
CONLL_STANZA = "from:parser_Stanza:NLP_CoNLL_Stanza.csv"
CONLL_SPACY = "from:parser_spaCy:NLP_CoNLL_SpaCy.csv"
VADER = "from:sentiment_VADER:NLP_VADER.csv"
LOCATIONS = "from:GIS_folium_Stanza:*geo-Nom_Location.csv"

# ------------------------------------------------------------------ CoNLL table analyzer (Stanza and spaCy tables)
CONLL_OFF = dict(
    extra_GUIs_var=0,
    run_parser_var=0,
    all_analyses_var=0,
    advanced_analyses_var=0,
    search_token_var=0,
    WordNet_var=0,
    compute_sentence_var=0,
    k_sentences_var=0,
)
for key, table in (("Stanza", CONLL_STANZA), ("spaCy", CONLL_SPACY)):
    add(
        R(
            "CoNLL_all_analyses_" + key,
            "CoNLL_table_analyzer_main",
            input=table,
            set={**CONLL_OFF, "all_analyses_var": 1, "all_analyses": "*"},
        )
    )
add(
    R(
        "CoNLL_advanced_analyses",
        "CoNLL_table_analyzer_main",
        input=CONLL_STANZA,
        set={**CONLL_OFF, "advanced_analyses_var": 1, "advanced_analyses": "*"},
    ),
    R(
        "CoNLL_search_token",
        "CoNLL_table_analyzer_main",
        input=CONLL_STANZA,
        set={
            **CONLL_OFF,
            "search_token_var": 1,
            "searchField_kw_var": "book",
            "searchedCoNLLField_var": "FORM",
            "postag_var": "*",
            "deprel_var": "*",
            "co_postag_var": "*",
            "co_deprel_var": "*",
        },
    ),
)

# ------------------------------------------------------------------ semantic aggregation (WordNet, from a CoNLL table)
SEM_OFF = dict(
    disambiguate_var=0,
    disaggregate_var=0,
    annotate_file_var=0,
    aggregate_lemmatized_var=0,
    extract_nouns_verbs_from_CoNLL_var=0,
    aggregate_bySentenceID_var=0,
    noun_verb_menu_var="NOUN",
    knowledge_base_menu_var="WordNet",
    csv_file_var="{csv}",
)
add(
    R(
        "semantic_aggregation_extract_nouns_verbs",
        "semantic_aggregation_main",
        csv=CONLL_STANZA,
        set={**SEM_OFF, "extract_nouns_verbs_from_CoNLL_var": 1},
    ),
    R(
        "semantic_aggregation_zoom_out",
        "semantic_aggregation_main",
        csv="from:semantic_aggregation_extract_nouns_verbs:*nouns_lemma*.csv",
        set={**SEM_OFF, "aggregate_lemmatized_var": 1},
    ),
    R(
        "semantic_aggregation_zoom_in",
        "semantic_aggregation_main",
        set={**SEM_OFF, "csv_file_var": "", "disaggregate_var": 1, "wordNet_keyword_list": ["person"]},
    ),
    R(
        "semantic_aggregation_bySentenceID",
        "semantic_aggregation_main",
        csv=CONLL_STANZA,
        input="from:semantic_aggregation_zoom_out:NLP_WordNet_UP_NOUN_*_nouns_lemma.csv",
        set={**SEM_OFF, "aggregate_bySentenceID_var": 1, "dict_WordNet_filename_var": "{input}"},
    ),
    R(
        "semantic_aggregation_WSD",
        "semantic_aggregation_main",
        csv=CONLL_STANZA,
        set={**SEM_OFF, "disambiguate_var": 1},
    ),
)

# ------------------------------------------------------------------ N-grams and co-occurrences
NG_OFF = dict(
    extra_GUIs_var=0,
    Ngrams_compute_var=0,
    Ngrams_search_var=0,
    ngrams_viewer_var=0,
    CoOcc_Viewer_var=0,
    csv_file_var="",
    search_words_var="",
    ngrams_menu_var="Word",
    ngrams_size=3,
    ngrams_options_list=[],
    viewer_options_list=[],
    date_options=0,
)
for key, options in (
    ("plain", []),
    ("lemmatized_no_stopwords", ["Lemmatize", "Exclude ALL stopwords (word N-grams only)"]),
    ("hapax", ["Hapax legomena (once-occurring words)"]),
    ("by_sentence", ["By sentence index"]),
    ("collocations", ["Collocation statistics (PMI, log-likelihood, chi-squared, t-score)"]),
):
    add(
        R(
            "ngrams_word_" + key,
            "NGrams_CoOccurrences_main",
            set={**NG_OFF, "Ngrams_compute_var": 1, "ngrams_options_list": options},
        )
    )
add(
    R(
        "ngrams_character",
        "NGrams_CoOccurrences_main",
        set={**NG_OFF, "Ngrams_compute_var": 1, "ngrams_menu_var": "Character"},
    ),
    R(
        "cooccurrences_viewer",
        "NGrams_CoOccurrences_main",
        set={**NG_OFF, "CoOcc_Viewer_var": 1, "search_words_var": "book, novel"},
    ),
)

# ------------------------------------------------------------------ statistics (txt and csv)
add(
    R(
        "statistics_txt_all",
        "statistics_txt_main",
        set=dict(
            corpus_statistics_var=1,
            corpus_statistics_byPOS_var=0,
            corpus_statistics_options_menu_var="*",
            corpus_text_options_menu_var="*",
        ),
    ),
    R(
        "statistics_txt_byPOS",
        "statistics_txt_main",
        set=dict(
            corpus_statistics_var=0,
            corpus_statistics_byPOS_var=1,
            corpus_statistics_options_menu_var="*",
            corpus_text_options_menu_var="*",
        ),
    ),
)
STAT_OFF = dict(
    all_csv_stats_var=0,
    csv_field_freq_var=0,
    stat_test_var=0,
    csv_list=[],
    hover_over_list=[],
    groupBy_list=[],
    input_csv_file_var="",
)
add(
    R("statistics_csv_all_columns", "statistics_csv_main", input=VADER, set={**STAT_OFF, "all_csv_stats_var": 1}),
    R(
        "statistics_csv_field_frequency",
        "statistics_csv_main",
        input=VADER,
        set={**STAT_OFF, "csv_field_freq_var": 1, "csv_list": ["Sentiment label"]},
    ),
)
TESTS = {  # test: (value column, group column) on the VADER table
    "MW_KW": ("Mann-Whitney U / Kruskal-Wallis", "Sentiment score", "Sentiment label"),
    "chi_square": ("Chi-square (independence)", "Sentiment label", "Document ID"),
    "crosstab": ("Cross-tabulation (contingency table)", "Sentiment label", "Document ID"),
    "correlation": ("Correlation (Spearman / Kendall)", "Sentiment score", "Sentence ID"),
    "Mann_Kendall": ("Mann-Kendall (temporal trend)", "Sentiment score", "Sentence ID"),
    "change_point": ("Change-point detection (temporal)", "Sentiment score", "Sentence ID"),
    "permutation": ("Permutation test (two groups)", "Sentiment score", "Sentiment label"),
    "Bayes_factor": ("Bayes factor (two groups)", "Sentiment score", "Sentiment label"),
    "adjusted_Rand": ("Adjusted Rand index (clustering agreement)", "Sentiment label", "Document ID"),
    "silhouette": ("Silhouette (cluster cohesion)", "", "Sentiment label"),
}
for key, (test, value, group) in TESTS.items():
    add(
        R(
            "statistics_csv_test_" + key,
            "statistics_csv_main",
            input=VADER,
            set={
                **STAT_OFF,
                "stat_test_var": 1,
                "stat_test_menu_var": test,
                "stat_value_col_var": value,
                "stat_group_col_var": group,
            },
        )
    )

# ------------------------------------------------------------------ Excel charts and data visualization (VADER table)
add(
    R(
        "charts_Excel_line",
        "charts_Excel_main",
        input=VADER,
        set=dict(
            selected_series=[["Sentence ID", "Sentiment score"]],
            chart_type="line",
            chart_type_list=["line"],
            count_var=0,
            hover_var_list=[0],
            second_yAxis_var_list=[0],
            column_yAxis_field_list=[],
            chart_title_var="Sentiment",
        ),
    ),
)
for key, option in (
    ("treemap", "Treemap"),
    ("sunburst", "Sunburst"),
    ("stacked_bar", "Stacked bar"),
    ("waffle", "Waffle chart"),
    ("colormap", "Colormap/heatmap"),
):
    add(
        R(
            "dataviz_categorical_" + key,
            "data_visualization_main",
            call="run_command",
            tab=1,
            input=VADER,
            set=dict(
                categorical_menu_var=option,
                csv_field_categorical_var="Sentiment label",
                # what the + button builds: "field|comma-separated search values"
                csv_file_categorical_field_list=[
                    ["Document ID|1,2,3,4,5"],
                    ["Sentiment label|positive,negative,neutral"],
                ],
            ),
        )
    )
for key, option in (
    ("boxplot", "Boxplots"),
    ("histogram", "Histogram"),
    ("violin", "Violin plot"),
    ("correlation_heatmap", "Correlation heatmap"),
):
    add(
        R(
            "dataviz_numeric_" + key,
            "data_visualization_main",
            call="run_command",
            tab=3,
            input=VADER,
            set=dict(visualizations_menu_var=option, csv_field_visualization_var="Sentiment score"),
        )
    )
add(
    R(
        "dataviz_relational_Sankey",
        "data_visualization_main",
        call="run_command",
        tab=0,
        input="from:SVO_spaCy:NLP_SVO_*.csv",
        set=dict(relations_menu_var="Sankey", csv_file_relational_field_list=["Subject (S)", "Verb (V)", "Object (O)"]),
    ),
    R(
        "dataviz_relational_visjs",
        "data_visualization_main",
        call="run_command",
        tab=0,
        input="from:SVO_spaCy:NLP_SVO_*.csv",
        set=dict(
            relations_menu_var="Network graph (vis.js)",
            csv_file_relational_field_list=["Subject (S)", "Verb (V)", "Object (O)"],
        ),
    ),
)

# ------------------------------------------------------------------ corpus profiler (one recipe per analysis group)
PROFILER = ("counts", "syntax", "semantics", "topics", "entities", "spatial", "narrative", "sentiment", "characters")
for group in PROFILER:
    add(
        R(
            "corpus_profiler_" + group,
            "corpus_profiler_main",
            set={**{g + "_var": int(g == group) for g in PROFILER}, group + "_menu_var": "*"},
            needs=("corenlp",) if group in ("entities", "narrative") else ("internet",) if group == "spatial" else (),
            yes=("ENTIRE",),  # the CoreNLP pass over the whole corpus
            timeout_min=40,
        )
    )

# ------------------------------------------------------------------ sentences, nominalization, style hubs
add(
    R(
        "sentence_complexity_readability",
        "sentence_analysis_main",
        set=dict(
            compute_sentence_length_var=1,
            visualize_bySentenceIndex_var=0,
            sentence_complexity_var=1,
            text_readability_var=1,
            visualize_sentence_structure_var=0,
        ),
    ),
    R("nominalization", "nominalization_main", set=dict(check_nom_verb_ending_var=1)),
    R(
        "syntactic_WSD",
        "syntactic_analysis_ALL_main",
        input=CONLL_STANZA,
        set=dict(extra_GUIs_var=0, WSD_var=1, SRL_var=0, SSC_var=0, vocabulary_analysis_var=0),
    ),
)

# ------------------------------------------------------------------ file tools
add(
    R("file_merger", "file_merger_main", set=dict(merge_subdir_var=0, merge_save_fileName_var=1)),
    R(
        "file_search_keyword",
        "file_search_byWord_main",
        set=dict(
            search_by_dictionary_var=0,
            search_by_keyword_var=1,
            keyword_value_var="book",
            extract_sentences_var=1,
            coOccurring_keywords_var=0,
            create_subcorpus_var=0,
        ),
    ),
    R(
        "file_splitter_by_length",
        "file_splitter_main",
        own_input=True,
        set=dict(docLength_var=1, split_docLength_var="2000"),
    ),
    R(
        "file_splitter_BME_sentences",
        "file_splitter_main",
        own_input=True,
        set=dict(extract_BME_K_sentences_var=1, Begin_K_sent_var=2, End_K_sent_var=2),
    ),
    R(
        "file_splitter_extract_sentences",
        "file_splitter_main",
        own_input=True,
        set=dict(extract_sentences_var=1, extract_sentences_search_words_var="book"),
    ),
    R(
        "file_manager_list",
        "file_manager_main",
        set=dict(list_var=1),
    ),
    R(
        "file_manager_count",
        "file_manager_main",
        set=dict(count_file_manager_var=1),
    ),
    R(
        "file_pre_processing_pipeline",
        "file_checker_pre_processing_pipeline_main",
        set=dict(
            utf8_var=1,
            ASCII_var=0,
            language_detect_var=1,
            spelling_var=1,
            NLTK_unusual_var=1,
            lower_case_words_after_end_of_sentence_var=1,
            word_length_var=1,
            sentence_length_var=1,
        ),
    ),
    R(
        "spell_checker_all",
        "file_spell_checker_main",
        call="run_similarity_command",
        set=dict(spelling_checker_var=1, checker_value_var="*", bydictionary_value_var=0, byNER_value_var=0),
    ),
    R(
        "sample_corpus_by_keyword",
        "sample_corpus_main",
        own_input=True,
        set=dict(sample_by_keywords_inDocument_var=1, keywords_inDocument_var="book"),
    ),
)
CHECK = (
    ("check_utf8", "check_tools_var", "Check utf-8 encoding compliance", "articles"),
    ("check_empty", "check_tools_var", "Check empty file", "articles"),
    ("check_hyphenation", "check_tools_var", "Check end-of-line typesetting hyphenation", "articles"),
    ("check_language", "check_tools_var", "Language detector", "articles"),
    (
        "check_encoding",
        "check_tools_var",
        "Predict encoding (via chardet)",
        "file:sampleData/The Three Little Pigs.txt",
    ),
    ("convert_docx", "convert_tools_var", "Document converter (docx --> txt)", "docs:article.docx"),
    ("convert_pdf", "convert_tools_var", "Document converter (pdf --> txt) (via pdfminer)", "docs:article.pdf"),
    ("convert_rtf", "convert_tools_var", "Document converter (rtf --> txt)", "docs:article.rtf"),
    ("clean_ASCII", "clean_tools_var", "Change to ASCII non-ASCII apostrophes & quotes and % to percent", "articles"),
    ("clean_blank_lines", "clean_tools_var", "Remove blank lines from text file(s)", "articles"),
    (
        "clean_add_full_stop",
        "clean_tools_var",
        "Add full stop (.) at the end of paragraphs without end-of-paragraph punctuation",
        "articles",
    ),
)
for key, var, label, source in CHECK:
    add(
        R(
            "file_" + key,
            "file_checker_converter_cleaner_main",
            input=source,
            own_input=source == "articles",  # cleaners change the files they read
            set={var: label},
            yes=("Are you sure you want to continue",),  # cleaners change the input files (their own copy here)
        )
    )

# ------------------------------------------------------------------ GIS from the geocoded locations, and symbolic space
add(
    R(
        "GIS_distance_pairwise",
        "GIS_distance_main",
        input=LOCATIONS,
        set=dict(
            compute_pairwise_distances_var=1, compute_baseline_distances_var=0, compute_consecutive_distances_var=1
        ),
    ),
    R(
        "GIS_Google_Earth",
        "GIS_Google_Earth_main",
        input=LOCATIONS,
        set=dict(location_var="Location", group_var=0, heat_map_var=0, date_var=0),
    ),
    R(
        "GIS_symbolic_extract",
        "GIS_symbolic_main",
        input=CONLL_STANZA,
        set=dict(extract_var=1, map_var=0, distribution_var=0),
    ),
)

# ------------------------------------------------------------------ annotators and knowledge graphs
add(
    R(
        "html_annotator_dictionary",
        "html_annotator_main",
        set=dict(
            html_annotator_dictionary_var=1,
            html_annotator_add_dictionary_var=0,
            html_annotator_extractor_var=0,
            knowledge_graphs_DBpedia_YAGO_var=0,
            semantic_aggregation_WordNet_var=0,
            html_gender_annotator_var=0,
            html_annotator_dictionary_file_var="{lib}/wordLists/social-actor-list.csv",
            csv_field1_var="Term",
            csv_field2_var="WordNet Category",
            color_palette_dict_var="red",
        ),
    ),
    R(
        "html_annotator_gender_dictionary",
        "html_annotator_gender_main",
        set=dict(
            CoreNLP_gender_annotator_var=0,
            annotator_dictionary_var=1,
            annotator_dictionary_file_var="{lib}/namesGender/NLTK.csv",
            plot_var=0,
        ),
    ),
    R(
        "knowledge_graph_Wikipedia",
        "knowledge_graphs_main",
        set=dict(knowledge_graphs_var="Wikipedia"),
        needs=("internet",),
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
    "narrative_analysis_ALL_main": "opens other GUIs only",
    "data_manipulation_main": "its operations are built one + click at a time; not written yet",
    "file_classifier_main": "needs a second folder of classified documents; not written yet",
    "file_matcher_main": "matches files of two types across folders; not written yet",
}


def by_name():
    return {r.name: r for r in RECIPES}
