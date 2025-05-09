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
        default="out.wav",
        help="Filename of the WAV file to save captured samples (default: out.wav)",
    )
    parser.add_argument(
        "--timestamps-file-play",
        default="timestamps_play.log",
        help="File where timestamp values will be written (play)",
    )
    parser.add_argument(
        "--timestamps-file-capture",
        default="timestamps_capture.log",
        help="File where timestamp values will be written (capture)",
    )
    parser.add_argument(
        "--volume-play",
        default=4000,
        type=int,
        help="Volume multiplier for playing (default: 4000)",
    )
    parser.add_argument(
        "--volume-capture",
        default=100,
        type=int,
        help="Volume multiplier for capture (default: 100)",
    )
    parser.add_argument(
        "--duration",
        default=None,
        type=float,
        help="Length of the capture in seconds (default: max available length)",
    )
    args = parser.parse_args()

    def run_player():
        """ Initializes the audio playback controller with arguments provided by argparse
        """
        ac = audio_controller.AudioController()
        ac.play_audio(
            Path(args.file), Path(args.timestamps_file_play), volume=args.volume_play
        )

    def run_recorder():
        """ Initializes the audio record controller with arguments provided by argparse
        """
        ac = audio_controller.AudioController()
        ac.start_recording(
            args.out_wav,
            Path(args.timestamps_file_capture),
            volume=args.volume_play,
            duration_s=args.duration,
            use_trigger=1,
        )

    recorder = Process(target=run_recorder)
    recorder.start()

    # The recorder needs to be configured and start waiting for trigger before the player is started.
    time.sleep(2)

    player = Process(target=run_player)
    player.start()

    player.join()
    recorder.join()


if __name__ == "__main__":
    main()
