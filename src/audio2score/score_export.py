#!/usr/bin/env python3
import pathlib
import subprocess
from typing import Optional


def export_score_with_musescore(
    midi_path: pathlib.Path,
    output_root: pathlib.Path,
    musescore_cmd: str = "mscore",
    no_pdf: bool = False,
) -> pathlib.Path:
    """
    MuseScore CLI を用いて
    - MIDI → MusicXML
    - MusicXML → PDF
    を行う。
    """
    midi_path = midi_path.resolve()
    score_dir = output_root / "score"
    score_dir.mkdir(parents=True, exist_ok=True)

    musicxml_path = score_dir / "main.musicxml"
    pdf_path = score_dir / "main.pdf"

    # MIDI -> MusicXML
    cmd_xml = [
        musescore_cmd,
        "-o",
        str(musicxml_path),
        str(midi_path),
    ]
    print(f"[MuseScore] MIDI → MusicXML: {' '.join(cmd_xml)}")
    subprocess.run(cmd_xml, check=True)

    if not no_pdf:
        cmd_pdf = [
            musescore_cmd,
            "-o",
            str(pdf_path),
            str(musicxml_path),
        ]
        print(f"[MuseScore] MusicXML → PDF: {' '.join(cmd_pdf)}")
        subprocess.run(cmd_pdf, check=True)

    return musicxml_path
