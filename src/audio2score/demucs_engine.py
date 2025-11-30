#!/usr/bin/env python3
import pathlib
import subprocess
from typing import List


def separate_stems(
    audio: pathlib.Path,
    models: List[str],
    output_root: pathlib.Path,
) -> pathlib.Path:
    """
    Demucs を使ってステム分離を行う。
    - models: ["htdemucs", "htdemucs_6s"] など
    - output_root/stems/{model}/ 以下に各ステムを保存
    """
    audio = audio.resolve()
    stems_dir = output_root / "stems"
    stems_dir.mkdir(parents=True, exist_ok=True)

    for model in models:
        model_out = stems_dir / model
        model_out.mkdir(parents=True, exist_ok=True)

        cmd = [
            "demucs",
            "-n",
            model,
            "-o",
            str(model_out),
            str(audio),
        ]

        print(f"[Demucs] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    return stems_dir
