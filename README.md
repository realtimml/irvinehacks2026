# Roost

Roost is a sophisticated, web-controlled alarm clock built for the **Arduino UNO Q**. It integrates a Python backend with a JavaScript-based web interface to manage alarms that can trigger physical hardware actions, such as moving a servo motor or updating a 7-segment display.

## Features

* **Web-Based Interface**: A sleek, mobile-friendly UI to create, edit, and toggle alarms.
* **Real-Time Sync**: Uses WebSocket communication to synchronize alarm states between multiple web clients and the hardware.
* **Hardware Integration**:
    * **7-Segment Display**: Displays the current time in PST (UTC-8).
    * **Servo Control**: A servo motor is used to perform physical "wake" actions when an alarm is triggered.
* **Smart Scheduling**: Supports repeating alarms on specific days of the week.

## Hardware Requirements

* **Arduino UNO Q** (x1)
* **TM1637 7-Segment Display** (Connected to pins 6 and 7)
* **Servo Motor** (Connected to pin 9)
* **USB-C® Cable** (For power and programming)

## Software Requirements

* **Arduino App Lab**
* **Python Dependencies**: Essential libraries include `opencv-python-headless`, `ultralytics`, `pygame`, and `torch`.

## Project Structure

* **`python/main.py`**: The application backend that manages the alarm data store, handles WebSocket messages, and communicates with the Arduino via the Router Bridge.
* **`sketch/sketch.ino`**: The Arduino firmware that controls the TM1637 display and the servo motor based on commands received from the Python backend.
* **`assets/`**: Contains the frontend components, including `index.html`, `style.css`, and `app.js`.
* **`python/start_alarm.py`**: A helper script triggered when an alarm goes off.

## How it Works

1. **Time Management**: The Python backend tracks time in PST and sends regular updates to the Arduino to refresh the 7-segment display.
2. **Alarm Triggering**: When the current time matches a saved alarm, the backend notifies the web interface, initiates the alarm sequence via `start_alarm.py`, and calls the `fire_servo` function on the Arduino.
3. **Communication**: The system relies on the `WebUI` brick for the browser-to-Python link and the `Router Bridge` for the Python-to-Arduino link.

## Usage

1. Launch the application using **Arduino App Lab**.
2. Access the interface by navigating to `<UNO-Q-IP-ADDRESS>:7000` in your web browser.
3. Use the **"Add New"** button to set a time and select the days for your alarm.
4. The system automatically handles "loading" the servo (setting it to 0 degrees) via the background loop to ensure it is ready to fire.