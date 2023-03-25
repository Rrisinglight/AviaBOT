import bd
import RPi.GPIO as GPIO
import time
from time import sleep
import serial

def door(q):
    
    while True:
        try:
            PortRF = serial.Serial('/dev/ttyS0', 9600)
            ID = ""
            read_byte = (PortRF.read())

            for Counter in range(12):
                read_byte = (PortRF.read()).decode("utf-8")
                ID = ID + str(read_byte)

            q.put(ID)

            if bd.if_approved(ID) == True:
                action_open()
                door_open()
                print("door open")
            else:
                action_error()
                print("Нет доступа")

            PortRF.close()
            time.sleep(2)
        except Exception:
            next

def door_open():
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    
    try:
        GPIO.output(18, GPIO.LOW)
        time.sleep(5)
        GPIO.output(18, GPIO.HIGH)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        GPIO.cleanup()

def terminated_door():
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    
    try:
        GPIO.output(18, GPIO.LOW)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        GPIO.cleanup()

def buzz(noteFreq, duration):
    halveWaveTime = 1 / (noteFreq * 2 )
    waves = int(duration * noteFreq)
    for i in range(waves):
       GPIO.output(BUZZER, True)
       time.sleep(halveWaveTime)
       GPIO.output(BUZZER, False)
       time.sleep(halveWaveTime)

def play(tones, melody, duration):
    t=0
    for i in melody:
        buzz(tones[i], duration[t])
        time.sleep(duration[t] *0.1)
        t+=1

def action_open():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GREEN, GPIO.OUT, initial=GPIO.LOW)
    
    GPIO.output(GREEN, GPIO.HIGH)
    play(tones, open_dour, open_dour_d)
    sleep(0.4)
    GPIO.output(GREEN, GPIO.LOW)
    GPIO.cleanup()
	
def action_close():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GREEN, GPIO.OUT, initial=GPIO.LOW)
    
    GPIO.output(RED, GPIO.HIGH)
    play(tones, close_dour, close_d)
    GPIO.output(RED, GPIO.LOW)
    sleep(0.2)
    GPIO.output(RED, GPIO.HIGH)
    sleep(0.2)
    GPIO.output(RED, GPIO.LOW)
    sleep(0.2)
    GPIO.output(RED, GPIO.HIGH)
    sleep(0.2)
    GPIO.output(RED, GPIO.LOW)
    GPIO.cleanup()

def action_error():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GREEN, GPIO.OUT, initial=GPIO.LOW)
    
    GPIO.output(RED, GPIO.HIGH)
    sleep(0.2)
    GPIO.output(RED, GPIO.LOW)
    play(tones, error_code, error_d)
    GPIO.output(RED, GPIO.HIGH)
    sleep(0.2)
    GPIO.output(RED, GPIO.LOW)
    GPIO.cleanup()
	
BUZZER = 26
GREEN = 13
RED = 19

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
        
#play(tones, open_dour, open_dour_d)
#play(tones, error_code, error_d)
