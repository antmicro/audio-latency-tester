# Audio latency tester

Copyright (c) 2024-2025 [Antmicro](https://www.antmicro.com)

[![image](https://img.shields.io/badge/View%20on-Antmicro%20Open%20Source%20Portal-332d37?style=flat-square)](https://opensource.antmicro.com/projects/audio-latency-tester/)

![](doc/source/img/collage.png)

## Overview

The aim of this project is to provide a hardware and software platform for the measurement and characterization of audio latencies for XR, communication and similar use cases.
This repository contains the software for the two associated hardware boards.

## Project structure

Notable elements of this repository include:

* `.github/` - GitHub CI configuration
* `doc/` - Sphinx-based documentation for the project
* `audio_in_pdm/` - RP2040 firmware for audio input
* `audio_out/` - RP2040 firmware for audio output
* `include/` - RP2040 USB payload definitions
* `audio_capture.py` - Python application for a PC host responsible for collecting audio samples
* `audio_controller.py` - Python module for data transactions
* `audio_playback.py` - Python application for a PC host responsible for playing audio samples 
* `1s_44100_2ch_16b.wav` - Example recording of a 439 Hz tone

## Licensing

This project is published under the [Apache-2.0](LICENSE) license.
