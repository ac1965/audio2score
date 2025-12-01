#!/usr/bin/env python3
import pathlib
from typing import Tuple

import numpy as np
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


def run_basic_pitch(
    audio: pathlib.Path,
    output_root: pathlib.Path,
    stem_name: str,
) -> Tuple[pathlib.Path, pathlib.Path]:
    """
    BasicPitch による Audio→MIDI 変換。
    - 既存の .mid / .npz / .csv があれば自動削除してから再生成
    - 入力ファイル名（stem_name）を最終成果物まで保持
    """
    audio = audio.resolve()
    midi_dir = output_root / "midi"
    midi_dir.mkdir(parents=True, exist_ok=True)

    print(f"[BasicPitch] audio={audio}")

    # --- ★ 既存出力の自動クリーン（BasicPitch の安全停止対策） ---
    for ext in ("*.mid", "*.npz", "*.csv"):
        for f in midi_dir.glob(ext):
            f.unlink()

    # --- Basic Pitch v0.4.x 正式API ---
    predict_and_save(
        [str(audio)],           # input_audio_path_list
        str(midi_dir),          # output_directory
        True,                   # save_midi
        False,                  # sonify_midi
        True,                   # save_model_outputs
        True,                   # save_notes
        ICASSP_2022_MODEL_PATH, # 使用モデル
    )

    # --- MIDI ファイル取得 ---
    mids = sorted(midi_dir.glob("*.mid"))
    if not mids:
        raise FileNotFoundError(f"No MIDI file generated in {midi_dir}")

    final_midi = midi_dir / f"{stem_name}.mid"
    if final_midi.exists():
        final_midi.unlink()
    mids[0].rename(final_midi)

    # --- npz ファイル取得 ---
    npzs = sorted(midi_dir.glob("*.npz"))
    if npzs:
        onnx_path = npzs[0]
    else:
        onnx_path = midi_dir / f"{stem_name}.npz"
        np.save(onnx_path, np.zeros((1,)))

    print(f"[BasicPitch] MIDI generated: {final_midi}")

    return final_midi, onnx_path
