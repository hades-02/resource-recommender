"""Command line interface for the resource recommender pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import build_pipeline


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Process AMI transcripts into action-item recommendations."
    )
    parser.add_argument("input", type=Path, help="Directory containing AMI transcripts")
    parser.add_argument(
        "output",
        type=Path,
        help="Directory where structured conversations and recommendations will be saved",
    )
    args = parser.parse_args(argv)

    artifacts = build_pipeline(args.input, args.output)
    print(f"Processed {len(artifacts)} meetings. Results stored in {args.output}.")


if __name__ == "__main__":
    main()
