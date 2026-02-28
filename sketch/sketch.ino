// SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
//
// SPDX-License-Identifier: MPL-2.0

#include <Arduino_RouterBridge.h>
#include <TM1637Display.h>

const int CLK = 6;
const int DIO = 7;
const bool leading_zero = true;


void setup() {
    // pinMode(LED_BUILTIN, OUTPUT);
    // // Start with the LED OFF (HIGH state of the PIN)
    // digitalWrite(LED_BUILTIN, HIGH);

    // Bridge.begin();
    // Bridge.provide("set_led_state", set_led_state);
    TM1637Display display(CLK, DIO);
  
    display.clear();

    display.setBrightness(7);

    display.showNumberDecEx(123, 0x40, leading_zero);
}

void loop() {}

void set_led_state(bool state) {
    // LOW state means LED is ON
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);
}

