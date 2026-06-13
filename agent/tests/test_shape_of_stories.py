import pytest

try:
    from shape_of_stories_main import run as run_shape_of_stories
except (ImportError, SystemExit):
    pytest.skip("shape_of_stories_main dependencies not available", allow_module_level=True)


def test_shape_of_stories_bert(fixture_txt, tmp_output):
    run_shape_of_stories(
        inputFilename=str(fixture_txt),
        inputDir=str(fixture_txt.parent),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="Matplotlib",
        dataTransformation="No transformation",
        sentimentAnalysis=True,
        sentimentAnalysisMethod="BERT",
        memory_var=1,
        corpus_analysis=False,
        hierarchical_clustering=False,
        SVD=False,
        NMF=False,
        best_topic_estimation=False,
    )


@pytest.mark.integration
def test_shape_of_stories_corenlp(fixture_txt, tmp_output, corenlp_running):
    run_shape_of_stories(
        inputFilename=str(fixture_txt),
        inputDir=str(fixture_txt.parent),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="Matplotlib",
        dataTransformation="No transformation",
        sentimentAnalysis=True,
        sentimentAnalysisMethod="Stanford CoreNLP",
        memory_var=1,
        corpus_analysis=False,
        hierarchical_clustering=False,
        SVD=False,
        NMF=False,
        best_topic_estimation=False,
    )
