"""Rule-based recommendation engine inspired by the project brief."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .data_models import ActionItem, Recommendation
from .preprocess import extract_key_terms, extract_resource_intents


@dataclass
class KnowledgeBase:
    """Static knowledge base describing curated resources."""

    entries: Dict[str, List[str]]

    @classmethod
    def default(cls) -> "KnowledgeBase":
        return cls(
            entries={
                "meeting_notes": [
                    "Template: action-oriented meeting minutes",
                    "Guide: synthesising stakeholder updates",
                ],
                "design_docs": [
                    "Checklist: UX specification review",
                    "Notion doc: design decision log",
                ],
                "data_sources": [
                    "Dashboard: weekly analytics snapshot",
                    "Dataset: NPS verbatim feedback sample",
                ],
                "engineering": [
                    "Playbook: prototype hardening steps",
                    "Runbook: deployment QA checklist",
                ],
                "communication": [
                    "Email template: stakeholder weekly update",
                    "Slack channel: #project-sync",
                ],
                "general": [
                    "AI assistant prompt: ask for summarised risks",
                    "LLM chain: convert transcripts into Jira issues",
                ],
            }
        )


DEFAULT_TIMELINE = {
    1: "Week 1: Immediate transcript preprocessing and extraction",
    2: "Week 2: Prototype recommender evaluation",
    3: "Week 3: Integrate LLM reasoning loop",
    4: "Week 4: Demo and retrospective",
}


class RecommendationEngine:
    """Generate recommendations and contextual briefings."""

    def __init__(self, knowledge_base: KnowledgeBase | None = None) -> None:
        self.knowledge_base = knowledge_base or KnowledgeBase.default()

    def recommend(self, meeting, action_items: Iterable[ActionItem]) -> List[Recommendation]:
        key_terms = extract_key_terms(meeting)
        intents = extract_resource_intents(action_items)
        recommendations: List[Recommendation] = []
        for item in action_items:
            resources = self._resources_for(item, intents)
            rationale = self._build_rationale(item, key_terms)
            summary = self._summarise(item)
            recommendations.append(
                Recommendation(
                    action_item=item,
                    summary=summary,
                    resources=resources,
                    rationale=rationale,
                )
            )
        return recommendations

    def _resources_for(self, item: ActionItem, intents: Dict[str, int]) -> List[str]:
        categories = ["general"]
        for category, _ in sorted(intents.items(), key=lambda kv: kv[1], reverse=True):
            if category not in categories:
                categories.append(category)
        matches: List[str] = []
        for category in categories:
            matches.extend(self.knowledge_base.entries.get(category, []))
        return matches[:5]

    def _build_rationale(self, item: ActionItem, key_terms: List[str]) -> str:
        due = (
            DEFAULT_TIMELINE.get(item.due_week)
            if item.due_week
            else "Align with sprint cadence and stakeholder checkpoints."
        )
        highlights = ", ".join(key_terms[:5]) or "core meeting themes"
        return (
            f"Task led by {item.owner or 'the assigned owner'} benefits from resources aligned "
            f"to {highlights}. {due}"
        )

    def _summarise(self, item: ActionItem) -> str:
        due_week = item.due_week or "TBD"
        return f"Assign to {item.owner or 'TBD'} | Due: {due_week} | Confidence: {item.confidence:.2f}"
