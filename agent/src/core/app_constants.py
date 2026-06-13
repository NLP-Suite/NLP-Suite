import os
from pathlib import Path

NLP_SUITE_ROOT = os.path.join(os.path.expanduser("~"), "nlp-suite")

MALLET_URL = "http://172.16.0.13:5050/run"

# Stanford CoreNLP service; the default resolves via Docker network DNS.
CORENLP_URL = os.environ.get("CORENLP_URL", "http://corenlp:9000")

NLP_DEFAULT_IO_CONFIG = "NLP_default_IO_config.csv"
NLP_DEFAULT_PACKAGE_LANG_CONFIG = "NLP_default_package_language_config.csv"

WORD_LISTS_DIR = Path(__file__).parent.parent.parent / "lib" / "wordLists"

LOCATION_NER_TAGS = {"LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"}

CONTINENTS = {"Africa", "Antarctica", "Asia", "Australia", "Europe", "North America", "South America", "Oceania"}
