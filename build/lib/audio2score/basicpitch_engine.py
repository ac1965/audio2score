#!/usr/bin/env python3
"""
Wrapper for BasicPitch.
Generates:
- main MIDI
- per-stem MIDI
"""

import pathlib
import os
from typing import Dict

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


def run_basic_pitch(wav: pathlib.Path, out_root: pathlib.Path) -> pathlib.Path:
    stem = wav.stem
    out_root.mkdir(parents=True, exist_ok=True)

    # clean old files
    for ext in ["mid", "csv", "npz"]:
        p = out_root / f"{stem}_basic_pitch.{ext}"
        if p.exists():
            p.unlink()

    predict_and_save(
        audio_path_list=[str(wav)],
        output_directory=str(out_root),
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        save_notes=False,
        model_or_model_path=ICASSP_2022_MODEL_PATH,
    )

    midi = out_root / f"{stem}_basic_pitch.mid"
    return midi


def run_basic_pitch_per_stems(stems: Dict[str, pathlib.Path], out_root: pathlib.Path):

    midi_root = out_root / "midi"
    midi_root.mkdir(parents=True, exist_ok=True)

    result = {}

    for stem_name, wav in stems.items():
        d = midi_root / stem_name
        d.mkdir(parents=True, exist_ok=True)

        midi = run_basic_pitch(wav, d)
        result[stem_name] = midi

    return result
