# Smart Meeting Action-Item Recommender

This project converts AMI Corpus meeting transcripts into speaker-by-speaker 
conversations and produces resource recommendations for the action items that 
emerge from each meeting. The design follows the *Smart Meeting Action-Item 
Recommender (LLM + NLP + Recommender)* blueprint in the attached reference: 

1. **Meeting Transcript (AMI Corpus)** – ingest raw transcripts exported from the
   [AMI Meeting Corpus](http://groups.inf.ed.ac.uk/ami/corpus/).
2. **NLP Preprocessing (NER, Task Extraction)** – normalise transcripts into a
   speaker timeline and apply lightweight heuristic extraction to surface action
   items.
3. **Recommendation Layer (Overview + Resource Prediction)** – map each action
   item to curated knowledge-base resources and provide rationale grounded in
   meeting themes.
4. **LLM-Agent Reasoning (Assignment + Explanation)** – emulate an agent that
   assigns owners (based on the speaker) and summarises why each recommendation
   matters and when it should be delivered.

The repository provides a fully reproducible Python pipeline, ready for local
experimentation or integration with downstream LLM systems.

## Project Structure

```text
├── data/
│   └── raw/                     # Place AMI transcripts here (sample provided)
├── src/
│   └── resource_recommender/
│       ├── ami_parser.py        # Converts TSV/CSV transcripts into timelines
│       ├── cli.py               # Command line entry-point
│       ├── data_models.py       # Dataclasses for meetings, actions, recs
│       ├── pipeline.py          # End-to-end orchestration
│       ├── preprocess.py        # NLP heuristics for action extraction
│       └── recommender.py       # Resource recommendation engine
└── README.md
```

## Getting Started

### 1. Clone the AMI transcript extraction repo

The pipeline expects transcripts exported by the
[`AMICorpus-Meeting-Transcript-Extraction`](https://github.com/Utkichaps/AMICorpus-Meeting-Transcript-Extraction)
project. Clone that repository and run its extraction scripts to produce TSV or
CSV files where each row contains a speaker label, start/end timestamps, and the
spoken text.

```bash
git clone https://github.com/Utkichaps/AMICorpus-Meeting-Transcript-Extraction.git
cd AMICorpus-Meeting-Transcript-Extraction
# Follow the repository instructions to export transcripts (TSV/CSV)
```

Copy the resulting transcript files into `data/raw/` inside this project (the
pipeline recursively scans subdirectories, so you can also point it at the
extracted folder directly).

A curated `sample_meeting.tsv` is provided for quick smoke-testing.

### 2. Create a Python environment

The code relies only on the Python standard library. Any Python 3.10+
interpreter works.

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Run the pipeline

```bash
python -m src.resource_recommender.cli data/raw output/
```

The command performs the following steps for each meeting transcript:

1. **Conversion** – produce a JSON conversation timeline with per-speaker
   utterances.
2. **Task Extraction** – identify candidate action items using keyword and
   pattern heuristics inspired by the project brief ("We need to…", "Please
   send…", etc.).
3. **Recommendation Generation** – match action items with curated knowledge-base
   resources (meeting notes templates, design checklists, LLM prompts, etc.) and
   create an interpretable rationale, including a suggested delivery week derived
   from temporal hints in the transcript.
4. **Reporting** – emit Markdown, JSON, and console summaries.

### 4. Inspect the outputs

The pipeline creates an `output/` directory with:

- `conversations/<meeting>.json` – speaker timelines and utterance metadata.
- `action_items/<meeting>.json` – extracted actions with owners, due weeks, and
  confidence scores.
- `recommendations/<meeting>.json` – recommended resources and rationales.
- `report.md` – Markdown report mirroring the layout of the reference
  architecture.

The sample data produces output similar to the example illustrated in the
reference poster (timeline, owner assignments, and recommended resources for
weeks 1–4).

## Extending the System

- **Plug in an LLM** – use the structured JSON outputs as prompts to a
  large-language model for richer reasoning, summarisation, or ticket creation.
- **Custom knowledge base** – edit `KnowledgeBase.default()` in
  `src/resource_recommender/recommender.py` to point at organisation-specific
  resources (Confluence pages, Slack channels, Jira templates, etc.).
- **Improved NLP** – replace the heuristic extractors in
  `src/resource_recommender/preprocess.py` with spaCy, transformers, or AMR parsers
  for higher recall and precision.
- **Evaluation** – integrate with metrics such as MAP@K, Recall@K, and track
  downstream adoption of recommended resources.

## License

This project is distributed for educational purposes. The AMI corpus is licensed
separately—ensure you comply with its terms when using the transcripts.
