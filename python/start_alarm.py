# from playsound3 import playsound
import os
from check_in_frame import camera_loop
from multiprocessing import Process, Event
import pygame
import time

def sound_loop(stop_event, sound_file='assets/sounds/alarm.mp3'):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)

    pygame.mixer.music.play(-1)
    while not stop_event.is_set():
        time.sleep(0.2)

    pygame.mixer.music.stop()
    pygame.mixer.quit()


def start_alarm():
    print("Starting Alarm loop...")
    stop_event = Event()
    alarm_sound = Process(target=sound_loop, args=(stop_event,))
    alarm_sound.start()
    camera_loop()
    stop_event.set()
    alarm_sound.join()
    print("Alarm loop ended...")
    return True