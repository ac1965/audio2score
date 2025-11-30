#!/usr/bin/env python3
import pathlib
from typing import Tuple

import numpy as np
from basic_pitch.inference import predict_and_save


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
    predict_and_save(
        [str(audio)],
        output_dir=str(midi_dir),
        save_midi=True,
        save_model_outputs=True,
    )

    # BasicPitch の標準出力に依存しないよう、ファイル名を決め打ちに揃える場合は
    # 必要に応じて rename する処理をここに追加する。
    # （現状はディレクトリ内の *.mid を 1つ想定）

    mids = list(midi_dir.glob("*.mid"))
    if not mids:
        raise FileNotFoundError(f"No MIDI file generated in {midi_dir}")
    # 最初のものを main.mid に統一
    mids[0].rename(midi_path)

    # モデルの生出力（オンセット・フレームなど）を保存している場合
    # onnx_path = midi_dir / "main_model_output.npy"
    if not onnx_path.exists():
        # ダミーで空の npy を置いておく（将来の解析用）
        np.save(onnx_path, np.zeros((1,)))

    return midi_path, onnx_path
