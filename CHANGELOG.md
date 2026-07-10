# NLP Suite — Changelog

The most recent release is at the top. Each release's bullets are shown as **"What's new"**
on the corresponding GitHub Release page (the top section is added automatically by the
release workflow). Keep the newest version's section at the very top and update it before tagging.

## v1.6.4
- **SVO extraction — many fixes.** The **gender** and **quote/speaker** annotators now work (they were crashing while writing their output files), and gender values populate correctly. Running SVO **with coreference resolution** no longer errors. The social-actor **Filter** actually filters (it was a no-op in some paths). An internal processing tag no longer leaks into charts and wordclouds. The **character-movement map** now displays your locations (it was opening blank), can be restricted to social actors, and labels what the moving items are.
- **Quote/dialogue annotator rewritten.** One row **per quote** — it no longer drops extra quotes in the same sentence or duplicates a quote that spans several sentences — and speakers are resolved to the actual name where possible instead of a bare pronoun.
- **Annotators run without a Setup detour.** Ticking a CoreNLP-only annotator (gender, quote, normalized NER date, OpenIE) now runs it via Stanford CoreNLP automatically, whatever your default package.
- **CoNLL Table Analyzer — repetition finder.** The **Begin K / End K** sentence-count fields now appear only when the repetition-finder analysis is selected (with a hover explaining them).
- **"By Document" charts fixed.** Multi-value distributions charted *by Document* (e.g., NER date types) now produce a proper **grouped bar chart** — one colored series per document, clean document names in the legend, a "Frequencies" y-axis — or field totals when there are too many documents/values to chart legibly. This removes the long-standing empty/duplicate series whose values only showed up in the data sheet. *(Good area to spot-check: the Normalized NER date annotator and any "… by Document" analyses.)*
- **Wordclouds:** multi-word expressions (e.g., proper names) now read as clean joined units instead of running together.

## v1.6.3
- **Faster corpus & sentence statistics charts.** The tools that build per-sentence charts (sentence complexity, subordination) no longer re-run the language model on every document just to count its sentences — a large speed-up on multi-document corpora, with identical results.
- **Fixed a crash in "What's in your corpus → sentence complexity".** It was trying to reinstall an old version of a language library at run time and failing; it now downloads the needed model instead.
- **Chart engine modernization (behind the scenes).** ~100 chart-producing tools were moved onto a cleaner internal chart interface. Charts look and behave exactly the same, but the code is far simpler and several long-standing chart bugs and dead code paths were removed. *(A good area to spot-check while testing: run a few tools that produce charts — POS/verb/adverb analyses, sentiment, parser visualizations — and confirm the Excel charts still open correctly.)*

## v1.6.2
- **Under-the-hood modernization of every tool.** All ~50 GUIs had their **RUN** button rewired to a simpler, more reliable pattern. Nothing changes in how you use the tools — but it removes a long-standing source of bugs and makes future fixes safer.
- **CoNLL Table Analyzer:** you can now run the **Basic and Advanced analyses together** in a single pass, instead of one at a time.
- **GIS distances:** fixed a crash in the **"distance from a baseline location"** mode when the corpus contained places that couldn't be geocoded — those are now skipped cleanly.
- Release-page and housekeeping improvements (dated release titles, a clearer "What's new" section).

## v1.6.1
- **Geographic distances (GIS) tool fully overhauled.** It now works directly on a geocoded corpus and offers three analyses on the same file:
  - distances between **all pairs** of places — within each document, across the whole corpus, or both;
  - distances **from a chosen location** (e.g., how far each place is from New York);
  - **movement** distances between successive places in a story (how far characters travel).
  Results open as readable distribution charts and are saved to their own subfolder.
- **Clearer bar charts across the Suite.** When a chart would show a wall of individual numeric values (distances, sentence lengths, scores…), the values are now grouped into readable ranges/classes.
- **Friendlier file selection.** Picking an input lists the relevant files found for your corpus, with buttons to open a file, remove empty leftover files, or browse — starting in the right folder.
- **Housekeeping.** Removed obsolete one-off scripts and fixed several long-standing bugs (chart generation, coordinate handling, Windows file-name length limits).

## v1.6.0
- **New tool: Narrative / Symbolic space.** Analyze characters moving through non-geocodable narrative space (house, field, forest, threshold), complementing the geographic GIS mapping.
- Fixes to the frozen Windows and Mac installers reported in testing.
