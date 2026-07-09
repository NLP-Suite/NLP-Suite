# NLP Suite — Changelog

The most recent release is at the top. Each release's bullets are shown as **"What's new"**
on the corresponding GitHub Release page (the top section is added automatically by the
release workflow). Keep the newest version's section at the very top and update it before tagging.

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
