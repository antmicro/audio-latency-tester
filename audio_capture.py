import audio_controller
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", help="Filename of the WAV file to save captured samples"
    )
    parser.add_argument(
        "--timestamps-file",
        help="File where timestamp values will be written (default: timestamps.log)",
    )
    parser.add_argument(
        "--duration",
        help="Length of the capture in seconds (default: max available length)",
    )
    parser.add_argument(
        "--volume",
        help="Volume multiplier (default: 100)",
    )
    args = parser.parse_args()

    timestamps_file = (
        "timestamps-capture.log"
        if args.timestamps_file is None
        else args.timestamps_file
    )

    duration = None if args.duration is None else float(args.duration)
    volume = 100 if args.volume is None else int(args.volume)

    ac = audio_controller.AudioController()
    ac.start_recording(
        Path(args.file), Path(timestamps_file), volume=volume, duration_s=duration
    )


if __name__ == "__main__":
    main()
