// SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
//
// SPDX-License-Identifier: MPL-2.0

#include <Arduino_RouterBridge.h>
#include <TM1637Display.h>
#include <Servo.h>

const int CLK = 6;
const int DIO = 7;
const int SERVO_PIN = 9;
const bool leading_zero = false;

TM1637Display display(CLK, DIO);
Servo servo;


void setup() {
    // pinMode(LED_BUILTIN, OUTPUT);
    // // Start with the LED OFF (HIGH state of the PIN)
    // digitalWrite(LED_BUILTIN, HIGH);

    // Bridge.begin();
    // Bridge.provide("set_led_state", set_led_state);
    servo.attach(SERVO_PIN);
    servo.write(0);

    display.clear();

    display.setBrightness(7);

    // display.showNumberDecEx(123, 0x40, leading_zero);

    Bridge.begin();
    Bridge.provide("set_clock_time", set_clock_time);
}

void loop() {}

// void set_led_state(bool state) {
//     // LOW state means LED is ON
//     digitalWrite(LED_BUILTIN, state ? LOW : HIGH);
// }

void set_clock_time(int time) {
    display.showNumberDecEx(time, 0x40, leading_zero);
}

void load_servo() {
    servo.write(0);
}

void fire_servo() {
    servo.write(90);
}