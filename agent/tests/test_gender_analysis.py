import pytest

# html_annotator_gender_main imports GUI_util (tkinter) at module level and
# some deps call sys.exit(0) on missing packages; skip if import fails.
try:
    from html_annotator_gender_main import run as run_gender_analysis
except (ImportError, SystemExit):
    pytest.skip("html_annotator_gender_main dependencies not available", allow_module_level=True)


@pytest.mark.integration
def test_gender_analysis_corenlp(fixture_txt, tmp_output, corenlp_running):
    run_gender_analysis(
        inputFilename=str(fixture_txt),
        input_main_dir_path=str(fixture_txt.parent),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="Matplotlib",
        dataTransformation="No transformation",
        CoreNLP_gender_annotator_var=True,
        CoreNLP_download_gender_file_var=False,
        CoreNLP_upload_gender_file_var=False,
        annotator_dictionary_var=False,
        annotator_dictionary_file_var="",
        personal_pronouns_var=False,
        plot_var=False,
        year_state_var="",
        firstName_entry_var="",
        new_SS_folders=[],
    )
