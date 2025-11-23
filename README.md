# Smart Meeting Action-Item Recommender

This project turns AMI Meeting Corpus transcripts into structured conversations
and heuristic action items, then attaches static (offline) resource suggestions
for each task. Everything runs locally with only the Python standard library.

---

## What it does

* **Input:** TSV/CSV meeting transcripts exported from the
  [AMICorpus-Meeting-Transcript-Extraction](https://github.com/Utkichaps/AMICorpus-Meeting-Transcript-Extraction)
  project (or any file with the same columns for speaker, start, end, text).
* **Processing steps:**
  1. Parse utterances into a time-ordered, per-speaker conversation timeline.
  2. Detect action-item phrases with keyword/regex rules (no external NLP).
  3. Assign the speaker as the task owner and infer a rough "due in N weeks"
     from temporal hints.
  4. Recommend up to five resources per task from a **static, in-repo knowledge
     base** (no internet calls or trained recommender).
* **Outputs:** JSON artefacts for conversations, action items, and resource
  recommendations, plus a consolidated Markdown report.

---

## Repository layout

```
├── data/
│   └── raw/                      # Place AMI transcripts here (sample provided)
├── src/
│   └── resource_recommender/
│       ├── ami_parser.py         # TSV/CSV parsing into speaker timelines
│       ├── cli.py                # Command-line entry point
│       ├── data_models.py        # Dataclasses for meetings, actions, recs
│       ├── pipeline.py           # End-to-end orchestration
│       ├── preprocess.py         # Rule-based action extraction
│       └── recommender.py        # Static knowledge-base recommender
└── README.md
```

---

## Setup (Python 3.10+)

There are **no external dependencies**. Any modern Python interpreter will do.

```bash
python -m venv .venv
source .venv/bin/activate
```

No `pip install` step is required.

---

## Prepare transcripts

1. Export or create TSV/CSV files with columns for speaker, start time, end
   time, and utterance text.
2. Place the files in `data/raw/` (a tiny `sample_meeting.tsv` is included), or
   keep them elsewhere and point the CLI to that directory when running.

---

## Run the pipeline

From the repository root:

```bash
python -m src.resource_recommender.cli <input_dir> <output_dir>
```

* `<input_dir>` – folder containing TSV/CSV transcripts.
* `<output_dir>` – destination folder (created if missing).

Example using the bundled sample:

```bash
python -m src.resource_recommender.cli data/raw output/
```

What happens during the run:

1. **Parse** transcripts into JSON speaker timelines.
2. **Extract** action items using heuristic patterns (e.g., "please send",
   "can you", "we need to").
3. **Assign** owners (speaker names) and approximate due weeks from temporal
   hints.
4. **Recommend** resources by matching task intents to the static knowledge
   base and limiting to five suggestions.
5. **Write** artefacts to the output directory.

---

## Output artefacts

* `conversations/<meeting>.json` – ordered speaker timeline with utterance
  metadata.
* `action_items/<meeting>.json` – extracted tasks with owners, due weeks, and
  heuristic confidence.
* `recommendations/<meeting>.json` – resource suggestions per action item (all
  from the static knowledge base).
* `report.md` – consolidated Markdown summary of all processed meetings.

You can open the Markdown report directly or load the JSON files into your own
workflows or LLM prompts.

---

## Customize the pipeline

* **Resource catalog:** Edit `KnowledgeBase.default()` in
  `src/resource_recommender/recommender.py` to point to your own templates,
  wikis, or tools. These entries are the only source of recommendations.
* **Extraction rules:** Tweak keyword and regex patterns in
  `src/resource_recommender/preprocess.py` to broaden or narrow what counts as
  an action item. Swap in an NLP library if you need NER or intent models.
* **Downstream use:** The JSON outputs are suitable inputs for an LLM to refine
  assignments, generate tickets, or provide explanations.

---

## Limitations

* No online search or external API calls; everything is offline and deterministic.
* No trained recommender or LLM reasoning—the system is rule-based.
* Due-week inference is coarse and may need manual review.

---

## Quick smoke test

```bash
python -m src.resource_recommender.cli data/raw output/
```

The bundled `sample_meeting.tsv` should complete in seconds and populate the
`output/` directory with the artefacts listed above.

