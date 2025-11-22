#!/usr/bin/env python3
"""
Entire audio2score pipeline.
- Normalize
- Demucs (optional)
- BasicPitch (main + stems)
- MusicXML
- PDF
"""

import pathlib
from typing import List, Dict, Optional

from .preprocess import normalize_audio
from .demucs_engine import separate_stems
from .basicpitch_engine import run_basic_pitch, run_basic_pitch_per_stems
from .score_export import midi_to_musicxml, musicxml_to_pdf


def run_pipeline(
    audio: pathlib.Path,
    output_root: pathlib.Path,
    do_stems: bool,
    models: List[str],
    musescore_cmd: str,
    no_pdf: bool,
) -> Dict:

    print("=== audio2score pipeline start ===")
    print(f"Input Audio : {audio}")
    print(f"Output Root : {output_root}")
    print(f"Stems       : {do_stems} (models={models})")
    print(f"MuseScore   : {musescore_cmd}")
    print(f"PDF Export  : {not no_pdf}")

    output_root.mkdir(parents=True, exist_ok=True)

    # 1. Normalize
    normalized = normalize_audio(audio)

    stem_midis = {}

    # 2. Demucs
    if do_stems:
        stems = separate_stems(normalized, output_root, models=models)
        # 3. BasicPitch for each stem
        stem_midis = run_basic_pitch_per_stems(stems, output_root)

        # 4. Export for stems
        for stem_name, midi in stem_midis.items():
            xml = output_root / "xml" / stem_name / f"{midi.stem}.musicxml"
            pdf = output_root / "pdf" / stem_name / f"{midi.stem}.pdf"

            xml.parent.mkdir(parents=True, exist_ok=True)
            pdf.parent.mkdir(parents=True, exist_ok=True)

            midi_to_musicxml(midi, xml, musescore_cmd)
            if not no_pdf:
                musicxml_to_pdf(xml, pdf, musescore_cmd)

    # 5. BasicPitch for main
    midi_main = run_basic_pitch(normalized, output_root / "midi" / "main")

    # 6. Export main
    xml_main = output_root / f"{midi_main.stem}.musicxml"
    midi_to_musicxml(midi_main, xml_main, musescore_cmd)

    pdf_main = None
    if not no_pdf:
        pdf_main = output_root / f"{midi_main.stem}.pdf"
        musicxml_to_pdf(xml_main, pdf_main, musescore_cmd)

    return {
        "normalized": normalized,
        "main_midi": midi_main,
        "main_xml": xml_main,
        "main_pdf": pdf_main,
        "stems_midi": stem_midis,
    }
