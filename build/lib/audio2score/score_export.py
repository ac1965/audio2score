#!/usr/bin/env python3
import pathlib
import subprocess
import sys

from music21 import converter


def run_musescore(input_path: pathlib.Path, output_path: pathlib.Path, cmd: str) -> bool:
    call = [cmd, "-o", str(output_path), str(input_path)]
    print(f"[musescore] {' '.join(call)}")
    try:
        subprocess.run(call, check=True)
        return True
    except Exception as e:
        print(f"[musescore] Failed: {e}", file=sys.stderr)
        return False


def midi_to_musicxml(midi: pathlib.Path, xml: pathlib.Path, musescore_cmd: str):
    if run_musescore(midi, xml, musescore_cmd):
        return xml

    print("[fallback] music21 MIDI→MusicXML")
    score = converter.parse(str(midi))
    score.write("musicxml", fp=str(xml))
    return xml


def musicxml_to_pdf(xml: pathlib.Path, pdf: pathlib.Path, musescore_cmd: str):
    if run_musescore(xml, pdf, musescore_cmd):
        return pdf
    return None
