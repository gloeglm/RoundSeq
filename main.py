#!/usr/bin/env python3
"""Entry point for RoundSeq MIDI Sequencer."""

import argparse
import os
import sys

# Tell Kivy not to consume our CLI args.
os.environ.setdefault("KIVY_NO_ARGS", "1")

# Ensure the package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from roundseq.app import run


def _parse_args():
    parser = argparse.ArgumentParser(description="RoundSeq circular MIDI tool")
    parser.add_argument(
        "--mode",
        choices=("play", "clock"),
        default="play",
        help="play: touchscreen note input (default). clock: visualize incoming MIDI clock.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(mode=args.mode)
