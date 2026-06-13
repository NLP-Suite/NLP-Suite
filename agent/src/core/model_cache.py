"""Process-wide cache for heavy NLP models (stanza, spaCy, SentenceTransformer).

Each request used to construct its pipelines from scratch; model loads dominated
small-corpus job time. The cache is a plain unbounded dict by design: the agent's
single-job lock means no concurrent model use, a single researcher touches a
handful of model/processor combinations, and an agent restart clears it.
"""

import logging
import threading

logger = logging.getLogger(__name__)

_CACHE = {}
_LOCK = threading.Lock()


def _get_or_create(key, factory):
    try:
        return _CACHE[key]
    except KeyError:
        pass
    with _LOCK:
        if key not in _CACHE:
            logger.info("Loading model %s", key)
            _CACHE[key] = factory()
        return _CACHE[key]


def get_stanza_pipeline(lang="en", processors="tokenize", **kwargs):
    import stanza

    processors = processors.replace(" ", "")
    key = ("stanza", lang, processors, tuple(sorted(kwargs.items())))
    return _get_or_create(key, lambda: stanza.Pipeline(lang=lang, processors=processors, **kwargs))


def get_spacy_model(name="en_core_web_sm", disable=()):
    import spacy

    key = ("spacy", name, tuple(disable))
    return _get_or_create(key, lambda: spacy.load(name, disable=list(disable)))


def get_sentence_transformer(name="all-MiniLM-L6-v2"):
    from sentence_transformers import SentenceTransformer

    key = ("sentence_transformer", name)
    return _get_or_create(key, lambda: SentenceTransformer(name))


def get_hf_pipeline(task, model_name, **kwargs):
    from transformers import pipeline

    key = ("hf_pipeline", task, model_name, tuple(sorted(kwargs.items())))
    return _get_or_create(key, lambda: pipeline(task, model=model_name, tokenizer=model_name, **kwargs))
