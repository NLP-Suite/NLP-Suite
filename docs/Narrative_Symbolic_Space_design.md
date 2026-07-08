# Narrative / Symbolic Space Analyzer — design memo

**Status:** design only (not yet implemented).
**Author:** Roberto Franzosi & Claude, 2026-07-07.

## 1. The research question

The suite's spatial analysis (NER locations → Nominatim geocoding → GIS map)
answers **"where on Earth"**. But much narrative text — folktales above all —
encodes **"where in the social / narrative world"**. *Kitchen vs. field* is not
a coordinate; it is a **semantic space**, and it is **gendered** (women in the
kitchen, men in the field). Fanciful settings (the forest, the castle, "the land
where no one returns") have no lat/long at all.

The key move: **stop treating non-geocodable places as failed geocodes and start
treating them as the signal.** The geocoder's *residue* is exactly the symbolic /
fanciful set worth analyzing.

This tool adds three analyses on top of the existing map:
1. a **spatial-domain typology** (what *kind* of space a place is),
2. a **gender × space** cross-tabulation (the gendered division of narrative
   space, quantified), and
3. a **narrative-space transition graph** (the Proppian home→forest→castle→home
   movement) — the folktale analogue of the migration map.

## 2. What it reuses (nothing is built from scratch)

| Need | Existing machinery |
|---|---|
| Place mentions | `NER_main` LOC/GPE/FAC tags (`_LOCATION_TAGS`); CoNLL NER |
| Actor–action–place triples | `SVO_main` (subject-verb-object) + CoNLL dependency args for locatives (`obl`, `nmod:in/at/on`) |
| Parsing | `parsers_annotators_main` → CoNLL (configured package) |
| Real-place resolution | GIS / Nominatim geocoding (`GIS_*`) |
| Actor gender | `html_annotator_gender_main` + SSA / CoreNLP gender dictionaries; coreference for pronouns |
| Semantic categories | `semantic_aggregation` knowledge-base dispatcher (WordNet / VerbNet / FrameNet) |
| WordNet hypernyms | `semantic_aggregation_WordNet_util` (to seed the typology) |
| Stats | `statistics_csv` (chi-square, Cramér's V, standardized residuals) |
| Charts | `charts_util` / `charts_Plotly_util` (heatmap, mosaic, bipartite network, Sankey) |
| Gazetteers | `lib/*.csv` (as `lib/VerbNet_classes.csv`, `lib/FrameNet_frames.csv` do) |

## 3. Pipeline

```
corpus (txt) ──▶ parser ──▶ CoNLL ──┬─▶ NER locations ─┐
                                    └─▶ SVO triples ────┤
                                                        ▼
                        (agent, verb, location) + place-mention list
                                                        │
                              ┌─────────── Stage 1: split at geocoding ───────────┐
                              ▼                                                    ▼
                    geocodable places                                   NON-geocodable residue
                    → existing GIS map                                  → symbolic pipeline (below)
```

### Stage 1 — Split geocodable vs symbolic
Run every place mention through Nominatim (as the GIS tool does today).
- **Resolves** → real place → hand to the existing GIS map.
- **Fails** → symbolic / fanciful → the pipeline below.

*Guard:* the split is a heuristic. Some real places fail (typos, historical
names) and some symbolic terms accidentally resolve ("Kitchen" is a hamlet
somewhere). So Stage 2 runs on **all** mentions: if a term matches a symbolic
category, it is treated as symbolic even when it weakly geocodes. Geocoding
narrows; the typology decides.

### Stage 2 — Spatial-domain typology (the new knowledge base)
A gazetteer mapping location nouns → **space types**, e.g.:

| Category | Anchor terms |
|---|---|
| domestic / interior | kitchen, hearth, bedroom, house, cottage, chamber |
| field / outdoor-labor | field, farm, meadow, pasture, mill |
| wild / forest | forest, woods, wilderness, mountain, cave |
| threshold / liminal | door, gate, bridge, crossroads, well, shore, edge |
| royal / court | castle, palace, throne, court, tower |
| sacred | church, temple, altar, shrine, grave |
| market / public | market, square, road, town, inn, tavern |
| water / passage | river, sea, path, road |

- **Stored** as `lib/symbolic_space_typology.csv` (columns: `term`, `category`,
  `source` = wordnet|curated), editable like the other lib gazetteers.
- **Seeded** from WordNet hypernyms (kitchen→room→area; field→tract→geographical
  area) via `semantic_aggregation_WordNet_util`, then hand-curated for the
  folktale domain.
- **Classifier** (`symbolic_space_typology_util.classify(lemma)`): exact lexicon
  hit first, else walk the WordNet hypernym path and match any ancestor synset
  to a category's anchor synsets, else `unclassified`.
- **Hangs off** the `semantic_aggregation` KB dispatcher as a new **"Spatial
  domain"** knowledge base, beside WordNet / VerbNet / FrameNet.

### Stage 3 — Gender of the actor
For each SVO subject/agent, assign M / F / unknown:
- NER PERSON + **first-name → gender** (reuse the SSA name dictionaries already
  in `html_annotator_gender`),
- **honorifics / kin terms** (Mr/Mrs, king/queen, mother/father, miller's
  daughter → F),
- **coreference** to propagate a named entity's gender onto its pronouns.

### Stage 4 — Gender × space cross-tab (the core result)
Contingency table: rows = gender, columns = space category, cell =
co-occurrence count of (agent-gender, action-location-category) from the triples.
- **Test:** chi-square + Cramér's V; standardized residuals flag the
  over/under-represented cells (women↔kitchen high, men↔field high) — reuse
  `statistics_csv`.
- **Charts:** mosaic plot / heatmap, plus a **bipartite gender↔space network**
  (edge weight = co-occurrence).

### Stage 5 — FrameNet convergence (a second, independent measure)
Each clause evokes a FrameNet frame (existing FrameNet / SRL route). Cross-tab
**gender × frame**: Cooking / Agriculture / Travel / Combat clustering by gender
converges with the space result.

### Stage 6 — Narrative-space transition graph
Per tale, order the (typed) settings by narrative position; build a **directed
transition graph** (node = space category, edge = setting→next-setting).
Aggregate across the corpus → the Proppian "narrative space" map
(home→forest→castle→home). **Chart:** directed graph / Sankey of transitions
(Gephi export like the SVO network).

## 4. Inputs / outputs

**Input:** a corpus of `.txt` files, or an existing CoNLL table / NER+SVO output.

**Output CSVs:**
- `place_mentions.csv` — mention, lemma, geocodable?, space_category
- `actor_gender.csv` — actor, gender, method
- `gender_x_space.csv` — contingency + residuals
- `gender_x_frame.csv` — contingency
- `narrative_transitions.csv` — from_setting, to_setting, count

**Output charts:** gender×space heatmap/mosaic, bipartite gender↔space network,
narrative-space transition graph, and (for the geocodable subset) the existing
GIS map.

## 5. New files

- `symbolic_space_main.py` (GUI) + `symbolic_space_util.py` (logic)
- `symbolic_space_typology_util.py` (classifier + WordNet seeding)
- `lib/symbolic_space_typology.csv` (the gazetteer)
- KB hook in `semantic_aggregation_main` ("Spatial domain" option)
- TIPS: `TIPS_NLP_Narrative symbolic space.pdf`

Reachable from the **Semantic analyses** hub (and/or the narrative-analysis GUI).

## 6. Build order (each phase ships something usable)

1. **Typology gazetteer + classifier** — seed from WordNet, curate a folktale
   starter list; standalone + unit-testable (pure, stdlib+WordNet). *Deliverable:*
   tag any location noun with a space category.
2. **Geocoding split** — route the Nominatim residue to the typology. *Deliverable:*
   corpus split into real vs symbolic places, symbolic ones categorized.
3. **Gender × space** cross-tab + heatmap/mosaic + bipartite network. *Deliverable:*
   the headline "gendered division of narrative space" result. **This is the MVP.**
4. **FrameNet convergence** (gender × frame).
5. **Narrative-space transition graph** (Proppian movement).

## 7. Open questions / validation

- **Locative extraction:** which dependency relations count as "location of the
  action" (`obl:in/at/on`, `nmod`, copular locatives)? Tune on a sample.
- **Non-named actors:** gender for "the old woman", "the miller's son" via kin /
  honorific / role lexicon.
- **Corpus:** Grimm / Afanasyev / an ATU-indexed collection; the user works with
  **English + Italian** — the typology should be language-tagged (Open
  Multilingual WordNet gives Italian hypernyms).
- **Validation:** hand-code a sample of tales, compare to the automated
  gender×space cross-tab (Cohen's κ) — the suite already has κ in `statistics_csv`.

## 8. Why it's a fitting capstone

Every piece reuses machinery already in the suite (NER, SVO, geocoding,
gender annotation, the semantic KB dispatcher, WordNet/FrameNet, stats, charts),
and it turns a *limitation* of the geographic map (folktale places don't geocode)
into a new analytical lens — social-science analysis of **narrative space** and
its **gendering**. The failed geocode becomes the finding.
