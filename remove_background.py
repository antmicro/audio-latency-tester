import librosa
import numpy as np
import soundfile as sf

def remove_background(input_wav, background_wav, output_wav):
    # Load audio files 
    samples_input, sampling_rate_input = librosa.load(input_wav, sr=None, mono=True)
    samples_background, sampling_rate_background = librosa.load(background_wav, sr=sampling_rate_input, mono=True)

    # Short-time Fourier transform
    input_spectogram = librosa.stft(samples_input)
    background_spectogram = librosa.stft(samples_background)

    # Spectral subtraction (magnitude only)
    mag_output, phase_output = np.abs(input_spectogram), np.angle(input_spectogram)
    mag_background = np.abs(background_spectogram)

    # Subtract background magnitude 
    # flooring to avoid negatives
    mag_clean = np.maximum(mag_output - mag_background, 0)

    # Reconstruct complex Short-time Fourier transform
    D_clean = mag_clean * np.exp(1j * phase_output)

    # Inverse Short-time Fourier transform
    y_clean = librosa.istft(D_clean)

    # Save result
    sf.write(output_wav, y_clean, sampling_rate_input)
    print(f"Saved audio to {output_wav}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Remove audio bleed from source speaker using spectral subtraction")
    parser.add_argument("input", help="WAV file to be filtered")
    parser.add_argument("reference", help="WAV file with only the bleeding audio")
    parser.add_argument("output", help="Output WAV file with background removed")
    
    args = parser.parse_args()
    remove_background(args.input, args.reference, args.output)
