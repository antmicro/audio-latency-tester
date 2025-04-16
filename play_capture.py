import audio_controller
from pathlib import Path
import argparse
import time
from multiprocessing import Process


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Filename of the WAV file to play")
    parser.add_argument(
        "--out-wav",
        help="Filename of the WAV file to save captured samples (default: out.wav)",
    )
    parser.add_argument(
        "--timestamps-file-play",
        help="File where timestamp values will be written (play)",
    )
    parser.add_argument(
        "--timestamps-file-capture",
        help="File where timestamp values will be written (capture)",
    )
    parser.add_argument(
        "--volume-play",
        help="Volume multiplier for playing (default: 4000)",
    )
    parser.add_argument(
        "--volume-capture",
        help="Volume multiplier for capture (default: 100)",
    )
    parser.add_argument(
        "--duration",
        help="Length of the capture in seconds (default: max available length)",
    )
    args = parser.parse_args()

    out_wav = "out.wav" if args.out_wav is None else args.out_wav

    timestamps_play = (
        "timestamps_play.log"
        if args.timestamps_file_play is None
        else args.timestamps_file_play
    )
    timestamps_capture = (
        "timestamps_capture.log"
        if args.timestamps_file_capture is None
        else args.timestamps_file_capture
    )

    volume_play = 4000 if args.volume_play is None else int(args.volume_play)
    volume_capture = 100 if args.volume_capture is None else int(args.volume_capture)

    duration = None if args.duration is None else float(args.duration)

    def run_player():
        ac = audio_controller.AudioController()
        ac.play_audio(Path(args.file), Path(timestamps_play), volume=volume_play)

    def run_recorder():
        ac = audio_controller.AudioController()
        ac.start_recording(
            out_wav,
            Path(timestamps_capture),
            volume=volume_capture,
            duration_s=duration,
            use_trigger=1,
        )

    recorder = Process(target=run_recorder)
    recorder.start()

    # TODO the recorder needs to be configured and start waiting for trigger
    # before the player is started.
    # We should do the configuration and recording steps in separate functions
    # instead of sleeping here
    time.sleep(2)

    player = Process(target=run_player)
    player.start()

    player.join()
    recorder.join()


if __name__ == "__main__":
    main()
