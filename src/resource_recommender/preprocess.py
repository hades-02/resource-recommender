"""Lightweight NLP utilities for extracting tasks and entities."""

from __future__ import annotations

import itertools
import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

from .data_models import ActionItem, MeetingTranscript, Utterance


TASK_PATTERNS: Sequence[Tuple[re.Pattern, float]] = [
    (re.compile(r"\b(?:we|i|let's|lets|someone) need(?:s)? to\b", re.I), 0.9),
    (re.compile(r"\b(?:action|task|todo)\b", re.I), 0.7),
    (re.compile(r"\b(?:follow up|follow-up)\b", re.I), 0.7),
    (re.compile(r"\b(?:prepare|draft|create|update|summarise|summarize)\b", re.I), 0.8),
    (re.compile(r"\b(?:share|send|review|deliver|organise|organize)\b", re.I), 0.6),
]

DUE_WEEK_HINTS: Dict[int, re.Pattern] = {
    1: re.compile(r"\bthis week|today|tomorrow|by friday\b", re.I),
    2: re.compile(r"\bnext week|week two|week 2\b", re.I),
    3: re.compile(r"\bweek three|week 3|in two weeks\b", re.I),
    4: re.compile(r"\bweek four|week 4|end of the month\b", re.I),
}

RESOURCE_KEYWORDS: Dict[str, Sequence[str]] = {
    "meeting_notes": ("minutes", "notes", "summary"),
    "design_docs": ("design", "wireframe", "spec", "requirement"),
    "data_sources": ("dataset", "data", "analytics", "metrics"),
    "engineering": ("build", "implement", "deploy", "prototype"),
    "communication": ("email", "announce", "stakeholder", "update"),
}


def extract_key_terms(meeting: MeetingTranscript) -> List[str]:
    """Return high-frequency content words to drive recommendations."""

    tokens = []
    for utt in meeting.utterances:
        tokens.extend(_tokenize(utt.text))
    counter = Counter(tok for tok in tokens if len(tok) > 3)
    return [word for word, _ in counter.most_common(15)]


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def extract_action_items(meeting: MeetingTranscript) -> List[ActionItem]:
    """Derive actionable tasks from a meeting transcript."""

    action_items: List[ActionItem] = []
    for utterance in meeting.utterances:
        confidence = _match_confidence(utterance.text)
        if confidence <= 0.0:
            continue
        description = _normalize_description(utterance.text)
        due_week = _infer_due_week(utterance.text)
        action_items.append(
            ActionItem(
                description=description,
                owner=utterance.speaker,
                due_week=due_week,
                confidence=confidence,
                supporting_utterance=utterance,
            )
        )
    merged = _merge_similar_actions(action_items)
    return merged


def _match_confidence(text: str) -> float:
    scores = [score for pattern, score in TASK_PATTERNS if pattern.search(text)]
    if not scores:
        return 0.0
    return min(1.0, max(scores))


def _normalize_description(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    cleaned = re.sub(r"^(?:let's|lets|we|i)\s+", "", cleaned, flags=re.I)
    return cleaned.capitalize()


def _infer_due_week(text: str) -> int | None:
    for week, pattern in DUE_WEEK_HINTS.items():
        if pattern.search(text):
            return week
    return None


def _merge_similar_actions(actions: List[ActionItem]) -> List[ActionItem]:
    grouped: Dict[str, List[ActionItem]] = defaultdict(list)
    for action in actions:
        key = re.sub(r"[^a-z0-9]+", " ", action.description.lower()).strip()
        grouped[key].append(action)
    merged: List[ActionItem] = []
    for candidates in grouped.values():
        if not candidates:
            continue
        top = max(candidates, key=lambda item: item.confidence)
        if len(candidates) > 1:
            top.confidence = min(1.0, top.confidence + 0.1 * (len(candidates) - 1))
        merged.append(top)
    return sorted(merged, key=lambda item: item.confidence, reverse=True)


def extract_resource_intents(action_items: Iterable[ActionItem]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for item in action_items:
        text = item.description.lower()
        for category, keywords in RESOURCE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                counts[category] += 1
    return counts


def rolling_windows(utterances: Sequence[Utterance], size: int = 3) -> Iterable[List[Utterance]]:
    for window in itertools.islice(_window_generator(utterances, size), len(utterances)):
        if len(window) == size:
            yield window


def _window_generator(sequence: Sequence[Utterance], size: int):
    for idx in range(len(sequence) - size + 1):
        yield sequence[idx : idx + size]
