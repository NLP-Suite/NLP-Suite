# Building the "clever" annotation-join tool

*Design memo — how to assemble the symbolic-space input (and much more) automatically
over large corpora by MERGING the outputs of existing tools. Roberto asked: which
tool-outputs can we merge, and how, so a 2,000-tale corpus needs no hand-coding.*

---

## 1. The one idea

Every NLP-Suite tool writes a csv whose rows are **keyed to the same spine**. The
**CoNLL table** is the token-level spine; the universal keys carried by almost every
layer are:

- **Document ID** (which text)
- **Sentence ID** (which sentence)
- **token ID / Head** (which word, and what it depends on)

So "combining tools" = a **relational join on (Document ID, Sentence ID [, token])**,
performed at the right *granularity*. That's it. The failed hand-assembly becomes an
automatic merge.

## 2. The annotation layers and their keys

| Layer | Tool | Grain | Join keys | What it contributes |
|---|---|---|---|---|
| Parse / POS / NER / deprel | CoNLL (`parsers_annotators`) | token | Doc, Sent, tokenID, Head | POS, NER type, lemma, dependency structure — **the spine** |
| Who-did-what-where | `SVO_main` | clause/event | Doc, Sent | Subject (**actor**), Verb, Object, **Location**, Time (order) |
| Gender | `html_annotator_gender` | person mention | Doc, Sent, Name | actor **gender** |
| Coreference | `coreference_main` / `coreference_neural` | mention→entity | Doc, Sent, token span | ties **pronouns → named actor** (the scale enabler) |
| WordNet sense/hypernym | dictionary annotator / `semantic_aggregation` | token | Doc, Sent, token | **type** of actor/thing (king→royalty, servant→labour) |
| DBpedia / YAGO | `knowledge_graphs_DBpedia_YAGO` | named entity | Doc, Sent, span | ontology **class** of a NAMED entity (occupation, role) |
| Space typology | `symbolic_space_typology_util` (built) | place word | the word | **kind of space** (domestic/field/wild…) |

## 3. What already exists — don't reinvent

- **`data_manipulation_util.merge`** — generic keyed `pd.merge` (inner/outer). This is
  the join *primitive*; the new tool orchestrates it, it doesn't re-code joining.
- **Coreference** — `coreference_main`, `coreference_neural_util`,
  `Stanford_CoreNLP_coreference_util`. Already there.
- **All the layers above** already emit csv with Doc/Sent keys.

The gap is a **granularity-aware orchestrator** that knows these layers and aligns them
on the spine — plus coreference in front, so it works at corpus scale.

## 4. Recipe — the symbolic-space input, fully automatic (folktales)

Target row: `document, sentence, actor, actor_type, gender, location, space_type, order`.

1. **Parse** the corpus → CoNLL (spine: POS, NER, Head, DepRel, Doc, Sent).
2. **Coreference** → resolve every pronoun/mention to a canonical actor id.
   *Without this step, "she went to the well" loses its actor and the whole corpus
   collapses to unattributed events. This is THE enabling step.*
3. **SVO** → one row per actor-event: Subject(actor) + Location + Sent (order).
4. **Merge gender** onto the actor: `SVO ⨝ gender on (Doc, Sent, actor≈Name)`.
   For generic characters (a girl, the king) gender comes from WordNet/lexicon, not names.
5. **Type the actor** (optional, = class/role proxy): WordNet hypernym of the subject
   noun under `person.n.01` (king→royalty, peasant→labour, witch→supernatural); for
   NAMED characters, DBpedia/YAGO class.
6. **Type the location**: `symbolic_space_typology_util.classify()` (already built).
7. Write `NLP_symbolic_space_input_<corpus>.csv`. Done — no hand-coding.

## 5. The clever bits (dependency + semantics, not just column joins)

- **Adjective attribution** — a character's descriptors: JJ tokens whose `Head` is the
  actor and `DepRel ∈ {amod, acomp}` → "the **wicked** witch", "the **poor** woodcutter".
  This is a **within-CoNLL self-join on Head**, and it's how you get characterization
  (moral/class attributes) with no annotator.
- **Role / class typing** — WordNet hypernym path of the actor noun gives social role
  for folktales; DBpedia/YAGO gives it for real named people (the lynching corpus).
- **Location typing** — already solved by the gazetteer + WordNet fallback.

## 6. The general tool: a "Feature-table builder" (annotation merger)

The symbolic-space input is one instance of a reusable engine:

- **Pick the unit of analysis**: token · **actor-event** · sentence · actor · document.
- **Pick the layers** to fold in (CoNLL, SVO, gender, WordNet, DBpedia/YAGO…).
- The engine **aligns on the spine**, **aggregates one-to-many** (a sentence has many
  tokens; an actor has many events) with declared rules (first / list / count / mode),
  and emits **one analysis-ready table**.
- Reusable far beyond symbolic space: any "who/what has which attributes where" question.

## 7. The honest hard parts

- **Coreference is the crux at scale.** Pronouns dominate narrative; without coref most
  actor-events are unattributed. Quality of coref caps quality of everything downstream.
- **Granularity / one-to-many joins** need explicit aggregation rules, or rows multiply.
- **Entity linking is corpus-dependent.** DBpedia/YAGO fire on NAMED entities →
  great for the **lynching newspaper corpus** (real people/places), mostly silent on
  **folktales** (generic a-girl/the-king) where **WordNet typing** is the right lever.
  → the engine must let the user choose the enrichment source per corpus.

## 8. Proposed build order

1. **Prototype the join** on ONE corpus with `data_manipulation.merge` on
   (Document ID, Sentence ID): `SVO(subject,location,order) ⨝ gender` → the input file.
   Validate the numbers by hand on a few tales.
2. Insert the **coreference** pass upstream; re-measure attribution coverage.
3. Add **dependency-adjective** + **WordNet-role** enrichment columns.
4. Generalize into the **Feature-table builder** GUI (unit-of-analysis + layer picker).

---

*Bottom line: the merge is a keyed join the suite can already do; the intelligence is
(a) putting coreference in front so actors survive at scale, and (b) mining the CoNLL
dependency + WordNet/ontology layers for attributes no single tool emits.*
