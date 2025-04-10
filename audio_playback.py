import audio_controller
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Filename of the WAV file to play")
    parser.add_argument(
        "--timestamps-file", help="File where timestamp values will be written"
    )
    parser.add_argument(
        "--volume",
        help="Volume multiplier (default: 2000)",
    )
    args = parser.parse_args()

    timestamps_file = (
        "timestamps-playback.log"
        if args.timestamps_file is None
        else args.timestamps_file
    )
    volume = 2000 if args.volume is None else int(args.volume)

    ac = audio_controller.AudioController()
    ac.play_audio(Path(args.file), Path(timestamps_file), volume=volume)


if __name__ == "__main__":
    main()
