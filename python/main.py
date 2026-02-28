# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

from arduino.app_utils import *
from arduino.app_bricks.web_ui import WebUI

import time
from datetime import datetime

# ============================================
# Alarm Data Store (in-memory)
# ============================================
# Each alarm: { "id": int, "time": "HH:MM", "days": ["M","W","F"], "enabled": True }
alarms = {}
alarm_id_counter = 1

# Map frontend day abbreviations to Python weekday indices (Monday=0 ... Sunday=6)
DAY_TO_WEEKDAY = {
    "M": 0,   # Monday
    "T": 1,   # Tuesday
    "W": 2,   # Wednesday
    "Th": 3,  # Thursday
    "F": 4,   # Friday
    "Sa": 5,  # Saturday
    "S": 6,   # Sunday
}

WEEKDAY_TO_DAY = {v: k for k, v in DAY_TO_WEEKDAY.items()}


def convert_12h_to_24h(time_12h):
    """Convert '08:00 AM' format to '08:00' (24h) format."""
    parts = time_12h.strip().split(" ")
    if len(parts) != 2:
        return time_12h  # Already 24h or malformed
    time_part, ampm = parts
    hh, mm = time_part.split(":")
    hh = int(hh)
    if ampm.upper() == "PM" and hh != 12:
        hh += 12
    elif ampm.upper() == "AM" and hh == 12:
        hh = 0
    return f"{hh:02d}:{mm}"


def convert_24h_to_12h(time_24h):
    """Convert '08:00' (24h) to '08:00 AM' (12h) format."""
    hh, mm = time_24h.split(":")
    hh = int(hh)
    ampm = "AM" if hh < 12 else "PM"
    if hh == 0:
        hh = 12
    elif hh > 12:
        hh -= 12
    return f"{hh:02d}:{mm} {ampm}"


def get_alarms_list():
    """Return all alarms as a list with 12h time format for the frontend."""
    result = []
    for alarm in alarms.values():
        result.append({
            "id": alarm["id"],
            "time": convert_24h_to_12h(alarm["time"]),
            "days": alarm["days"],
            "enabled": alarm["enabled"],
        })
    return result


# ============================================
# Socket.IO Handlers
# ============================================

def on_get_alarms(client, data):
    """Send the full alarm list to the requesting client."""
    print(f"[Alarms] Client requested alarm list")
    ui.send_message("alarms_list", {"alarms": get_alarms_list()}, client)


def on_create_alarm(client, data):
    """Create a new alarm from frontend data."""
    global alarm_id_counter

    time_str = data.get("time", "")
    days = data.get("days", [])

    # Convert 12h to 24h for internal storage
    time_24h = convert_12h_to_24h(time_str)

    alarm_id = alarm_id_counter
    alarm_id_counter += 1
    alarms[alarm_id] = {
        "id": alarm_id,
        "time": time_24h,
        "days": days,
        "enabled": True,
    }

    print(f"[Alarms] Created alarm #{alarm_id}: {time_24h} on {', '.join(days)}")

    # Broadcast updated list to all clients
    ui.send_message("alarm_changed", {"alarms": get_alarms_list()})


def on_update_alarm(client, data):
    """Update an existing alarm."""
    alarm_id = data.get("id")
    if alarm_id is None:
        return

    alarm_id = int(alarm_id)

    if alarm_id not in alarms:
        print(f"[Alarms] Alarm #{alarm_id} not found for update")
        return

    if "time" in data:
        alarms[alarm_id]["time"] = convert_12h_to_24h(data["time"])
    if "days" in data:
        alarms[alarm_id]["days"] = data["days"]
    if "enabled" in data:
        alarms[alarm_id]["enabled"] = data["enabled"]

    alarm = alarms[alarm_id]
    print(f"[Alarms] Updated alarm #{alarm_id}: {alarm['time']} on {', '.join(alarm['days'])} (enabled={alarm['enabled']})")

    # Broadcast updated list to all clients
    ui.send_message("alarm_changed", {"alarms": get_alarms_list()})


