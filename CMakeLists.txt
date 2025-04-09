cmake_minimum_required(VERSION 3.20)

include("$ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake")
include("$ENV{PICO_EXTRAS_PATH}/external/pico_extras_import.cmake")

project(rp2040-i2s-timestamp C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

if (PICO_SDK_VERSION_STRING VERSION_LESS "2.1.0")
    message(FATAL_ERROR "Raspberry Pi Pico SDK version 2.1.0 (or later) required. Your version is ${PICO_SDK_VERSION_STRING}")
endif()

add_subdirectory("audio_out")
add_compile_definitions(AUDIO_CONTROLLER_BOARD)
add_subdirectory("audio_in_pdm")

