"""Parsing utilities for AMI Corpus style transcripts."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable, List

from .data_models import MeetingTranscript, Utterance


COLUMN_ALIASES = {
    "speaker": {"speaker", "speaker_id", "participant", "agent"},
    "start_time": {"start_time", "start", "startseconds", "start_seconds"},
    "end_time": {"end_time", "end", "endseconds", "end_seconds"},
    "text": {"text", "transcript", "utterance", "content", "dialogue"},
}


class TranscriptFormatError(RuntimeError):
    """Raised when a transcript cannot be parsed."""


def _normalize_header(header: Iterable[str]) -> dict:
    mapping = {}
    for name in header:
        lowered = name.strip().lower()
        for key, aliases in COLUMN_ALIASES.items():
            if lowered in aliases:
                mapping[key] = name
                break
    missing = {key for key in COLUMN_ALIASES if key not in mapping}
    if missing:
        raise TranscriptFormatError(
            f"Transcript is missing required columns: {', '.join(sorted(missing))}"
        )
    return mapping


def parse_transcript_file(path: Path, meeting_id: str | None = None) -> MeetingTranscript:
    """Parse a TSV/CSV transcript file into a :class:`MeetingTranscript`."""

    delimiter = "\t" if path.suffix.lower() in {".tsv", ".txt"} else ","
    with path.open("r", encoding="utf8") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        mapping = _normalize_header(reader.fieldnames or [])
        utterances: List[Utterance] = []
        for row in reader:
            speaker = row.get(mapping["speaker"], "").strip() or "Unknown"
            text = _clean_text(row.get(mapping["text"], ""))
            start = _parse_float(row.get(mapping["start_time"], 0.0))
            end = _parse_float(row.get(mapping["end_time"], 0.0))
            if not text:
                continue
            utterances.append(
                Utterance(
                    speaker=speaker,
                    start_time=start,
                    end_time=end,
                    text=text,
                )
            )
    inferred_meeting_id = meeting_id or path.stem
    return MeetingTranscript(meeting_id=inferred_meeting_id, utterances=utterances)


def _parse_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def load_transcripts(root_dir: Path) -> List[MeetingTranscript]:
    """Load all transcripts contained in ``root_dir``."""

    transcripts: List[MeetingTranscript] = []
    for path in sorted(root_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".tsv", ".csv", ".txt"}:
            continue
        transcripts.append(parse_transcript_file(path))
    if not transcripts:
        raise FileNotFoundError(
            f"No transcripts found in {root_dir}. Expected .tsv, .csv or .txt files."
        )
    return transcripts
