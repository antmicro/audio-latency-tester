#!/bin/env python3

import click
import struct
import wave

def read_wav(file_path):
    try:
        with wave.open(file_path, 'rb') as wav_file:
            num_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            duration = num_frames / float(frame_rate)

            click.echo(f"Processing {file_path}:")
            click.echo(f"  Channels: {num_channels}")
            click.echo(f"  Sample Width: {sample_width} bytes")
            click.echo(f"  Frame Rate: {frame_rate} Hz")
            click.echo(f"  Duration: {duration:.2f} seconds")

            raw_data = wav_file.readframes(num_frames)
            # Format string for unpacking
            fmt = {1: 'B', 2: 'h', 3: '3B', 4: 'i'}[sample_width]  # 'B' (unsigned 8-bit), 'h' (signed 16-bit), etc.
            fmt = f"<{num_frames * num_channels}{fmt}"  # Little-endian format

            # Convert raw data into samples
            audio_data = struct.unpack(fmt, raw_data)
            return audio_data, 1/(num_channels * frame_rate)
    except wave.Error as e:
        click.echo(f"Error processing {file_path}: {e}")


def count_leading_zeros(data):
    count = 0
    for x in data:
        if x == 0:
            count += 1
        else:
            break
    return count


def sine_to_const(data):
    threshold = 0.6 * max(data)
    new_data = []
    for i in range(0, len(data)-1):
        if abs(data[i]) > threshold:
            new_data.append(threshold)
        else:
            new_data.append(0)

    keep_going = True
    id = 0
    while keep_going:
        try:
            id = new_data.index(0, id)
        except ValueError:
            break

        zeros = count_leading_zeros(new_data[id:])
        # adjust this if needed
        if zeros < 50:
            for i in range(id, id+zeros):
                new_data[i] = threshold
        else:
            id += zeros + 1

    new_data.append(new_data[-1])
    return new_data


def find_sound_start(data):
    """find the start of each time sound is detected"""
    res = []

    if data[0] != 0:
        res.append(0)

    for i in range(len(data)-1):
        if data[i] == 0 and data[i+1] != 0:
            res.append(i+1)
    return res


def find_sound_end(data):
    """find the end of each time sound is detected"""
    res = []
    for i in range(len(data)-1):
        if data[i] != 0 and data[i+1]==0:
            res.append(i+1)

    if data[-1] != 0:
        res.append(len(data)-1)

    return res


def process_wav(wav_file):
    audio, time_delta = read_wav(wav_file)
    threshed = sine_to_const(audio)

    starts = find_sound_start(threshed)
    stops = find_sound_end(threshed)

    # Filter indices where the duration is at least 10 samples
    filtered = [(s, e) for s, e in zip(starts, stops) if e - s >= 10]

    filtered_starts = [s for s, _ in filtered]
    filtered_stops = [e for _, e in filtered]

    return (audio, time_delta, (filtered_starts, filtered_stops))


def indices_to_timestamps(data, delta_time_per_sample):
    res = []
    for d in data:
        res.append(d * delta_time_per_sample)
    return res


def csv_entry(filename, timestamps_start, timestamps_end):
    event_timestamps = ";".join(str(ts) for ts in sorted(timestamps_start + timestamps_end))
    return f"{filename}; {event_timestamps}\n"


@click.command()
@click.argument('wav_files', nargs=-1, type=click.Path(exists=True))
def main(wav_files):
    """Calculate delay between the first wav file and any number of test wav files."""
    if not wav_files or len(wav_files) < 2:
        click.echo("Provide a reference wav file and at least one test wav file")
        return

    sounds_detected = []
    # 1/frequency, how much time between samples
    time_deltas = []
    audio_samples = []

    for wav_file in wav_files:
        if wav_file.lower().endswith('.wav'):

            audio_sample, time_delta, samples = process_wav(wav_file)

            audio_samples.append(audio_sample)
            sounds_detected.append(samples)
            time_deltas.append(time_delta)

        else:
            click.echo(f"Skipping {wav_file}: Not a WAV file.")

    (ref_start, ref_end) = sounds_detected[0]
    ref_audio_samples = audio_samples[0]
    time_delta_ref = time_deltas[0]
    test_names = wav_files[1:]
    test_data = sounds_detected[1:]
    time_deltas_test = time_deltas[1:]
    test_audio_samples = audio_samples[1:]

    ref_start_timestamps = indices_to_timestamps(ref_start, time_delta_ref)
    ref_end_timestamps = indices_to_timestamps(ref_end, time_delta_ref)

    csv_data = []
    csv_data.append("filename; event timestamps\n")
    csv_data.append(csv_entry(wav_files[0], ref_start_timestamps, ref_end_timestamps))

    # iterate over arrays with indices of events in wav data
    for (i, (start, end)) in enumerate(test_data):
        if len(start) != len(ref_start) or len(end) != len(ref_end):
            print(f"reference file: sound started {len(ref_start)} times, ended {len(ref_end)} times")
            print(f"{wav_files[i+1]} file: sound started {len(start)} times, ended {len(end)} times")

        start_diffs = []
        end_diffs = []

        start_timestamps = indices_to_timestamps(start, time_deltas_test[i])
        end_timestamps = indices_to_timestamps(end, time_deltas_test[i])
        csv_data.append(csv_entry(test_names[i], start_timestamps, end_timestamps))

        for j, (st, ref_st) in enumerate(zip(start, ref_start)):
            # convert array index to time
            test_start_time = st * time_deltas_test[i]

            ref_start_time = ref_st * time_delta_ref

            diff = test_start_time - ref_start_time
            start_diffs.append(diff)

        for j, (_end, _ref_end) in enumerate(zip(end, ref_end)):
            # convert array index to time
            test_end_time = _end * time_deltas_test[i]

            ref_end_time = _ref_end * time_delta_ref

            diff = test_end_time - ref_end_time
            end_diffs.append(diff)

    with open('results.csv', 'w') as _csv:
        _csv.writelines(csv_data)


if __name__ == "__main__":
    main()