def on_delete_alarm(client, data):
    """Delete an alarm by ID."""
    alarm_id = data.get("id")
    if alarm_id is None:
        return

    alarm_id = int(alarm_id)

    if alarm_id in alarms:
        removed = alarms.pop(alarm_id)
        print(f"[Alarms] Deleted alarm #{alarm_id}: {removed['time']}")
    else:
        print(f"[Alarms] Alarm #{alarm_id} not found for deletion")
        return

    # Broadcast updated list to all clients
    ui.send_message("alarm_changed", {"alarms": get_alarms_list()})


def on_toggle_alarm(client, data):
    """Toggle an alarm's enabled state."""
    alarm_id = data.get("id")
    enabled = data.get("enabled")
    if alarm_id is None or enabled is None:
        return

    alarm_id = int(alarm_id)

    if alarm_id not in alarms:
        print(f"[Alarms] Alarm #{alarm_id} not found for toggle")
        return
    alarms[alarm_id]["enabled"] = bool(enabled)

    state_str = "enabled" if enabled else "disabled"
    print(f"[Alarms] Alarm #{alarm_id} {state_str}")

    # Broadcast updated list to all clients
    ui.send_message("alarm_changed", {"alarms": get_alarms_list()})


# ============================================
# Alarm Checker — runs inside the main loop
# ============================================
# Tracks which alarms have already fired this minute to avoid duplicate triggers
already_triggered = set()
last_check_time = 0  # timestamp of last alarm check


def loop():
    """Called repeatedly by App.run(). Checks if any alarm should fire."""
    global already_triggered, last_check_time

    # Only check every ~15 seconds for efficiency
    current_timestamp = time.time()
    if current_timestamp - last_check_time < 15:
        return
    last_check_time = current_timestamp

    now = datetime.now()
    current_time = f"{now.hour:02d}:{now.minute:02d}"
    current_weekday = now.weekday()  # 0=Monday ... 6=Sunday
    current_day_abbr = WEEKDAY_TO_DAY.get(current_weekday, "")
    minute_key = f"{now.hour:02d}:{now.minute:02d}"

    for alarm_id, alarm in alarms.items():
        if not alarm["enabled"]:
            continue

        trigger_key = f"{alarm_id}_{minute_key}"

        if trigger_key in already_triggered:
            continue

        # Check if time matches
        if alarm["time"] != current_time:
            continue

        # Check if today is in the alarm's day list
        # If no days selected, treat as a one-time alarm (fires any day)
        if alarm["days"] and current_day_abbr not in alarm["days"]:
            continue

        # 🔔 ALARM TRIGGERED!
        already_triggered.add(trigger_key)
        time_12h = convert_24h_to_12h(alarm["time"])
        days_str = ", ".join(alarm["days"]) if alarm["days"] else "Every day"
        print(f"\n{'=' * 50}")
        print(f"🔔 ALARM TRIGGERED: {time_12h} on {days_str}")
        print(f"   Alarm ID: #{alarm_id}")
        print(f"   Current time: {now.strftime('%I:%M %p')}")
        print(f"{'=' * 50}\n")

        # Notify frontend
        ui.send_message("alarm_triggered", {
            "id": alarm_id,
            "time": time_12h,
            "days": alarm["days"],
        })

    # Clean up old trigger keys (keep only current minute)
    already_triggered = {k for k in already_triggered if k.endswith(f"_{minute_key}")}


# ============================================
# Initialize & Start
# ============================================

# Initialize WebUI
ui = WebUI()

# Register socket message handlers
ui.on_message("get_alarms", on_get_alarms)
ui.on_message("create_alarm", on_create_alarm)
ui.on_message("update_alarm", on_update_alarm)
ui.on_message("delete_alarm", on_delete_alarm)
ui.on_message("toggle_alarm", on_toggle_alarm)

print("[Alarms] Starting alarm app with loop-based checker")

# Start the application with our loop function
App.run(user_loop=loop)

