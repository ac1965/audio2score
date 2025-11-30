#!/usr/bin/env python3
import pathlib
import numpy as np
import soundfile as sf
import librosa


def normalize_audio(input_path: pathlib.Path, sr: int = 44100) -> pathlib.Path:
    """
    WAV を読み込み:
    - モノラル変換
    - サンプリングレート統一
    - 振幅正規化（peak=0.95）
    """
    y, orig_sr = librosa.load(str(input_path), sr=sr, mono=True)
    if y.size == 0:
        raise ValueError(f"Input audio is empty: {input_path}")

    peak = np.max(np.abs(y))
    if peak > 0:
        y = 0.95 * y / peak

    out_path = input_path.with_suffix(".norm.wav")
    sf.write(out_path, y, sr)
    return out_path
