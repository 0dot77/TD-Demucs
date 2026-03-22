"""
Demucs Worker - Subprocess for audio source separation.

TouchDesigner에서 subprocess로 실행되며, 오디오 파일을 입력받아
vocals, drums, bass, other 4개 스템으로 분리합니다.

Usage:
    python demucs_worker.py --input <audio_path> --output <output_dir> [--model htdemucs]
"""

import argparse
import json
import sys
import os
import time


def print_status(status: str, **kwargs):
    """JSON 형식으로 상태를 stdout에 출력합니다."""
    msg = {"status": status, "timestamp": time.time(), **kwargs}
    print(json.dumps(msg), flush=True)


def separate(input_path: str, output_dir: str, model_name: str = "htdemucs"):
    """Demucs를 사용하여 오디오를 분리합니다."""

    if not os.path.isfile(input_path):
        print_status("error", message=f"Input file not found: {input_path}")
        return False

    os.makedirs(output_dir, exist_ok=True)

    print_status("loading", message="Loading demucs model...")

    try:
        import torch
        from demucs.api import Separator
    except ImportError as e:
        print_status("error", message=f"Missing dependency: {e}. Run: pip install demucs")
        return False

    try:
        separator = Separator(model=model_name)
        print_status("processing", message=f"Separating: {os.path.basename(input_path)}")

        _, stems = separator.separate_audio_file(input_path)

        stem_paths = {}
        for stem_name, stem_audio in stems.items():
            stem_path = os.path.join(output_dir, f"{stem_name}.wav")
            separator.save_audio(stem_audio, stem_path, samplerate=separator.samplerate)
            stem_paths[stem_name] = stem_path
            print_status("stem_complete", stem=stem_name, path=stem_path)

        print_status("complete", stems=stem_paths)
        return True

    except Exception as e:
        print_status("error", message=str(e))
        return False


def main():
    parser = argparse.ArgumentParser(description="Demucs audio source separation worker")
    parser.add_argument("--input", required=True, help="Input audio file path")
    parser.add_argument("--output", required=True, help="Output directory for stems")
    parser.add_argument("--model", default="htdemucs", help="Model name (default: htdemucs)")
    args = parser.parse_args()

    success = separate(args.input, args.output, args.model)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
