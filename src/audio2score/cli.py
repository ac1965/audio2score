#!/usr/bin/env python3
import argparse
import pathlib
import sys

from .pipeline import run_pipeline


def main():
    p = argparse.ArgumentParser("audio2score CLI")

    p.add_argument("audio", help="Input WAV (or converted WAV)")
    p.add_argument("--output-dir", default="build")
    p.add_argument("--stems", action="store_true")
    p.add_argument("--models", nargs="*", default=["htdemucs", "htdemucs_6s"])
    p.add_argument("--musescore-cmd", default="mscore")
    p.add_argument("--no-pdf", action="store_true")

    args = p.parse_args()

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


if __name__ == "__main__":
    sys.exit(main())
