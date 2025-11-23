# Smart Meeting Action-Item Recommender

This repository turns AMI Meeting Corpus transcripts into structured, speaker-
by-speaker conversations and surfaces action items with static, curated resource
suggestions. The codebase is intentionally lightweight—no external network
calls, no learned models—so you can run it locally as-is or plug it into a
larger orchestration stack.

## What the pipeline does (and does not do)
- ✅ **Parses AMI-style TSV/CSV transcripts** into ordered speaker timelines.
- ✅ **Extracts action items heuristically** using rule-based keyword and phrase
  detection (e.g., "please send", "we need to", "can you").
- ✅ **Assigns owners and coarse due weeks** from the speaker label and temporal
  hints in each utterance.
- ✅ **Recommends resources from a static knowledge base** (templates, guides,
  links) bundled in the code—no internet lookups or trained recommender.
- ❌ **No NER or advanced NLP models** are shipped; extraction is deterministic
  and pattern-driven.
- ❌ **No LLM reasoning** is invoked; outputs are produced in a single scripted
  pass.
- ❌ **No online resource search** occurs; every suggestion comes from the
  in-repo `KnowledgeBase` mapping.

## Repository layout
```
├── data/
│   └── raw/                      # Place AMI transcripts here (sample provided)
├── src/
│   └── resource_recommender/
│       ├── ami_parser.py         # Converts TSV/CSV transcripts into timelines
│       ├── cli.py                # Command-line entry point
│       ├── data_models.py        # Dataclasses for meetings, actions, recs
│       ├── pipeline.py           # End-to-end orchestration
│       ├── preprocess.py         # Rule-based action extraction
│       └── recommender.py        # Static knowledge-base recommender
└── README.md
```

## Input requirements
- **Transcript format:** TSV or CSV with columns for speaker, start time, end
  time, and utterance text. A minimal example lives at
  `data/raw/sample_meeting.tsv`.
- **Source:** The files can be produced by the
  [AMICorpus-Meeting-Transcript-Extraction](https://github.com/Utkichaps/AMICorpus-Meeting-Transcript-Extraction)
  project. Run that exporter, then copy the generated TSV/CSV files into
  `data/raw/` (or point the CLI at the folder containing them).

## Environment setup
The code uses only the Python standard library. Any Python **3.10+** interpreter
works.

```bash
python -m venv .venv
source .venv/bin/activate
```

(No additional `pip install` steps are required.)

## Running the pipeline
From the repository root, execute the CLI with the input folder and an output
folder of your choice (it will be created if missing):

```bash
python -m src.resource_recommender.cli data/raw output/
```

What happens when you run it:
1. **Parse transcripts:** Each TSV/CSV is converted into a JSON conversation
   timeline grouped by speaker.
2. **Extract action items:** Simple regex and keyword rules surface candidate
   tasks, assign the speaking participant as owner, and infer a coarse "due in
   N weeks" if temporal hints are found.
3. **Recommend resources:** For each action, the recommender matches detected
   intents to the static `KnowledgeBase` mapping (e.g., design docs, meeting
   notes templates) and returns up to five curated suggestions plus a fallback.
4. **Emit artefacts:** Structured JSON files and a Markdown report are written
   to the output directory.

## Output artefacts
The output folder will contain:
- `conversations/<meeting>.json` – ordered speaker timeline with utterance
  metadata.
- `action_items/<meeting>.json` – extracted tasks with owners, due weeks, and
  heuristic confidence.
- `recommendations/<meeting>.json` – resource suggestions and rationales per
  action item (all from the static knowledge base).
- `report.md` – a consolidated Markdown summary for all processed meetings.

## Customisation tips
- **Update resources:** Edit `KnowledgeBase.default()` in
  `src/resource_recommender/recommender.py` to point to your own templates,
  wikis, or playbooks. These entries are the sole source of recommendations.
- **Improve extraction:** Enhance the patterns in `src/resource_recommender/
  preprocess.py` or swap in an NLP library (spaCy, transformers) for richer
  entity and intent detection.
- **Integrate an LLM:** Use the JSON outputs as structured context for an LLM to
  refine assignments, explain recommendations, or generate tickets.

## Limitations and expectations
- Recommendations are **static** and **offline**—they will not change unless you
  edit the code or knowledge base.
- Owner and due-week assignments are **heuristic** and may need manual review.
- The pipeline is single-process with no orchestration layer; distributed or
  interactive agent behaviour is out of scope by design.

## Quick smoke test
A tiny sample transcript is available at `data/raw/sample_meeting.tsv`. Running
`python -m src.resource_recommender.cli data/raw output/` should complete in
seconds and populate `output/` with the artefacts described above.
