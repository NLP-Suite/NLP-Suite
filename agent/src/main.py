import json
import logging
import os
import sys
import traceback
from collections.abc import Callable
from threading import Lock, Thread
from typing import Annotated

# Configure logging before any processing module is imported: the first
# basicConfig call wins, and INFO is where job validation warnings surface.
logging.basicConfig(format="%(asctime)s : %(levelname)s : %(name)s : %(message)s", level=logging.INFO)

# Add all src subdirectories to sys.path so flat imports in util files work
# regardless of which subdirectory the module lives in.
_src_dir = os.path.dirname(os.path.abspath(__file__))
for _d in os.listdir(_src_dir):
    _dp = os.path.join(_src_dir, _d)
    if os.path.isdir(_dp) and not _d.startswith("."):
        sys.path.insert(0, _dp)

import uvicorn
from boxplot_chart import run as run_boxplot
from colormap_chart import run_colormap
from CoNLL_table_analyzer_main import run_CoNLL_table_analyzer
from excel_plotly_charts import run_excel_plotly_charts
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from file_manager_main import run_file_manager
from file_search_byWord_main import run_search_byWord
from GIS_main import run_GIS
from html_annotator_gender_main import run as run_gender_analysis
from knowledge_graphs_WordNet_main import run_kg_wordnet
from NER_main import run_NER
from NGrams_CoOccurrences import run_ngrams
from parsers_annotators import run_parsers_annotators
from sankey_flowchart import run_sankey
from sentence_analysis import run_sentence_analysis
from sentiment_analysis import run_sentiment_analysis
from shape_of_stories_main import run as run_shape_of_stories
from statistics_txt_main import run_statistics
from style_analysis import run_style_analysis
from sunburst_charts import run_sun_burst
from SVO import run_svo
from topic_modeling import run_topic_modeling
from word2vec import run_word2vec
from wordcloud_visual import run_wordcloud

_ENV_PATH = os.path.join(os.path.expanduser("~"), "nlp-suite", ".env")
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "nlp-suite", "output")


