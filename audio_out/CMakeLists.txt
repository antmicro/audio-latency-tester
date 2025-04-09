cmake_minimum_required(VERSION 3.20)

project(rp2040-i2s-timestamp-audio-out)

pico_sdk_init()

add_executable(rp2040-i2s-timestamp
  main.c
  usb_descriptors.c
)

target_link_libraries(rp2040-i2s-timestamp PRIVATE
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

target_compile_definitions(rp2040-i2s-timestamp PRIVATE
  USE_AUDIO_I2S=1
  PICO_AUDIO_I2S_DATA_PIN=16
  PICO_AUDIO_I2S_CLOCK_PIN_BASE=17
  PICO_DEFAULT_UART=0
  GPIO_MAX98357_ENABLE=23
  GPIO_TRIGGER_PIN=20
)

target_include_directories(rp2040-i2s-timestamp PUBLIC
  ${CMAKE_CURRENT_LIST_DIR}
)

target_include_directories(rp2040-i2s-timestamp PUBLIC
  ${CMAKE_CURRENT_LIST_DIR}/../include
)

pico_add_extra_outputs(rp2040-i2s-timestamp)
