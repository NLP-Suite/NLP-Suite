from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("contact", views.contact, name="contact"),
    path("status", views.status, name="status"),
    path("status/poll", views.status_poll, name="status_poll"),
    path("sentiment_analysis", views.sentiment_analysis, name="sentiment_analysis"),
    path("svo", views.SVO, name="svo"),
    path("stories", views.shape_of_stories, name="stories"),
    path("style_analysis", views.style_analysis, name="style_analysis"),
    path("topic_modeling", views.topic_modeling, name="topic_modeling"),
    path("ngrams", views.NGrams_CoOccurrences, name="ngrams"),
    path("conll_table", views.conll_table_analyzer_main, name="conll_table"),
    path("parse", views.parsers_annotators, name="parse"),
    path("wordcloud", views.wordclouds, name="wordcloud"),
    path("word2vec", views.word2vec, name="word2vec"),
    path("wordnet", views.wordnet, name="wordnet"),
    path("file_search", views.filesearchword, name="file_search"),
    path("gis", views.gis, name="gis"),
    path("gender_analysis", views.genderanalysis, name="gender_analysis"),
    path("NER", views.NER, name="NER"),
    path("sunburst", views.sunburst_charts, name="sunburst"),
    path("sankey", views.sankey_flowchart, name="sankey"),
    path("boxplot", views.boxplot, name="boxplot"),
    path("colormap", views.colormap_chart, name="colormap"),
    path("excel_charts", views.excel_plotly_charts, name="excel_charts"),
    path("statistics", views.document_statistics, name="statistics"),
    path("sentence_analysis", views.sentence_analysis, name="sentence_analysis"),
    path("file_manager", views.file_manager, name="file_manager"),
    path("settings", views.settings, name="settings"),
]
