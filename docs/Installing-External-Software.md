### NLP Suite  ![GitHub release (latest by date)](https://img.shields.io/github/v/release/NLP-Suite/NLP-Suite?color=Green&label=Latest%20Version)  

# Install External Software

The standalone NLP Suite build bundles most of what you need. The tools listed below are **optional** — install them only if you need the specific functionality they provide.

## Optional External Software

| Tool | When needed | Alternative already included | Download |
|------|------------|------------------------------|----------|
| **Stanford CoreNLP** | Only if you select CoreNLP as your NLP package for parsing, NER, or sentiment analysis | **Stanza** does the same tasks, is bundled, and requires no Java | [stanford.edu](https://stanfordnlp.github.io/CoreNLP/) |
| **Java JDK** | Only if you use Stanford CoreNLP | Not needed if you use Stanza | [oracle.com](https://www.oracle.com/java/technologies/downloads/) |
| **Google Earth Pro** | For KML map visualizations | **Folium** (bundled) creates interactive HTML maps automatically when Google Earth is not installed | [google.com/earth](https://www.google.com/earth/about/versions/#earth-pro) |
| **Google Maps API key** | For Google Maps visualizations | **Folium** (bundled) is used automatically as a fallback | [developers.google.com](https://developers.google.com/maps/documentation/javascript/get-api-key) |
| **Gephi** | For interactive network graph exploration | **vis.js** (bundled) produces interactive HTML network graphs | [gephi.org](https://gephi.org/users/download/) |
| **MALLET** | For LDA topic modeling via MALLET | **Gensim LDA** (bundled) provides topic modeling without external software | [mallet.cs.umass.edu](http://mallet.cs.umass.edu/download.php) |

## No Longer Required

The following tools were previously required but are now bundled or replaced:

| Tool | Status |
|------|--------|
| **WordNet** | Bundled via NLTK — no separate download needed |
| **Anaconda / Python** | Bundled in the standalone build |
| **Git** | Only needed for developer setup (running from source) |
| **Microsoft C++ Redistributable** | Usually pre-installed on Windows 10/11. Install only if you get a DLL error (see [Troubleshooting](https://github.com/NLP-Suite/NLP-Suite/wiki/Troubleshooting)) |

## When the NLP Suite Prompts You

If you select a feature that requires external software (e.g., Stanford CoreNLP), the NLP Suite will detect that the software is not installed and either:

1. **Automatically fall back** to the bundled alternative (e.g., Folium instead of Google Earth), or
2. **Show a message** explaining what to install and where to download it

You do not need to install external software in advance.
