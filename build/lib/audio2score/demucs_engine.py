#!/usr/bin/env python3
"""
Demucs ensemble stem separation.
Handles variable number of stems across models
(4-stem, 6-stem, etc.)
"""

import pathlib
from typing import Dict, List

import numpy as np
import soundfile as sf
import torch

from demucs.pretrained import get_model
from demucs.apply import apply_model
from demucs.audio import convert_audio


def _load_audio(path: pathlib.Path):
    wav, sr = sf.read(str(path), always_2d=True)
    wav_t = torch.tensor(wav.T, dtype=torch.float32).unsqueeze(0)
    return wav_t, sr


def separate_stems(
    wav_path: pathlib.Path,
    out_dir: pathlib.Path,
    models: List[str],
    shifts: int = 1,
    overlap: float = 0.25,
) -> Dict[str, pathlib.Path]:

    print(f"[demucs] Loading: {wav_path}")
    wav, sr = _load_audio(wav_path)

    ensembles = []
    sample_rate = None

    for model_name in models:
        print(f"[demucs] Running model: {model_name}")
        model = get_model(model_name)
        model.eval()

        sample_rate = model.samplerate
        wav_m = convert_audio(wav, sr, sample_rate, model.audio_channels)

        with torch.no_grad():
            pred = apply_model(
                model, wav_m,
                shifts=shifts,
                split=True,
                overlap=overlap,
            )[0]

        ensembles.append(pred.cpu().numpy())

    # Align stem dimensions
    max_stems = max(e.shape[0] for e in ensembles)
    aligned = []
    for e in ensembles:
        if e.shape[0] < max_stems:
            pad = np.zeros(
                (max_stems - e.shape[0], e.shape[1], e.shape[2]),
                dtype=e.dtype
            )
            e = np.concatenate([e, pad], axis=0)
        aligned.append(e)

    avg = sum(aligned) / len(aligned)

    out_root = out_dir / "stems" / "ensemble"
    out_root.mkdir(parents=True, exist_ok=True)

    print(f"[demucs] Saving stems → {out_root}")

    paths = {}
    for i in range(max_stems):
        stem_name = f"stem{i}"
        audio = avg[i].T
        outf = out_root / f"{wav_path.stem}_{stem_name}.wav"
        sf.write(str(outf), audio, sample_rate)
        print(f"[demucs]   {stem_name}: {outf}")
        paths[stem_name] = outf

    return paths
