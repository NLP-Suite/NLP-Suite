import pytest

try:
    from NER_main import run_NER
except (ImportError, SystemExit):
    pytest.skip("NER_main dependencies not available", allow_module_level=True)


def test_ner_spacy(fixture_txt, tmp_output):
    run_NER(
        inputFilename=str(fixture_txt),
        inputDir=str(fixture_txt.parent),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="Matplotlib",
        dataTransformation="No transformation",
        config_filename="NLP_default_IO_config.csv",
        NER_package="spaCy",
        NER_list=[],
    )
