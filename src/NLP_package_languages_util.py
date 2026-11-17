"""The languages each NLP package supports, as plain data.

No Tk, Stanza or spaCy import, so the menu's language advisor can read these lists without loading the packages
(issue #1731). Stanza_util and spaCy_util import their lists from here.
"""

# Stanza: language codes with a dependency parser, sentiment and NER model
available_ud = [
    "af",
    "grc",
    "ar",
    "hy",
    "eu",
    "be",
    "bg",
    "ca",
    "zh",  # has an alias called zh-hans
    "zh-hans",  # has an alias called zh-hans
    # "zh-hant", traditional_chinese has hardly any processes
    "lzh",
    "cop",
    "hr",
    "cs",
    "da",
    "nl",
    "en",
    "et",
    "fi",
    "fr",
    "gl",
    "de",
    "got",
    "el",
    "he",
    "hi",
    "hu",
    "id",
    "ga",
    "it",
    "ja",
    "ko",
    "la",
    "lv",
    "lt",
    "mt",
    "mr",
    "sme",
    "no",
    "nb",
    "nn",
    "cu",
    "fro",
    "orv",
    "fa",
    "pl",
    "pt",
    "ro",
    "ru",
    "gd",
    "sr",
    "sk",
    "sl",
    "es",
    "sv",
    "ta",
    "te",
    "tr",
    "uk",
    "ur",
    "ug",
    "vi",
    "wo",
]

available_sentiment = ["de", "en", "zh", "zh-hans"]

available_NER = [
    "af",
    "ar",
    "bg",
    "zh",
    "zh-hans",
    "da",
    "nl",
    "en",
    "fi",
    "fr",
    "de",
    "hu",
    "it",
    "ja",
    "my",
    "nb",
    "nn",
    "fa",
    "ru",
    "es",
    "sv",
    "tr",
    "uk",
    "vi",
]

# spaCy: language codes with a model
spacy_available_lang = [
    "xx",  # mult-language has different rest of model name
    "ca",
    "zh",
    "hr",
    "da",
    "nl",
    "en",
    "fi",
    "fr",
    "de",
    "el",
    "it",
    "ja",
    "ko",
    "lt",
    "mk",
    "nb",
    "pl",
    "pt",
    "ro",
    "ru",
    "es",
    "sv",
    "uk",
]


def stanza_display_name(lang_name):
    """A Stanza language name as the Setup lists it: variants after the language, so they sort together
    (e.g. Simplified_Chinese -> Chinese_Simplified)."""
    for language in ("_Chinese", "_French", "_Greek", "_Hebrew", "_Russian"):
        if language in lang_name:
            return lang_name.split("_")[-1] + "_" + lang_name.split("_")[0]
    return lang_name


def stanza_display_names(lang_names):
    """Sorted display names of Stanza's languages (the lang_name values of its resources.json), without
    Chinese_Traditional, which handles very few annotators."""
    names = (stanza_display_name(name) for name in lang_names)
    return sorted(name for name in names if "Chinese_Traditional" not in name)


def spacy_language_names():
    """Sorted full names of the languages spaCy has a model for."""
    import constants_util

    names = dict(constants_util.languages)
    return sorted(names[code] for code in spacy_available_lang)
