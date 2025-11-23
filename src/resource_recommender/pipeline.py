"""End-to-end pipeline for converting AMI transcripts and generating recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .ami_parser import load_transcripts
from .data_models import PipelineArtifacts, ensure_directory
from .preprocess import extract_action_items
from .recommender import RecommendationEngine


def build_pipeline(input_dir: Path, output_dir: Path) -> List[PipelineArtifacts]:
    """Run the extraction and recommendation pipeline."""

    transcripts = load_transcripts(Path(input_dir))
    output_dir = Path(output_dir)
    conversations_dir = ensure_directory(output_dir / "conversations")
    actions_dir = ensure_directory(output_dir / "action_items")
    recommendations_dir = ensure_directory(output_dir / "recommendations")

    engine = RecommendationEngine()
    artifacts: List[PipelineArtifacts] = []

    for meeting in transcripts:
        action_items = extract_action_items(meeting)
        recommendations = engine.recommend(meeting, action_items)
        artifact = PipelineArtifacts(
            meeting=meeting,
            action_items=action_items,
            recommendations=recommendations,
        )
        artifacts.append(artifact)

        _write_json(conversations_dir / f"{meeting.meeting_id}.json", meeting.to_dict())
        _write_json(
            actions_dir / f"{meeting.meeting_id}.json",
            [item.to_dict() for item in action_items],
        )
        _write_json(
            recommendations_dir / f"{meeting.meeting_id}.json",
            [rec.to_dict() for rec in recommendations],
        )

    _write_report(output_dir / "report.md", artifacts)
    return artifacts


def _write_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def _write_report(path: Path, artifacts: Iterable[PipelineArtifacts]) -> None:
    lines: List[str] = [
        "# Smart Meeting Action-Item Recommender Report",
        "",
        "This report summarises extracted action items and recommended resources",
        "for each processed AMI meeting transcript.",
        "",
    ]
    for artifact in artifacts:
        lines.extend(_meeting_section(artifact))
    path.write_text("\n".join(lines), encoding="utf8")


def _meeting_section(artifact: PipelineArtifacts) -> List[str]:
    lines = [
        f"## Meeting {artifact.meeting.meeting_id}",
        "",
        "**Speakers:** " + ", ".join(artifact.meeting.speakers),
        "",
        "### Action Items",
    ]
    if not artifact.action_items:
        lines.append("- No confident action items detected.")
    else:
        for item in artifact.action_items:
            lines.append(
                f"- ({item.confidence:.2f}) {item.description} — Owner: {item.owner or 'TBD'}; Due week: {item.due_week or 'TBD'}"
            )
    lines.append("")
    lines.append("### Recommendations")
    if not artifact.recommendations:
        lines.append("- No recommendations generated.")
    else:
        for rec in artifact.recommendations:
            resource_list = "; ".join(rec.resources)
            lines.append(
                f"- {rec.summary}. Resources: {resource_list}. Rationale: {rec.rationale}"
            )
    lines.append("")
    return lines
