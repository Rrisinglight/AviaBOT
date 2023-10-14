#!/usr/bin/python3
import bd
import RPi.GPIO as GPIO
from time import sleep
import serial
from threading import Thread

def door_open():
    GPIO.output(16, GPIO.LOW)
    action_open()
    sleep(2)
    GPIO.output(16, GPIO.HIGH)

def buzz(noteFreq, duration):
    halveWaveTime = 1 / (noteFreq * 2 )
    waves = int(duration * noteFreq)
    for i in range(waves):
       GPIO.output(BUZZER, True)
       sleep(halveWaveTime)
       GPIO.output(BUZZER, False)
       sleep(halveWaveTime)

def play(tones, melody, duration, COLOR):
    t=0
    TOGGLE = GPIO.HIGH
    GPIO.output(COLOR, TOGGLE)
    for i in melody:
        buzz(tones[i], duration[t])
        sleep(duration[t] *0.1)
        if TOGGLE == GPIO.HIGH: TOGGLE = GPIO.LOW
        else: TOGGLE = GPIO.HIGH
        GPIO.output(COLOR, TOGGLE)
        t+=1

def action_open():
    play(tones, open_dour, open_dour_d, GREEN)
    GPIO.output(GREEN, GPIO.HIGH)
    sleep(0.4)
    GPIO.output(GREEN, GPIO.LOW)
	
def action_close():
    play(tones, close_dour, close_d, RED)
    GPIO.output(RED, GPIO.HIGH)
    sleep(0.15)
    GPIO.output(RED, GPIO.LOW)

def action_error():
    play(tones, error_code, error_d, RED)
    GPIO.output(RED, GPIO.HIGH)
    sleep(0.1)
    GPIO.output(RED, GPIO.LOW)

def action_blink():
    while True:
        if signal == False:
            play(tones, blink_code, blink_d, GREEN)
            GPIO.output(GREEN, GPIO.LOW)
            GPIO.output(RED, GPIO.HIGH)
            sleep(0.15)
            GPIO.output(RED, GPIO.LOW)
        sleep(16)

def action_key():
    GPIO.output(RED, GPIO.HIGH)
    GPIO.output(GREEN, GPIO.LOW)
    buzz(1109, 0.2)
    sleep(0.8)
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(GREEN, GPIO.HIGH)
    buzz(78, 0.2)
    sleep(0.9)
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(GREEN, GPIO.LOW)

def door(q):
    while True:
        try:
            PortRF = serial.Serial('/dev/ttyS0', 9600)
            ID = ""
            read_byte = PortRF.read()

            for Counter in range(12):
                read_byte = (PortRF.read()).decode("utf-8")
                ID = ID + str(read_byte)

            q.put(ID)

            if signal == False:
                if bd.if_approved(ID) == True:
                    user = bd.check_id(ID)
                    bd.insert_info(user[0], user[1], 'Дверь открыта ключом')
                    door_open()
                else:
                    bd.insert_small_info(f'Неизвестный ключ: {ID}')
                    action_error()


            PortRF.close()
        except Exception:
            next

def push_button():
    while True:
        if GPIO.input(21) == GPIO.HIGH:
            door_open()
            bd.insert_small_info('Дверь открыта кнопкой')
        sleep(0.5)

BUZZER = 26
GREEN = 19
RED = 13

global signal
signal = False

tones = {
    "B0": 31, "C1": 33, "CS1": 35, "D1": 37, "DS1": 39, "E1": 41, "F1": 
    44, "FS1": 46, "G1": 49, "GS1": 52, "A1": 55, "AS1": 58, "B1": 62, 
    "C2": 65, "CS2": 69, "D2": 73, "DS2": 78, "E2": 82, "F2": 87, 
    "FS2": 93, "G2": 98, "GS2": 104, "A2": 110, "AS2": 117, "B2": 123, 
    "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175, 
    "FS3": 185, "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 
    247, "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 
    349, "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, 
    "B4": 494, "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, 
    "F5": 698, "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 
    932, "B5": 988, "C6": 1047, "CS6": 1109, "D6": 1175, "DS6": 1245, 
    "E6": 1319, "F6": 1397, "FS6": 1480, "G6": 1568, "GS6": 1661, "A6": 
    1760, "AS6": 1865, "B6": 1976, "C7": 2093, "CS7": 2217, "D7": 2349, 
    "DS7": 2489, "E7": 2637, "F7": 2794, "FS7": 2960, "G7": 3136, 
    "GS7": 3322, "A7": 3520, "AS7": 3729, "B7": 3951, "C8": 4186, 
    "CS8": 4435, "D8": 4699, "DS8": 4978, "REST": 0
}

open_dour = ["D5", "E5", "C6"]
open_dour_d = [0.4, 0.2, 0.2]

error_code = ["D3", "A4", "B0", "D2"]
error_d = [0.4, 0.2, 0.3, 0.3]

close_dour = ["C4", "C4", "C4", "C4"]
close_d = [0.4, 0.4, 0.4, 0.5]

blink_code = ["E6", "F6", "E6"]
blink_d = [0.1, 0.1, 0.1]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(21, GPIO.IN)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(19, GPIO.OUT, initial=GPIO.LOW)
        
# action_open()
# action_close()
# action_error()

    
