# from playsound3 import playsound
import os
from check_in_frame import camera_loop
from multiprocessing import Process

def sound_loop(sound_file='sounds/alarm.m4a'):
    os.system(f"mpg123 {sound_file}")


def start_alarm():
    print("Starting Alarm loop...")
    alarm_sound = Process(target=sound_loop)
    alarm_sound.start()
    camera_loop()
    alarm_sound.terminate()
    print("Alarm loop ended...")
    return True