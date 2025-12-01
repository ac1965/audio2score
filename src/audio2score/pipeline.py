#!/usr/bin/env python3
import pathlib  # ← ★ これが抜けていた
from dataclasses import dataclass
from typing import List, Optional

from .preprocess import normalize_audio
from .demucs_engine import separate_stems
from .basicpitch_engine import run_basic_pitch
from .score_export import export_score_with_musescore


@dataclass
class PipelineResult:
    raw_wav: pathlib.Path
    normalized_wav: pathlib.Path
    stems_dir: pathlib.Path
    midi_path: pathlib.Path
    musicxml_path: pathlib.Path
    pdf_path: Optional[pathlib.Path]


def run_pipeline(
    audio: pathlib.Path,
    output_root: pathlib.Path,
    do_stems: bool = True,
    models: Optional[List[str]] = None,
    musescore_cmd: str = "musescore4",
    no_pdf: bool = False,
) -> PipelineResult:

    audio = audio.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    stem_name = audio.stem

    print(f"[Pipeline] Input: {audio}")

    # 1. 正規化
    normalized = normalize_audio(audio)

    # 2. Demucs ステム分離
    stems_dir = output_root / "stems"
    if do_stems:
        if models is None:
            models = ["htdemucs", "htdemucs_6s"]
        stems_dir = separate_stems(normalized, models, output_root)
    else:
        stems_dir.mkdir(parents=True, exist_ok=True)

    # 3. BasicPitch（入力名を保持）
    midi_path, _onnx_path = run_basic_pitch(
        normalized,
        output_root,
        stem_name=stem_name,
    )

    # 4. MuseScore（入力名を保持）
    musicxml_path = export_score_with_musescore(
        midi_path=midi_path,
        output_root=output_root,
        stem_name=stem_name,
        musescore_cmd=musescore_cmd,
        no_pdf=no_pdf,
    )

    pdf_path = output_root / "score" / f"{stem_name}.pdf"
    if no_pdf or not pdf_path.exists():
        pdf_path = None

    return PipelineResult(
        raw_wav=audio,
        normalized_wav=normalized,
        stems_dir=stems_dir,
        midi_path=midi_path,
        musicxml_path=musicxml_path,
        pdf_path=pdf_path,
    )
