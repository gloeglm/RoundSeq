#!/usr/bin/env python3
"""Entry point for RoundSeq MIDI Sequencer."""

import os
import sys

# Ensure the package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from roundseq.app import run

if __name__ == "__main__":
    run()
