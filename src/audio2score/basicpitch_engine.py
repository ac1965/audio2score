#!/usr/bin/env python3
import pathlib
from typing import Tuple

import numpy as np
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


def run_basic_pitch(
    audio: pathlib.Path,
    output_root: pathlib.Path,
) -> Tuple[pathlib.Path, pathlib.Path]:
    """
    BasicPitch による Audio→MIDI 変換。
    - audio: 正規化済み WAV
    - output_root/midi/main.mid として保存
    """
    audio = audio.resolve()
    midi_dir = output_root / "midi"
    midi_dir.mkdir(parents=True, exist_ok=True)

    midi_path = midi_dir / "main.mid"
    onnx_path = midi_dir / "main.onnx.npy"

    print(f"[BasicPitch] audio={audio}")

    # Basic Pitch v0.4.0 以降のシグネチャ（位置引数）に完全に合わせる:
    # predict_and_save(
    #     input_audio_path_list,
    #     output_directory,
    #     save_midi,
    #     sonify_midi,
    #     save_model_outputs,
    #     save_notes,
    #     model_or_model_path,
    # )
    predict_and_save(
        [str(audio)],           # input_audio_path_list
        str(midi_dir),          # output_directory
        True,                   # save_midi
        False,                  # sonify_midi (WAV 出力は不要なので False)
        True,                   # save_model_outputs (NPZ 出力)
        True,                   # save_notes (CSV 出力)
        ICASSP_2022_MODEL_PATH, # 使用するモデルパス
    )

    # BasicPitch が生成した .mid を拾って main.mid に統一する
    mids = sorted(midi_dir.glob("*.mid"))
    if not mids:
        raise FileNotFoundError(f"No MIDI file generated in {midi_dir}")

    if midi_path.exists():
        midi_path.unlink()
    mids[0].rename(midi_path)

    # モデル出力の placeholder （必要なら後でちゃんと拾う）
    if not onnx_path.exists():
        np.save(onnx_path, np.zeros((1,)))

    return midi_path, onnx_path
