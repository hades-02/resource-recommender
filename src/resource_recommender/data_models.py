"""Data models used in the AMI transcript processing pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Utterance:
    """A single speaker utterance."""

    speaker: str
    start_time: float
    end_time: float
    text: str

    def duration(self) -> float:
        """Return the duration of the utterance in seconds."""

        return max(0.0, self.end_time - self.start_time)


@dataclass
class MeetingTranscript:
    """Structured representation of a meeting transcript."""

    meeting_id: str
    utterances: List[Utterance] = field(default_factory=list)

    @property
    def speakers(self) -> List[str]:
        """Return unique speakers in order of first appearance."""

        seen = []
        for utt in self.utterances:
            if utt.speaker not in seen:
                seen.append(utt.speaker)
        return seen

    def to_dict(self) -> Dict:
        """Serialize to a JSON-compatible dictionary."""

        return {
            "meeting_id": self.meeting_id,
            "speakers": self.speakers,
            "utterances": [
                {
                    "speaker": u.speaker,
                    "start_time": u.start_time,
                    "end_time": u.end_time,
                    "text": u.text,
                    "duration": u.duration(),
                }
                for u in self.utterances
            ],
        }


@dataclass
class ActionItem:
    """Represents a task extracted from a meeting."""

    description: str
    owner: Optional[str] = None
    due_week: Optional[int] = None
    confidence: float = 0.5
    supporting_utterance: Optional[Utterance] = None

    def to_dict(self) -> Dict:
        return {
            "description": self.description,
            "owner": self.owner,
            "due_week": self.due_week,
            "confidence": self.confidence,
            "supporting_utterance": {
                "speaker": self.supporting_utterance.speaker,
                "text": self.supporting_utterance.text,
                "start_time": self.supporting_utterance.start_time,
                "end_time": self.supporting_utterance.end_time,
            }
            if self.supporting_utterance
            else None,
        }


@dataclass
class Recommendation:
    """A resource recommendation generated for an action item."""

    action_item: ActionItem
    summary: str
    resources: List[str]
    rationale: str

    def to_dict(self) -> Dict:
        return {
            "action_item": self.action_item.to_dict(),
            "summary": self.summary,
            "resources": self.resources,
            "rationale": self.rationale,
        }


@dataclass
class PipelineArtifacts:
    """Artifacts produced by the pipeline for a single meeting."""

    meeting: MeetingTranscript
    action_items: List[ActionItem]
    recommendations: List[Recommendation]

    def to_dict(self) -> Dict:
        return {
            "meeting": self.meeting.to_dict(),
            "action_items": [item.to_dict() for item in self.action_items],
            "recommendations": [rec.to_dict() for rec in self.recommendations],
        }


def ensure_directory(path: Path) -> Path:
    """Create a directory if it does not exist and return the path."""

    path.mkdir(parents=True, exist_ok=True)
    return path


def chunked(iterable: Iterable, size: int) -> Iterable[List]:
    """Yield lists of length ``size`` from ``iterable``."""

    chunk: List = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
