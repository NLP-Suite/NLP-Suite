import os

import requests
from django.contrib import messages
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.template import loader

AGENT_SERVER_URL = os.getenv("AGENT_SERVER_URL", "http://172.16.0.11:3000")

# The agent dispatches jobs to a background thread and responds immediately,
# so this only needs to cover connection setup and form parsing.
AGENT_TIMEOUT_SECONDS = 30


def _proxy_post(request: HttpRequest, path: str, template_name: str):
    """Forward a POST form body to the agent and redirect to /status.

    On GET (or after an error message is queued), render the form template.
    """
    if request.method == "POST":
        try:
            response = requests.post(
                f"{AGENT_SERVER_URL}{path}",
                data=request.body,
                headers=request.headers,
                timeout=AGENT_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            messages.add_message(request, messages.ERROR, f"Could not reach the NLP agent: {exc}")
        else:
            if response.ok:
                return HttpResponseRedirect("/status")
            messages.add_message(request, messages.ERROR, response.content.decode())
    return render(request, template_name)


def index(_: HttpRequest):
    template = loader.get_template("../templates/index.html")
    return HttpResponse(template.render())


def contact(_: HttpRequest):
    template = loader.get_template("../templates/contact.html")
    return HttpResponse(template.render())


def status(request: HttpRequest):
    return render(request, "status.html")


def status_poll(_: HttpRequest):
    """Proxy the agent's /status for the browser, which cannot reach the agent's
    Docker-internal address directly."""
    try:
        resp = requests.get(f"{AGENT_SERVER_URL}/status", timeout=5)
        return JsonResponse(resp.json())
    except (requests.RequestException, ValueError):
        return JsonResponse({"unreachable": True}, status=502)


def sentiment_analysis(request: HttpRequest):
    return _proxy_post(request, "/sentiment_analysis", "sentiment_analysis.html")


def SVO(request: HttpRequest):
    return _proxy_post(request, "/svo", "SVO.html")


def shape_of_stories(request: HttpRequest):
    return _proxy_post(request, "/stories", "shape_of_stories.html")


def style_analysis(request: HttpRequest):
    return _proxy_post(request, "/style_analysis", "style_analysis.html")


def topic_modeling(request: HttpRequest):
    return _proxy_post(request, "/topic_modeling", "topic_modeling.html")


def NGrams_CoOccurrences(request: HttpRequest):
    return _proxy_post(request, "/ngrams", "NGrams_CoOccurrences.html")


def parsers_annotators(request: HttpRequest):
    return _proxy_post(request, "/parse", "parsers_annotators.html")


def wordclouds(request: HttpRequest):
    return _proxy_post(request, "/wordcloud", "wordclouds.html")


def word2vec(request: HttpRequest):
    return _proxy_post(request, "/word2vec", "word2vec.html")


def wordnet(request: HttpRequest):
    return _proxy_post(request, "/wordnet", "wordnet.html")


def filesearchword(request: HttpRequest):
    return _proxy_post(request, "/file_search", "filesearchword.html")


def gis(request: HttpRequest):
    return _proxy_post(request, "/gis", "gis.html")


def genderanalysis(request: HttpRequest):
    return _proxy_post(request, "/gender", "gender_analysis.html")


def NER(request: HttpRequest):
    return _proxy_post(request, "/ner", "NER.html")


def sunburst_charts(request: HttpRequest):
    return _proxy_post(request, "/sunburst", "sunburst_charts.html")


def sankey_flowchart(request: HttpRequest):
    return _proxy_post(request, "/sankey", "sankey_flowchart.html")


def boxplot(request: HttpRequest):
    return _proxy_post(request, "/boxplot", "boxplot.html")


def colormap_chart(request: HttpRequest):
    return _proxy_post(request, "/colormap", "colormap_chart.html")


def excel_plotly_charts(request: HttpRequest):
    return _proxy_post(request, "/excel_charts", "excel_plotly_charts.html")


def conll_table_analyzer_main(request: HttpRequest):
    return _proxy_post(request, "/conll_table", "CoNLL_table_analyzer_main.html")


def document_statistics(request: HttpRequest):
    return _proxy_post(request, "/statistics", "document_statistics.html")


def sentence_analysis(request: HttpRequest):
    return _proxy_post(request, "/sentence_analysis", "sentence_analysis.html")


def file_manager(request: HttpRequest):
    return _proxy_post(request, "/file_manager", "file_manager.html")


def settings(request: HttpRequest):
    if request.method == "POST":
        try:
            response = requests.post(
                f"{AGENT_SERVER_URL}/settings",
                data=request.POST,
                timeout=10,
            )
        except requests.RequestException as exc:
            messages.add_message(request, messages.ERROR, f"Could not reach the NLP agent: {exc}")
        else:
            if response.ok:
                messages.add_message(request, messages.SUCCESS, "Settings saved.")
            else:
                messages.add_message(request, messages.ERROR, response.content.decode())
        return HttpResponseRedirect("/settings")
    current = {}
    try:
        resp = requests.get(f"{AGENT_SERVER_URL}/settings", timeout=5)
        if resp.ok:
            current = resp.json()
    except requests.RequestException:
        pass
    return render(request, "settings.html", {"current": current})
