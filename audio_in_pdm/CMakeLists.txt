cmake_minimum_required(VERSION 3.20)

project(rp2040-i2s-timestamp-audio-in)

pico_sdk_init()

add_executable(rp2040-i2s-timestamp-audio-in
  main.c
  ${CMAKE_CURRENT_LIST_DIR}/../third_party/pdm_microphone/pdm_microphone.c
  ${CMAKE_CURRENT_LIST_DIR}/../third_party/usb_descriptors_audio_in_pdm.c
  ${CMAKE_CURRENT_LIST_DIR}/../third_party/OpenPDM2PCM/OpenPDMFilter.c
)

pico_generate_pio_header(rp2040-i2s-timestamp-audio-in ${CMAKE_CURRENT_LIST_DIR}/../third_party/pdm_microphone/pdm_microphone.pio)

target_link_libraries(rp2040-i2s-timestamp-audio-in PRIVATE
  pico_stdlib
  pico_audio_i2s
  hardware_resets
  hardware_irq
  hardware_dma
  hardware_pio
  hardware_timer
  tinyusb_device
  tinyusb_board
)

target_compile_definitions(rp2040-i2s-timestamp-audio-in PRIVATE
  PICO_AUDIO_I2S_DATA_PIN=11
  PICO_AUDIO_I2S_CLOCK_PIN_BASE=9
  PICO_DEFAULT_UART=0
  GPIO_TRIGGER_PIN=20
)

target_include_directories(rp2040-i2s-timestamp-audio-in PUBLIC
  ${CMAKE_CURRENT_LIST_DIR}
)

target_include_directories(rp2040-i2s-timestamp-audio-in PUBLIC
  ${CMAKE_CURRENT_LIST_DIR}/../include
)

target_include_directories(rp2040-i2s-timestamp-audio-in PUBLIC
  ${CMAKE_CURRENT_LIST_DIR}/../third_party
)

pico_add_extra_outputs(rp2040-i2s-timestamp-audio-in)