def _load_env_file():
    """Read key=value lines from ~/nlp-suite/.env into os.environ (does not override existing vars)."""
    if not os.path.exists(_ENV_PATH):
        return
    with open(_ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k not in os.environ:
                os.environ[k] = v


_load_env_file()

GOOGLE_MAPS_API_KEY: str = os.environ.get("GOOGLE_MAPS_API_KEY", "")
NYT_API_KEY: str = os.environ.get("NYT_API_KEY", "")


def _write_env_file(google_maps_api_key: str, nyt_api_key: str):
    os.makedirs(os.path.dirname(_ENV_PATH), exist_ok=True)
    lines: list[str] = []
    if os.path.exists(_ENV_PATH):
        with open(_ENV_PATH) as f:
            for line in f:
                k = line.split("=")[0].strip()
                if k not in ("GOOGLE_MAPS_API_KEY", "NYT_API_KEY"):
                    lines.append(line.rstrip("\n"))
    lines.append(f"GOOGLE_MAPS_API_KEY={google_maps_api_key}")
    lines.append(f"NYT_API_KEY={nyt_api_key}")
    with open(_ENV_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")


app = FastAPI(debug=True)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_worker_lock = Lock()
app.worker = False

logger = logging.getLogger(__name__)

# Error message from the most recently finished job, or None if it succeeded.
# Read by /status so the UI can tell "done" apart from "crashed".
_job_state: dict = {"last_error": None}

# Paths that never trigger background jobs and must not participate in lock management.
_LOCK_EXEMPT_PATHS = {"/settings", "/status"}


def run(app, method):
    try:
        method()
        _job_state["last_error"] = None
    except Exception as exc:
        _job_state["last_error"] = f"{type(exc).__name__}: {exc}"
        logger.error("Background job failed:\n%s", traceback.format_exc())
    finally:
        app.worker = False
        _worker_lock.release()


def dispatch(app, fn: Callable[[], None]) -> PlainTextResponse:
    Thread(target=lambda: run(app, fn)).start()
    return PlainTextResponse("", status_code=200)


@app.middleware("http")
async def single_runner(request: Request, call_next):
    if request.url.path in _LOCK_EXEMPT_PATHS:
        return await call_next(request)

    if not _worker_lock.acquire(blocking=False):
        return PlainTextResponse("The agent is currently busy running another job", status_code=503)

    app.worker = True
    response = await call_next(request)
    if response.status_code >= 400:
        app.worker = False
        _worker_lock.release()

    return response


@app.get("/status")
def status() -> JSONResponse:
    return JSONResponse({"busy": app.worker, "last_error": _job_state["last_error"]})


@app.post("/file_manager")
def file_manager(
    inputDirectory: Annotated[str, Form()],
    chartPackage: Annotated[str, Form()] = "",
    dataTransformation: Annotated[str, Form()] = "",
    selectedCsvFile_var: Annotated[str, Form()] = "",
    selectedCsvFile_colName: Annotated[str, Form()] = "",
    list_var: Annotated[bool, Form()] = False,
    rename_var: Annotated[bool, Form()] = False,
    copy_var: Annotated[bool, Form()] = False,
    move_var: Annotated[bool, Form()] = False,
    delete_var: Annotated[bool, Form()] = False,
    count_file_manager_var: Annotated[bool, Form()] = False,
    split_var: Annotated[bool, Form()] = False,
    rename_new_entry: Annotated[str, Form()] = "",
    by_file_type_var: Annotated[bool, Form()] = False,
    file_type_menu_var: Annotated[str, Form()] = "",
    by_creation_date_var: Annotated[bool, Form()] = False,
    by_author_var: Annotated[bool, Form()] = False,
    before_date_var: Annotated[str, Form()] = "",
    after_date_var: Annotated[str, Form()] = "",
    by_prefix_var: Annotated[bool, Form()] = False,
    by_substring_var: Annotated[bool, Form()] = False,
    string_entry_var: Annotated[str, Form()] = "",
    by_foldername_var: Annotated[bool, Form()] = False,
    folder_character_separator_var: Annotated[str, Form()] = "",
    by_embedded_items_var: Annotated[bool, Form()] = False,
    comparison_var: Annotated[str, Form()] = "",
    number_of_items_var: Annotated[int, Form()] = 0,
    embedded_item_character_value_var: Annotated[str, Form()] = "",
    include_exclude_var: Annotated[str, Form()] = "",
    character_count_file_manager_var: Annotated[bool, Form()] = False,
    character_entry_var: Annotated[str, Form()] = "",
    include_subdir_var: Annotated[bool, Form()] = False,
    fileName_embeds_date: Annotated[bool, Form()] = False,
    date_format: Annotated[str, Form()] = "",
    date_separator: Annotated[str, Form()] = "",
    date_position: Annotated[int, Form()] = 0,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return dispatch(
        app,
        lambda: run_file_manager(
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            selectedCsvFile_var=selectedCsvFile_var,
            selectedCsvFile_colName=selectedCsvFile_colName,
            utf8_var=False,
            ASCII_var=False,
            list_var=list_var,
            rename_var=rename_var,
            copy_var=copy_var,
            move_var=move_var,
            delete_var=delete_var,
            count_file_manager_var=count_file_manager_var,
            split_var=split_var,
            rename_new_entry=rename_new_entry,
            by_file_type_var=by_file_type_var,
            file_type_menu_var=file_type_menu_var,
            by_creation_date_var=by_creation_date_var,
            by_author_var=by_author_var,
            before_date_var=before_date_var,
            after_date_var=after_date_var,
            by_prefix_var=by_prefix_var,
            by_substring_var=by_substring_var,
            string_entry_var=string_entry_var,
            by_foldername_var=by_foldername_var,
            folder_character_separator_var=folder_character_separator_var,
            by_embedded_items_var=by_embedded_items_var,
            comparison_var=comparison_var,
            number_of_items_var=number_of_items_var,
            embedded_item_character_value_var=embedded_item_character_value_var,
            include_exclude_var=include_exclude_var,
            character_count_file_manager_var=character_count_file_manager_var,
            character_entry_var=character_entry_var,
            include_subdir_var=include_subdir_var,
            fileName_embeds_date=fileName_embeds_date,
            date_format=date_format,
            date_separator=date_separator,
            date_position=date_position,
        ),
    )


@app.post("/sentiment_analysis")
def sentiment_analysis(
    inputDirectory: Annotated[str, Form()],
    algorithm: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    calculateMean: Annotated[bool, Form()] = False,
    calculateMedian: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_sentiment_analysis(
            input_dir,
            OUTPUT_DIR,
            False,
            "Excel",
            dataTransformation,
            calculateMean,
            calculateMedian,
            algorithm,
        ),
    )


@app.post("/topic_modeling")
def topic_modeling(
    inputDirectory: Annotated[str, Form()],
    numberOfTopics: Annotated[int, Form()],
    optimizeTopicIntervals: Annotated[int, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    topicModelingBERT: Annotated[bool, Form()] = False,
    splitToSentence: Annotated[bool, Form()] = False,
    topicModelingMALLET: Annotated[bool, Form()] = False,
    topicModelingGensim: Annotated[bool, Form()] = False,
    removeStopwords: Annotated[bool, Form()] = False,
    lemmatizeWords: Annotated[bool, Form()] = False,
    nounsOnly_var: Annotated[bool, Form()] = False,
    Gensim_MALLET_var: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_topic_modeling(
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            num_topics=numberOfTopics,
            BERT_var=topicModelingBERT,
            split_docs_var=splitToSentence,
            MALLET_var=topicModelingMALLET,
            optimize_intervals_var=optimizeTopicIntervals,
            Gensim_var=topicModelingGensim,
            remove_stopwords_var=removeStopwords,
            lemmatize_var=lemmatizeWords,
            nounsOnly_var=nounsOnly_var,
            Gensim_MALLET_var=Gensim_MALLET_var,
        ),
    )


@app.post("/parse")
def parsers_annotators(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    manual_Coref: Annotated[bool, Form()] = False,
    parser_var: Annotated[bool, Form()] = False,
    parser_menu_var: Annotated[str, Form()] = "",
    single_quote: Annotated[bool, Form()] = False,
    annotators_var: Annotated[bool, Form()] = False,
    annotators_menu_var: Annotated[str, Form()] = "",
    package: Annotated[str, Form()] = "Stanford CoreNLP",
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_parsers_annotators(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=False,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            manual_Coref=manual_Coref,
            parser_var=parser_var,
            parser_menu_var=parser_menu_var,
            single_quote=single_quote,
            CoNLL_table_analyzer_var=False,
            annotators_var=annotators_var,
            annotators_menu_var=annotators_menu_var,
            package=package,
        ),
    )


@app.post("/word2vec")
def word2vec(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    ngramsDropDown: Annotated[str, Form()] = "3-grams (unigrams)",
    remove_stopwords_var: Annotated[bool, Form()] = False,
    lemmatize_var: Annotated[bool, Form()] = False,
    WSI_var: Annotated[bool, Form()] = False,
    BERT_var: Annotated[bool, Form()] = False,
    Gensim_var: Annotated[bool, Form()] = False,
    sg_menu_var: Annotated[str, Form()] = "Skip-Gram",
    vector_size_var: Annotated[int, Form()] = 100,
    window_var: Annotated[int, Form()] = 5,
    min_count_var: Annotated[int, Form()] = 5,
    vis_menu_var: Annotated[str, Form()] = "Plot word vectors",
    dim_menu_var: Annotated[str, Form()] = "2D",
    compute_distances_var: Annotated[bool, Form()] = False,
    top_words_var: Annotated[int, Form()] = 200,
    keywords_var: Annotated[str, Form()] = "",
    keywordInput: Annotated[str, Form()] = "",
    range4: Annotated[int, Form()] = 4,
    range6: Annotated[int, Form()] = 6,
    range20: Annotated[int, Form()] = 10,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_word2vec(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            remove_stopwords_var=remove_stopwords_var,
            lemmatize_var=lemmatize_var,
            WSI_var=WSI_var,
            BERT_var=BERT_var,
            Gensim_var=Gensim_var,
            sg_menu_var=sg_menu_var,
            vector_size_var=vector_size_var,
            window_var=window_var,
            min_count_var=min_count_var,
            vis_menu_var=vis_menu_var,
            dim_menu_var=dim_menu_var,
            compute_distances_var=compute_distances_var,
            top_words_var=top_words_var,
            keywords_var=keywords_var,
            keywordInput=keywordInput,
            range4=range4,
            range6=range6,
            range20=range20,
            ngramsDropDown=ngramsDropDown,
        ),
    )


@app.post("/conll_table")
def CoNLL_table_analyzer(
    inputDirectory: Annotated[str, Form()],
    searchedCoNLLField: Annotated[str, Form()],
    postag_var: Annotated[str, Form()],
    deprel: Annotated[str, Form()],
    co_postag: Annotated[str, Form()],
    co_deprel: Annotated[str, Form()],
    inputFilename: Annotated[str, Form()] = "",
    dataTransformation: Annotated[str, Form()] = "No transformation",
    all_analyses_var: Annotated[bool, Form()] = False,
    all_analyses: Annotated[str, Form()] = "*",
    searchField_kw: Annotated[str, Form()] = "",
    Begin_K_sent_var: Annotated[bool, Form()] = False,
    End_K_sent_var: Annotated[bool, Form()] = False,
    compute_sentence_var: Annotated[bool, Form()] = False,
    search_token_var: Annotated[bool, Form()] = False,
    k_sentences_var: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_CoNLL_table_analyzer(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=False,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            searchedCoNLLField=searchedCoNLLField,
            searchField_kw=searchField_kw,
            postag_var=postag_var,
            deprel=deprel,
            co_postag=co_postag,
            co_deprel=co_deprel,
            Begin_K_sent_var=Begin_K_sent_var,
            End_K_sent_var=End_K_sent_var,
            all_analyses_var=all_analyses_var,
            all_analyses=all_analyses,
            search_token_var=search_token_var,
            WordNet_var=False,
            compute_sentence_var=compute_sentence_var,
            k_sentences_var=k_sentences_var,
        ),
    )


@app.post("/style_analysis")
def style_analysis(
    inputDirectory: Annotated[str, Form()],
    analysis_dropdown: Annotated[str, Form()],
    voc_options: Annotated[str, Form()],
    min_rating: Annotated[int, Form()],
    max_rating_sd: Annotated[int, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    complexity_analysis: Annotated[bool, Form()] = False,
    vocabulary_analysis: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_style_analysis(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            extra_GUIs_var=False,
            complexity_readability_analysis_var=complexity_analysis,
            complexity_readability_analysis_menu_var=analysis_dropdown,
            vocabulary_analysis_var=vocabulary_analysis,
            vocabulary_analysis_menu_var=voc_options,
            gender_guesser_var=False,
            min_rating=min_rating,
            max_rating_sd=max_rating_sd,
        ),
    )


@app.post("/sunburst")
def sunburst_charts(
    sunburst_file_input: Annotated[str, Form()],
    inputDirectory: Annotated[str, Form()],
    file_data: Annotated[str, Form()] = "",
    filter_options_var: Annotated[str, Form()] = "No filtering",
    savedPairsToSend: Annotated[str, Form()] = "[]",
    piechart_var: Annotated[bool, Form()] = False,
    treemap_var: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_sun_burst(
            inputFilename=sunburst_file_input,
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            file_data=file_data,
            filter_options_var=filter_options_var,
            selected_pairs_data=savedPairsToSend,
            piechart_var=piechart_var,
            treemap_var=treemap_var,
        ),
    )


@app.post("/colormap")
def colormap_chart(
    colormap_file_input: Annotated[str, Form()],
    max_number_of_rows: Annotated[int, Form()],
    less_freq_color_picker: Annotated[str, Form()],
    csv_file_categorical_field_list_front: Annotated[str, Form()] = "[]",
    more_freq_color_picker: Annotated[str, Form()] = False,
    normalize: Annotated[str, Form()] = False,
    file_data: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    return dispatch(
        app,
        lambda: run_colormap(
            inputFilename=colormap_file_input,
            outputDir=OUTPUT_DIR,
            csv_file_categorical_field_list=csv_file_categorical_field_list_front,
            max_rows_var=max_number_of_rows,
            color_1_style_var=less_freq_color_picker,
            color_2_style_var=more_freq_color_picker,
            normalize_var=normalize,
            inputFileData=file_data,
        ),
    )


@app.post("/sankey")
def sankey_flowchart(
    inputDirectory: Annotated[str, Form()],
    variable_1_max: Annotated[int, Form()],
    variable_2_max: Annotated[int, Form()],
    variable_3_max: Annotated[int, Form()],
    selected_pairs_data: Annotated[str, Form()] = "[]",
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_sankey(
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            csv_file_relational_field_list=selected_pairs_data,
            Sankey_limit1_var=variable_1_max,
            Sankey_limit2_var=variable_2_max,
            Sankey_limit3_var=variable_3_max,
        ),
    )


@app.post("/svo")
def SVO(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    coreferenceResolution: Annotated[bool, Form()] = False,
    manualCoreference: Annotated[bool, Form()] = False,
    package: Annotated[str, Form()] = "Excel",
    lemmatize_subjects: Annotated[bool, Form()] = False,
    filter_subjects: Annotated[bool, Form()] = False,
    lemmatize_verbs: Annotated[bool, Form()] = False,
    filter_verbs: Annotated[bool, Form()] = False,
    lemmatize_objects: Annotated[bool, Form()] = False,
    filter_objects: Annotated[bool, Form()] = False,
    so_gender: Annotated[bool, Form()] = False,
    so_quote: Annotated[bool, Form()] = False,
    google_earth_var: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_svo(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=False,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            coref_var=coreferenceResolution,
            manual_coref_var=manualCoreference,
            normalized_NER_date_extractor_var=False,
            package_var=package,
            gender_var=so_gender,
            quote_var=so_quote,
            subjects_dict_path_var=False,
            verbs_dict_path_var=False,
            objects_dict_path_var=False,
            filter_subjects=filter_subjects,
            filter_verbs=filter_verbs,
            filter_objects=filter_objects,
            lemmatize_subjects=lemmatize_subjects,
            lemmatize_verbs=lemmatize_verbs,
            lemmatize_objects=lemmatize_objects,
            gephi_var=False,
            google_earth_var=google_earth_var,
        ),
    )


@app.post("/wordcloud")
def wordcloud(
    inputDirectory: Annotated[str, Form()],
    wordcloudservice: Annotated[str, Form()],
    font_name: Annotated[str, Form()],
    maxNumberOfWords: Annotated[int, Form()],
    horizontal: Annotated[bool, Form()] = False,
    stopwords: Annotated[bool, Form()] = False,
    lemmas: Annotated[bool, Form()] = False,
    punctuation: Annotated[bool, Form()] = False,
    lowercase_checkbox: Annotated[bool, Form()] = False,
    collocation: Annotated[bool, Form()] = False,
    differentColorsByPOS: Annotated[bool, Form()] = False,
    prepareImage: Annotated[bool, Form()] = False,
    imageContour: Annotated[bool, Form()] = False,
    useColorsForCsvColumns: Annotated[bool, Form()] = False,
    csvField: Annotated[str, Form()] = "[]",
    intermediateWordcloudFiles: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    # csvField arrives as a JSON list of column names and colors, e.g.
    # ["col1", "col2", "(250, 0, 0)", "|"]; an empty/non-JSON value means no selection
    try:
        csvField_color_list = json.loads(csvField)
        if not isinstance(csvField_color_list, list):
            csvField_color_list = []
    except (json.JSONDecodeError, TypeError):
        csvField_color_list = []
    return dispatch(
        app,
        lambda: run_wordcloud(
            "",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            visualization_tools=wordcloudservice,
            prefer_horizontal=horizontal,
            font=font_name,
            max_words=maxNumberOfWords,
            lemmatize=lemmas,
            exclude_stopwords=stopwords,
            exclude_punctuation=punctuation,
            lowercase=lowercase_checkbox,
            collocation=collocation,
            differentPOS_differentColor=differentColorsByPOS,
            prepare_image_var=prepareImage,
            selectedImage="",
            use_contour_only=imageContour,
            differentColumns_differentColors=useColorsForCsvColumns,
            csvField_color_list=csvField_color_list,
            openOutputFiles=False,
            doNotCreateIntermediateFiles=intermediateWordcloudFiles,
        ),
    )


@app.post("/ngrams")
def NGrams_CoOccurrences(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    ngrams_options_list: Annotated[str, Form()] = "[]",
    Ngrams_compute_var: Annotated[bool, Form()] = False,
    ngrams_menu_var: Annotated[str, Form()] = "",
    ngrams_size: Annotated[int, Form()] = 2,
    search_words: Annotated[str, Form()] = "",
    minus_K_words_var: Annotated[int, Form()] = 0,
    plus_K_words_var: Annotated[int, Form()] = 0,
    Ngrams_search_var: Annotated[str, Form()] = "",
    csv_file_var: Annotated[bool, Form()] = False,
    ngrams_viewer_var: Annotated[bool, Form()] = False,
    CoOcc_Viewer_var: Annotated[bool, Form()] = False,
    date_options: Annotated[bool, Form()] = False,
    temporal_aggregation_var: Annotated[str, Form()] = "",
    viewer_options_list: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    csv_path = input_dir if csv_file_var else ""
    return dispatch(
        app,
        lambda: run_ngrams(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=False,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            ngrams_options_list=ngrams_options_list,
            Ngrams_compute_var=Ngrams_compute_var,
            ngrams_menu_var=ngrams_menu_var,
            ngrams_options_menu_var="",
            ngrams_size=ngrams_size,
            search_words=search_words,
            minus_K_words_var=minus_K_words_var,
            plus_K_words_var=plus_K_words_var,
            Ngrams_search_var=Ngrams_search_var,
            csv_file_var=csv_path,
            ngrams_viewer_var=ngrams_viewer_var,
            CoOcc_Viewer_var=CoOcc_Viewer_var,
            date_options=date_options,
            temporal_aggregation_var=temporal_aggregation_var,
            viewer_options_list=viewer_options_list,
            language_list=["English"],
            config_input_output_numeric_options=[1, 0, 0, 1],
            number_of_years=0,
        ),
    )


@app.post("/file_search")
def filesearchword(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    search_options: Annotated[str, Form()] = "",
    minus_K_words_sentences_var: Annotated[int, Form()] = 0,
    plus_K_words_sentences_var: Annotated[int, Form()] = 0,
    search_keyword_values: Annotated[str, Form()] = "",
    selectedCsvFile: Annotated[str, Form()] = "",
    search_by_dictionary: Annotated[bool, Form()] = False,
    search_by_keyword: Annotated[bool, Form()] = False,
    extract_sentences_var: Annotated[bool, Form()] = False,
    coOccurring_keywords_var: Annotated[bool, Form()] = False,
    create_subcorpus_var: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    extract = 1 if extract_sentences_var else 0
    co_occur = 1 if coOccurring_keywords_var else 0
    # the form sends the picked search options as a JSON list, e.g. ["Partial match"]
    search_options_list = json.loads(search_options) if search_options.startswith("[") else []
    return dispatch(
        app,
        lambda: run_search_byWord(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=False,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            search_options=search_options,
            search_by_dictionary=search_by_dictionary,
            selectedCsvFile=selectedCsvFile,
            search_by_keyword=search_by_keyword,
            search_keyword_values=search_keyword_values,
            minus_K_words_sentences_var=minus_K_words_sentences_var,
            plus_K_words_sentences_var=plus_K_words_sentences_var,
            extract_sentences_var=extract,
            coOccurring_keywords_var=co_occur,
            create_subcorpus_var=1 if create_subcorpus_var else 0,
            search_options_menu_var="",
            search_options_list=search_options_list,
            language_list=["English"],
            language="English",
        ),
    )


@app.post("/statistics")
def document_statistics(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    corpus_statistics_var: Annotated[bool, Form()] = False,
    corpus_text_options_menu_var: Annotated[str, Form()] = "*",
    corpus_statistics_options_menu_var: Annotated[str, Form()] = "*",
    corpus_statistics_byPOS_var: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_statistics(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            corpus_statistics_options_menu_var=corpus_statistics_options_menu_var,
            corpus_text_options_menu_var=corpus_text_options_menu_var,
            openOutputFiles=False,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            corpus_statistics_var=corpus_statistics_var,
            corpus_statistics_byPOS_var=corpus_statistics_byPOS_var,
        ),
    )


@app.post("/sentence_analysis")
def sentence_analysis(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    compute_sentence_length_var: Annotated[bool, Form()] = False,
    sentence_complexity_var: Annotated[bool, Form()] = False,
    text_readability_var: Annotated[bool, Form()] = False,
    visualize_sentence_structure_var: Annotated[bool, Form()] = False,
    num_sentences: Annotated[int, Form()] = 1,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_sentence_analysis(
            inputFilename="",
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=False,
            chartPackage="Excel",
            dataTransformation=dataTransformation,
            compute_sentence_length_var=compute_sentence_length_var,
            visualize_bySentenceIndex_var=False,
            visualize_bySentenceIndex_options_var="",
            script_to_run="",
            IO_values="",
            sentence_complexity_var=sentence_complexity_var,
            text_readability_var=text_readability_var,
            visualize_sentence_structure_var=visualize_sentence_structure_var,
            num_sentences=num_sentences,
        ),
    )


@app.post("/gis")
def gis(
    inputDirectory: Annotated[str, Form()],
    dataTransformation: Annotated[str, Form()] = "No transformation",
    NER_extractor: Annotated[bool, Form()] = False,
    geocoder: Annotated[str, Form()] = "Nominatim",
    country_bias_var: Annotated[str, Form()] = "",
    area_var: Annotated[str, Form()] = "e.g.,",
    restrict_var: Annotated[bool, Form()] = False,
    GIS_package_var: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_GIS(
            "",
            input_dir,
            OUTPUT_DIR,
            False,
            "Excel",
            dataTransformation,
            "",
            NER_extractor,
            "",
            geocoder,
            False,
            country_bias_var,
            area_var,
            restrict_var,
            "",
            GIS_package_var,
            False,
        ),
    )


@app.post("/ner")
def ner(
    inputDirectory: Annotated[str, Form()],
    inputFilename: Annotated[str, Form()] = "",
    openOutputFiles: Annotated[bool, Form()] = False,
    chartPackage: Annotated[str, Form()] = "Matplotlib",
    dataTransformation: Annotated[str, Form()] = "No transformation",
    config_filename: Annotated[str, Form()] = "NLP_default_IO_config.csv",
    NER_package: Annotated[str, Form()] = "spaCy",
    NER_list: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    ner_list = [t.strip() for t in NER_list.split(",") if t.strip()]
    return dispatch(
        app,
        lambda: run_NER(
            inputFilename=inputFilename,
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=openOutputFiles,
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            config_filename=config_filename,
            NER_package=NER_package,
            NER_list=ner_list,
        ),
    )


@app.post("/gender")
def gender_analysis(
    inputDirectory: Annotated[str, Form()],
    inputFilename: Annotated[str, Form()] = "",
    openOutputFiles: Annotated[bool, Form()] = False,
    chartPackage: Annotated[str, Form()] = "Excel",
    dataTransformation: Annotated[str, Form()] = "No transformation",
    config_filename: Annotated[str, Form()] = "NLP_default_IO_config.csv",
    CoreNLP_gender_annotator_var: Annotated[bool, Form()] = False,
    annotator_dictionary_var: Annotated[bool, Form()] = False,
    annotator_dictionary_file_var: Annotated[str, Form()] = "",
    personal_pronouns_var: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    dictionary_file = os.path.expanduser(annotator_dictionary_file_var)
    return dispatch(
        app,
        lambda: run_gender_analysis(
            inputFilename=inputFilename,
            input_main_dir_path=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=openOutputFiles,
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            CoreNLP_gender_annotator_var=CoreNLP_gender_annotator_var,
            # download/upload of the CoreNLP gender file is a desktop-only
            # workflow; run() accepts but never reads these
            CoreNLP_download_gender_file_var=False,
            CoreNLP_upload_gender_file_var=False,
            annotator_dictionary_var=annotator_dictionary_var,
            annotator_dictionary_file_var=dictionary_file,
            personal_pronouns_var=personal_pronouns_var,
            # the US SS plot path needs lib/namesGender data not shipped with the agent
            plot_var=False,
            year_state_var="",
            firstName_entry_var="",
            new_SS_folders=[],
            config_filename=config_filename,
        ),
    )


@app.post("/wordnet")
def wordnet(
    inputDirectory: Annotated[str, Form()],
    inputFilename: Annotated[str, Form()] = "",
    openOutputFiles: Annotated[bool, Form()] = False,
    chartPackage: Annotated[str, Form()] = "Excel",
    dataTransformation: Annotated[str, Form()] = "No transformation",
    csv_file: Annotated[str, Form()] = "",
    aggregate_POS_var: Annotated[bool, Form()] = False,
    noun_verb: Annotated[str, Form()] = "NOUN",
    disaggregate_var: Annotated[bool, Form()] = False,
    wordNet_keyword_list: Annotated[str, Form()] = "",
    annotate_file_var: Annotated[bool, Form()] = False,
    extract_proper_nouns: Annotated[bool, Form()] = False,
    extract_improper_nouns: Annotated[bool, Form()] = False,
    aggregate_lemmatized_var: Annotated[bool, Form()] = False,
    extract_nouns_verbs_from_CoNLL_var: Annotated[bool, Form()] = False,
    aggregate_bySentenceID_var: Annotated[bool, Form()] = False,
    dict_WordNet_filename_var: Annotated[str, Form()] = "",
    hidden_noun_lemma_csv: Annotated[str, Form()] = "",
    hidden_verb_lemma_csv: Annotated[str, Form()] = "",
    noun_verb_menu_var: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    keyword_list = [k.strip() for k in wordNet_keyword_list.split(",") if k.strip()]
    # the form sends these as text paths (browser file inputs only submit bare filenames)
    csv_file = os.path.expanduser(csv_file)
    dict_WordNet_filename_var = os.path.expanduser(dict_WordNet_filename_var)
    return dispatch(
        app,
        lambda: run_kg_wordnet(
            inputFilename=inputFilename,
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=openOutputFiles,
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            csv_file=csv_file,
            aggregate_POS_var=aggregate_POS_var,
            noun_verb=noun_verb,
            disaggregate_var=disaggregate_var,
            wordNet_keyword_list=keyword_list,
            annotate_file_var=annotate_file_var,
            extract_proper_nouns=extract_proper_nouns,
            extract_improper_nouns=extract_improper_nouns,
            aggregate_lemmatized_var=aggregate_lemmatized_var,
            extract_nouns_verbs_from_CoNLL_var=extract_nouns_verbs_from_CoNLL_var,
            aggregate_bySentenceID_var=aggregate_bySentenceID_var,
            dict_WordNet_filename_var=dict_WordNet_filename_var,
            hidden_noun_lemma_csv=hidden_noun_lemma_csv,
            hidden_verb_lemma_csv=hidden_verb_lemma_csv,
            noun_verb_menu_var=noun_verb_menu_var,
        ),
    )


@app.post("/stories")
def shape_of_stories(
    inputDirectory: Annotated[str, Form()],
    inputFilename: Annotated[str, Form()] = "",
    openOutputFiles: Annotated[bool, Form()] = False,
    chartPackage: Annotated[str, Form()] = "Excel",
    dataTransformation: Annotated[str, Form()] = "No transformation",
    sentimentAnalysis: Annotated[bool, Form()] = False,
    sentimentAnalysisMethod: Annotated[str, Form()] = "BERT",
    memory_var: Annotated[int, Form()] = 1,
    corpus_analysis: Annotated[bool, Form()] = False,
    hierarchical_clustering: Annotated[bool, Form()] = False,
    SVD: Annotated[bool, Form()] = False,
    NMF: Annotated[bool, Form()] = False,
    best_topic_estimation: Annotated[bool, Form()] = False,
) -> PlainTextResponse:
    input_dir = os.path.expanduser(inputDirectory)
    return dispatch(
        app,
        lambda: run_shape_of_stories(
            inputFilename=inputFilename,
            inputDir=input_dir,
            outputDir=OUTPUT_DIR,
            openOutputFiles=openOutputFiles,
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            sentimentAnalysis=sentimentAnalysis,
            sentimentAnalysisMethod=sentimentAnalysisMethod,
            memory_var=memory_var,
            corpus_analysis=corpus_analysis,
            hierarchical_clustering=hierarchical_clustering,
            SVD=SVD,
            NMF=NMF,
            best_topic_estimation=best_topic_estimation,
        ),
    )


@app.post("/excel_charts")
def excel_plotly_charts(
    inputFilename: Annotated[str, Form()],
    csv_field_visualization_var: Annotated[str, Form()] = "",
    X_axis_var: Annotated[str, Form()] = "",
    csv_file_field_Y_axis_list: Annotated[str, Form()] = "[]",
    charts_type_options: Annotated[str, Form()] = "bar",
    chartPackage: Annotated[str, Form()] = "Plotly",
    dataTransformation: Annotated[str, Form()] = "No transformation",
    inputFileData: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    # the form sends the Y-axis fields as a JSON list, e.g. ["valence"]
    y_axis_list = json.loads(csv_file_field_Y_axis_list or "[]")
    return dispatch(
        app,
        lambda: run_excel_plotly_charts(
            inputFilename=inputFilename,
            outputDir=OUTPUT_DIR,
            csv_field_visualization_var=csv_field_visualization_var,
            X_axis_var=X_axis_var,
            csv_file_field_Y_axis_list=y_axis_list,
            charts_type_options=charts_type_options,
            chart_package=chartPackage,
            data_transformation=dataTransformation,
            inputFileData=inputFileData,
        ),
    )


@app.post("/boxplot")
def boxplot(
    inputFilename: Annotated[str, Form()],
    csv_field_visualization_var: Annotated[str, Form()] = "",
    points_var: Annotated[str, Form()] = "",
    split_data_byCategory_var: Annotated[bool, Form()] = False,
    csv_field_boxplot_var: Annotated[str, Form()] = "",
    csv_field_boxplot_color_var: Annotated[str, Form()] = "",
    inputFileData: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    return dispatch(
        app,
        lambda: run_boxplot(
            inputFilename=inputFilename,
            outputDir=OUTPUT_DIR,
            csv_field_visualization_var=csv_field_visualization_var,
            points_var=points_var,
            split_data_byCategory_var=split_data_byCategory_var,
            csv_field_boxplot_var=csv_field_boxplot_var,
            csv_field_boxplot_color_var=csv_field_boxplot_color_var,
            inputFileData=inputFileData,
        ),
    )


@app.get("/settings")
def get_settings() -> JSONResponse:
    def mask(val: str) -> str:
        return ("*" * (len(val) - 4) + val[-4:]) if len(val) > 4 else ("*" * len(val))

    return JSONResponse(
        {
            "google_maps_api_key": mask(GOOGLE_MAPS_API_KEY),
            "nyt_api_key": mask(NYT_API_KEY),
        }
    )


@app.post("/settings")
def save_settings(
    google_maps_api_key: Annotated[str, Form()] = "",
    nyt_api_key: Annotated[str, Form()] = "",
) -> PlainTextResponse:
    global GOOGLE_MAPS_API_KEY, NYT_API_KEY
    GOOGLE_MAPS_API_KEY = google_maps_api_key
    NYT_API_KEY = nyt_api_key
    os.environ["GOOGLE_MAPS_API_KEY"] = google_maps_api_key
    os.environ["NYT_API_KEY"] = nyt_api_key
    _write_env_file(google_maps_api_key, nyt_api_key)
    return PlainTextResponse("", status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, port=3000, host="0.0.0.0")
