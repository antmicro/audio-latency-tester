# Installation and setup

## Installing dependencies
`CMake` (3.20 or newer), `Python3` and the `ARM toolchain` are required to build the project.

To install the dependencies on Debian Bookworm, run:

```sh
apt install cmake python3 python3-venv build-essential gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib libusb-1.0-0-dev
```

Clone the audio-latency-tester repository:

```sh
git clone https://github.com/antmicro/audio-latency-tester.git
cd audio-latency-tester
```

To run the project, it is also required to install `PyUSB`:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install pyusb click
```

## Building RP2040 firmware

Install `pico-sdk` and `pico-extras` :

```sh
git clone --recurse-submodules --branch 2.1.0 https://github.com/raspberrypi/pico-sdk.git
git clone --recurse-submodules --branch sdk-2.1.0 https://github.com/raspberrypi/pico-extras.git
```

The build system uses environment variables to find these repositories:

```sh
export PICO_SDK_PATH=$(pwd)/pico-sdk
export PICO_EXTRAS_PATH=$(pwd)/pico-extras
```


To build the project, run:

```sh
cmake -S . -B build
cmake --build build -j$(nproc)
```

If the build succeeded, the following files should be present in build directory:

* `build/audio_out/rp2040-i2s-timestamp.elf`
* `build/audio_out/rp2040-i2s-timestamp.uf2`
* `build/audio_in_pdm/rp2040-i2s-timestamp-audio-in.elf`
* `build/audio_in_pdm/rp2040-i2s-timestamp-audio-in.uf2`

## Flashing hardware

### Install Picotool

In order to flash the devices, `picotool` is required.
The installation instructions can be found in this [README](https://github.com/raspberrypi/picotool/blob/master/README.md).

### Flashing firmware to the board

The [Audio latency tester board](https://github.com/antmicro/audio-latency-tester-board) consists of 2 independent RP2040 MCUs - one for audio input, other for audio output.
Each of them has to be flashed with the `.uf2` file prepared in the previous steps.

#### Flashing Audio input firmware

* Connect MCU-1 USB-C (the port labeled as `USB-C Mics`) to your PC. LEDs should light up.

:::{figure-md}
![](img/mcu-1-usb.png)

MCU-1 USB-C connection
:::


* Press and hold the `MCU-1 BOOTSEL` ([`SW2`](#SW2)) button.

* Press and release the `MCU-1 RST` ([`SW1`](#SW1)) button.

* Release the `MCU-1 BOOTSEL` button.

* With `lsusb`, you should see that the device is recognized as a USB device `Raspberry Pi RP2 Boot`

```console
Bus 001 Device 099: ID 2e8a:0003 Raspberry Pi RP2 Boot

```

* Use `picotool` to flash the device and execute the program immediately:

```sh
picotool load -x build/audio_in_pdm/rp2040-i2s-timestamp-audio-in.uf2
```

Expected output:

```console
Loading into Flash:   [==============================]  100%

The device was rebooted to start the application.
```
* With `lsusb`, you should see that the device is recognized as a USB device with ID `cafe:4010`

```console
Bus 003 Device 012: ID cafe:4010 Raspberry Pi RP2040
```

#### Flashing Audio output firmware

* If it's still connected - remove the USB-C from the previous step.
* Connect MCU-2 USB-C (the port labeled as `USB-C Speaker`) to your PC. LEDs should light up.

:::{figure-md}
![](img/mcu-2-usb.png)

MCU-2 USB-C connection
:::


* Press and hold the `MCU-2 BOOTSEL` ([`SW4`](#SW4)) button.

* Press and release the `MCU-2 RST` ([`SW3`](#SW3)) button.

* Release the `MCU-2 BOOTSEL` button.

* With `lsusb`, you should see that the device is recognized as a USB device `Raspberry Pi RP2 Boot`

```console
Bus 001 Device 101: ID 2e8a:0003 Raspberry Pi RP2 Boot

```

* Use `picotool` to flash the device and execute the program immediately:

```sh
picotool load -x build/audio_out/rp2040-i2s-timestamp.uf2
```
* With `lsusb`, you should see that the device is recognized as a USB device with ID `cafe:4011`

```console
Bus 003 Device 012: ID cafe:4011 Raspberry Pi RP2040
```