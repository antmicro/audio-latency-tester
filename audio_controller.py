"""Main module for the audio system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import usb.core
import wave
import struct
import math

NUMBER_OF_CHANNELS = 8
NUMBER_OF_ADC_IN_GPIO = 4

CFG_PACKET_MAGIC_HDR = 0x50534341
TIMESTAMP_PACKET_MAGIC_HDR = 0x50534342
USB_PACKET_SIZE = 64
USB_VENDOR_ID = 0xCAFE
USB_PRODUCT_ID_PLAYBACK = 0x4010
USB_PRODUCT_ID_CAPTURE = 0x4011

CAPTURE_MAX_SAMPLE_COUNT = 64000


class FixedArray(object):
    def __init__(self, size, default_value=None):
        self.array = [default_value] * size

    def __repr__(self):
        return str(self.array)

    def __get__(self, instance, owner):
        return self.array

    def append(self, index=None, value=None):
        print(f"Append operation is forbidden")
        return

    def insert(self, index=None, value=None):
        if not index or index >= len(self.array):
            print("Index out of range")
            return
        self.array[index] = value


class DeviceShutdownDuration(Enum):
    """Enum class for device shutdown options."""

    MILISECONDS_5 = 0b11
    MILISECONDS_10 = 0b10
    MILISECONDS_25 = 0b01
    MILISECONDS_30 = 0b00


class PllFrequency(Enum):
    """Enum class for PLL frequency options."""

    MHz_12 = 0
    MHz_12_288 = 1
    MHz_13 = 2
    MHz_16 = 3
    MHz_19_2 = 4
    MHz_19_68 = 5
    MHz_24 = 6
    MHz_24_576 = 7


class Transport(ABC):
    """
    This class is interface that needs to be implemented by all classes that read and write to the hardware.
    """

    @abstractmethod
    def open(self) -> bool:
        """Opens the connection to allow reading/writing.

        Returns:
            True if connection is successfully opened, False otherwise.
        """
        pass

    @abstractmethod
    def close(self):
        """Closes the connection."""
        pass

    @abstractmethod
    def opened(self) -> bool:
        """Returns True if connection is opened, False otherwise."""
        pass

    @abstractmethod
    def send(self, address, value, len):
        """Writes a value to to address."""
        pass

    @abstractmethod
    def receive(self, address, len):
        """Reads a value from address."""
        pass


class I2CTransport(Transport):
    """
    This class is responsible for reading and writing to the hardware using I2C protocol.
    """

    def __init__(self, address: int):
        self.address = address

    def open(self) -> bool:
        """Opens the connection to allow reading/writing.
        Returns:
            True if connection is successfully opened, False otherwise.
        """
        return True

    def close(self):
        """Closes the connection."""
        pass

    def opened(self) -> bool:
        """Returns True if connection is opened, False otherwise."""
        return True

    def send(self, address, value, len):
        """Writes a value to to address."""
        pass

    def receive(self, address, len):
        """Reads a value from address."""
        pass


class SocketTransport(Transport):
    """
    This class is responsible for reading and writing to the hardware using socket protocol.
    """

    def __init__(self, file: Path):
        self.socket_file = file

    def open(self) -> bool:
        """Opens the connection to allow reading/writing.
        Returns:
            True if connection is successfully opened, False otherwise.
        """
        self.socket = open(self.socket_file, "rw")
        return True

    def close(self):
        """Closes the connection."""
        pass

    def opened(self) -> bool:
        """Returns True if connection is opened, False otherwise."""
        return True  # TODO: Implement

    def send(self, address, value, len):
        """Writes a value to to address."""
        pass

    def receive(self, address, len):
        """Reads a value from address."""
        pass


@dataclass
class ChannelConfiguration:
    channel_slot: int = 0  # Convert to enum
    channel_output: int = 0  # Convert to enum


@dataclass
class ControllerConfiguration:
    pll_frequency: PllFrequency = PllFrequency.MHz_12
    fs_mode: int = 0  # Convert to enum..
    # More settings


@dataclass
class GPIOConfiguration:
    output_drive: int = 0  # Convert to enum
    mode: int = 0  # Convert to enum


class InGPIOConfiguration:
    output_drive: int = 0  # Convert to enum
    mode: int = 0  # Convert to enum


@dataclass
class InterruptSettings:
    readback_configuration: bool = False  # Convert to enum
    event_configuration: int = 0  # Convert to enum
    polarity: bool = False  # Convert to enum
    interrupt_mask: int = 0  # Convert to enum


class ADCSettings:
    """Main settings class for the ADC.
    Contains all the settings for the ADC controlling microphones.
    """

    shutdown_time: DeviceShutdownDuration = DeviceShutdownDuration.MILISECONDS_25
    channels_configuration: FixedArray = FixedArray(
        NUMBER_OF_CHANNELS, ChannelConfiguration()
    )
    controller_configuration: ControllerConfiguration = ControllerConfiguration()
    gpio_configuration: GPIOConfiguration = GPIOConfiguration()
    in_gpio_configuration: FixedArray = FixedArray(
        NUMBER_OF_ADC_IN_GPIO, InGPIOConfiguration()
    )
    interrupt_settings: InterruptSettings = InterruptSettings()

    @staticmethod
    def initialize_from_yaml(path: Path):
        """Constructs Settings class from a yaml file."""
        return ADCSettings()

    def save_to_yaml(self, path: Path):
        """Saves current settings to a yaml file."""
        pass


@dataclass
class AmplifierClockConfiguration:
    clock_settings: int = 0  # Convert to enum
    pll_divider: int = 0  # Convert to enum
    pll_multiplier: int = 0  # Convert to enum
    # More settings


@dataclass
class AudioConfiguration:
    interface: str = "I2S"  # Convert to enum
    data_word_length: int = 16  # Convert to enum
    # More settings


@dataclass
class DACConfiguration:
    active: bool = False
    mute: bool = False
    auto_mute: int = 0  # Convert to enum
    # More settings


class AmplifierSettings:
    """Main settings class for the amplifier.
    Contains all the settings for the amplifier controlling speakers.
    """

    clock_configuration: AmplifierClockConfiguration = AmplifierClockConfiguration()
    audio_configuration: AudioConfiguration = AudioConfiguration()
    dac_configuration: DACConfiguration = DACConfiguration()

    @staticmethod
    def initialize_from_yaml(path: Path):
        """Constructs Settings class from a yaml file."""
        return AmplifierSettings()

    def save_to_yaml(self, path: Path):
        """Saves current settings to a yaml file."""
        pass


class ADCController:
    """Class for controlling the ADC.
    This class is responsible for managing the ADC settings
    and directly interfacing with the ADC hardware.
    """

    settings: ADCSettings = ADCSettings()

    def __init__(
        self, transport: Transport, settings: ADCSettings | Path | None = None
    ):
        """Initializes the ADC controller with provided settings."""
        self.transport = transport
        if settings is None:
            return
        elif isinstance(settings, ADCSettings):
            self.settings = settings
        elif isinstance(settings, Path):
            self.settings = ADCSettings.initialize_from_yaml(settings)
        pass

    def reset(self):
        """Resets ADC and places all register values in their default power-on-reset state."""
        pass

    def get_sample_rate(self):
        """Returns detected sample rate of the ASI bus"""
        pass

    def get_bclk_to_fsync_ratio(self):
        """Returns the ratio of BCLK to FSCLK"""
        pass

    def write_register(self, address, value, len):
        """Writes a value to a register."""
        self.reader_writer.send(address, value, len)

    def read_register(self, address, len):
        """Reads a value from a register."""
        self.reader_writer.receive(address, len)


class AmplifierController:
    """Class for controlling the amplifier.
    This class is responsible for managing the amplifier settings
    and directly interfacing with the amplifier hardware.
    """

    settings: AmplifierSettings = AmplifierSettings()

    def __init__(
        self, transport: Transport, settings: AmplifierSettings | Path | None = None
    ):
        """Initializes the Amplifier controller with provided settings."""
        self.transport = transport
        if settings is None:
            return
        elif isinstance(settings, AmplifierSettings):
            self.settings = settings
        elif isinstance(settings, Path):
            self.settings = AmplifierSettings.initialize_from_yaml(settings)
        pass

    def reset(self):
        """Resets the amplifier."""
        pass

    def write_register(self, address, value, len):
        """Writes a value to a register."""
        self.transport.send(address, value, len)
        pass

    def read_register(self, address, len):
        """Reads a value from a register."""
        self.transport.receive(address, len)
        pass


class AudioController:
    """Main controller class for the audio system.
    This class is responsible for managing the ADC and Amplifier controllers
    and contains methods for recording and playing audio.
    """

    adc_controller: ADCController
    amplifier_controller: AmplifierController

    def __init__(
        self,
        adc_controller: ADCController | None = None,
        amplifier_controller: AmplifierController | None = None,
    ):
        if adc_controller is not None:
            self.adc_controller = adc_controller
        if amplifier_controller is not None:
            self.amplifier_controller = amplifier_controller

    def start_recording(
        self,
        filename: Path = "recording.wav",
        timestamps_filename: Path = "timestamps.log",
        file_format: str = "WAV",
        override_existing_file: bool = False,
        duration_s: float | None = None,
        volume: int = 100,
        use_trigger: bool = False,
    ):
        """Starts recording audio data.

        Args:
            filename (str): Name of the file to save the recording to.
            file_format (str): Format of the file to save the recording to.
            override_existing_file (bool): Whether to override existing file with the same name.
            duration_s (float): Duration of the recording in seconds. If None, recording will continue until `stop_recording` is called.
        """

        sample_rate = 16000
        sample_depth = 2
        channels_count = 1

        samples_count = CAPTURE_MAX_SAMPLE_COUNT

        if duration_s is not None:
            samples_count = min(
                samples_count, int(duration_s * channels_count * sample_rate)
            )

        try:
            # Locate the USB device
            dev = usb.core.find(
                idVendor=USB_VENDOR_ID, idProduct=USB_PRODUCT_ID_CAPTURE
            )
            if dev is None:
                raise ValueError("USB Device not found")

            cfg = dev[0]
            intf = cfg[(0, 0)]
            ep_in, ep_out = intf[1], intf[0]

            # Prepare and send configuration packet
            config_data = struct.pack(
                "IIIIIII",
                CFG_PACKET_MAGIC_HDR,
                samples_count,
                sample_rate,
                sample_depth,
                channels_count,
                volume,
                int(use_trigger),
            )
            ep_out.write(config_data)

            with wave.open(str(filename), "w") as wavfile:
                wavfile.setnchannels(1)
                wavfile.setsampwidth(2)
                wavfile.setframerate(16000)

                packet_count = math.ceil(
                    samples_count * sample_depth * channels_count / USB_PACKET_SIZE
                )
                for _ in range(packet_count):
                    samples_raw = ep_in.read(USB_PACKET_SIZE, timeout=5000)
                    wavfile.writeframes(samples_raw)

            # Read timestamp packet
            timestamp_packet_raw = ep_in.read(USB_PACKET_SIZE, timeout=5000)
            timestamp_header, timestamp_count = struct.unpack(
                "II", timestamp_packet_raw[:8]
            )

            if timestamp_header != TIMESTAMP_PACKET_MAGIC_HDR:
                raise RuntimeError("Malformed timestamp packet header")

            print(f"Number of timestamps: {timestamp_count}")

            # Read timestamps
            timestamps = []
            for _ in range(math.ceil(timestamp_count / 8)):
                timestamp_raw = ep_in.read(USB_PACKET_SIZE)
                timestamps.extend(struct.unpack("QQQQQQQQ", timestamp_raw))

            ep_in.read(USB_PACKET_SIZE)  # Acknowledge final packet

            with open(str(timestamps_filename), "a") as f:
                for ts in timestamps:
                    f.write(f"{ts}\n")

        except usb.core.USBError as e:
            print(f"USB Error: {e}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except wave.Error:
            print(f"Error: Invalid WAV file format: '{filename}'.")
        except struct.error:
            print("Error: Failed to unpack data (possibly malformed packet).")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def stop_recording(self):
        """Stops recording audio data."""
        pass

    def play_audio(
        self,
        filename: Path,
        timestamps_filename: Path = "timestamps.log",
        volume: int = 2000,
        use_trigger: bool = True,
    ):
        """Plays audio from a file through a USB device."""
        try:
            # Locate the USB device
            dev = usb.core.find(
                idVendor=USB_VENDOR_ID, idProduct=USB_PRODUCT_ID_PLAYBACK
            )
            if dev is None:
                raise ValueError("USB Device not found")

            cfg = dev[0]
            intf = cfg[(0, 0)]
            ep_in, ep_out = intf[1], intf[0]

            # Open the WAV file
            with wave.open(str(filename), "rb") as wav_file:
                channels = wav_file.getnchannels()
                framerate = wav_file.getframerate()
                sampwidth = wav_file.getsampwidth()
                frame_count = wav_file.getnframes()

                print(f"Channels: {channels}")
                print(f"Sampling Frequency: {framerate} Hz")
                print(f"Sample Count: {frame_count}")
                print(f"Depth (bytes per sample): {sampwidth}")
                print(f"use trigger: {use_trigger}")

                # Prepare and send configuration packet
                config_data = struct.pack(
                    "IIIIIII",
                    CFG_PACKET_MAGIC_HDR,
                    frame_count,
                    framerate,
                    sampwidth,
                    channels,
                    volume,
                    int(use_trigger),
                )
                ep_out.write(config_data)

                frames_per_packet = USB_PACKET_SIZE // (sampwidth * channels)
                print(f"Frames per packet: {frames_per_packet}")

                # Stream audio frames
                while frames := wav_file.readframes(frames_per_packet):
                    ep_out.write(frames)

            # Read timestamp packet
            timestamp_packet_raw = ep_in.read(USB_PACKET_SIZE, timeout=5000)
            timestamp_header, timestamp_count = struct.unpack(
                "II", timestamp_packet_raw[:8]
            )

            if timestamp_header != TIMESTAMP_PACKET_MAGIC_HDR:
                raise RuntimeError("Malformed timestamp packet header")

            print(f"Number of timestamps: {timestamp_count}")

            # Read timestamps
            timestamps = []
            for _ in range(math.ceil(timestamp_count / 8)):
                timestamp_raw = ep_in.read(USB_PACKET_SIZE)
                timestamps.extend(struct.unpack("QQQQQQQQ", timestamp_raw))

            ep_in.read(USB_PACKET_SIZE)  # Acknowledge final packet

            # Display timestamps
            with open(str(timestamps_filename), "a") as f:
                for ts in timestamps:
                    f.write(f"{ts}\n")

        except usb.core.USBError as e:
            print(f"USB Error: {e}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except wave.Error:
            print(f"Error: Invalid WAV file format: '{filename}'.")
        except struct.error:
            print("Error: Failed to unpack data (possibly malformed packet).")
        except Exception as e:
            print(f"Unexpected error: {e}")
