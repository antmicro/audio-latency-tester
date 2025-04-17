# Project overview

Audio latency is a key factor in determining the quality of the user experience in communication services.
A controlled delay is necessary for responsive and natural communication as it helps mitigate issues such as echo, timing issues, or a fragmented user experience.

The aim of this project is to provide a platform for measurement and characterization of audio latencies. 

The tester suite includes:
* [Audio latency tester board](https://github.com/antmicro/audio-latency-tester-board) - responsible for emitting sound with a speaker and collecting audio samples (in various sampling rates) from  a pair of microphones
* [Microphone board](https://github.com/antmicro/pdm-microphone-board) - houses PDM microphone with selectable left or right channel audio output
* [Software controller](https://github.com/antmicro/audio-latency-tester) - provides firmware for the RP2040 MCUs located on board Audio latency tester board as well as host PC application responsible for collecting, sending and automated analyzing audio samples

## Tester suite architecture
The tester system integrates two microphones, an audio codec, an audio power amplifier and a speaker. These peripherals are driven with two separate RP2040 MCU units that can synchronize via a shared GPIO signal. 

System architecture is presented below:

:::{figure-md}
![](img/audio-graph.png)

System architecture
:::
