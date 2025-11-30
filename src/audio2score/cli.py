#!/usr/bin/env python3
import argparse
import pathlib
import sys

from .pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser("audio2score CLI")

    parser.add_argument("audio", help="Input WAV (or converted WAV)")
    parser.add_argument(
        "--output-dir",
        default="build",
        help="Output root directory (default: build)",
    )
    parser.add_argument(
        "--stems",
        action="store_true",
        help="Run Demucs stem separation",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        default=["htdemucs", "htdemucs_6s"],
        help="Demucs model names (default: htdemucs htdemucs_6s)",
    )
    parser.add_argument(
        "--musescore-cmd",
        default="mscore",
        help="MuseScore CLI command (mscore or musescore4)",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Do not export PDF (MusicXML only)",
    )

    args = parser.parse_args()

    audio = pathlib.Path(args.audio).resolve()
    out = pathlib.Path(args.output_dir).resolve()

    result = run_pipeline(
        audio=audio,
        output_root=out,
        do_stems=args.stems,
        models=args.models,
        musescore_cmd=args.musescore_cmd,
        no_pdf=args.no_pdf,
    )

    print("=== DONE ===")
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
