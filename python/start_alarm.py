from playsound3 import playsound
from check_in_frame import camera_loop
from multiprocessing import Process

def sound_loop(sound_file='sounds/alarm.m4a'):
    while True:
        playsound(sound_file)  # Replace with the path to your alarm sound file


def start_alarm():
    print("Starting Alarm loop...")
    alarm_sound = Process(target=sound_loop)
    alarm_sound.start()
    camera_loop()
    alarm_sound.terminate()
    print("Alarm loop ended...")