# Supported Systems & Languages

## Supported Operating Systems

| Platform | Status | Notes |
|----------|--------|-------|
| **Windows 10/11** (64-bit) | Fully supported | Standalone build available |
| **macOS** (Apple Silicon — M1/M2/M3/M4/M5) | Fully supported | Standalone build available |
| **macOS** (Intel) | Run from source | No standalone build currently provided; may be added if needed |
| **Linux** | Run from source | Not tested extensively; should work with the developer setup |

## Supported Languages

The NLP Suite supports **60+ languages** through integration with multiple NLP packages:

| Package | Languages | Used for |
|---------|-----------|----------|
| **Stanza** | 60+ languages | Tokenization, POS tagging, NER, lemmatization, dependency parsing, sentiment analysis |
| **spaCy** | 20+ languages | Tokenization, POS tagging, NER, lemmatization |
| **BERT** | English + Multilingual | Sentiment analysis (English and multilingual models) |

### English-only features

Some dictionary-based algorithms are available only for English:

- WordNet (noun/verb aggregation)
- ANEW (sentiment/arousal/dominance)
- Hedonometer (sentiment)
- VADER (sentiment)
- NRC Emotion Wheel (8-emotion analysis)
- SentiWordNet (sentiment)
- Style analysis (concreteness, iconicity)

### Setting your language

The NLP Suite language is configured in the **Setup NLP package and corpus language** dialog, accessible from the Setup menu at the bottom of most GUIs. The default is English with Stanza.
