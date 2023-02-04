import bd
import time
import serial
import RPi.GPIO as GPIO

def door(q):   
    while True:
        PortRF = serial.Serial('/dev/ttyS0', 9600)
        ID = ""
        read_byte = (PortRF.read())

        for Counter in range(12):
            read_byte = (PortRF.read()).decode("utf-8")
            ID = ID + str(read_byte)
            
        q.put(ID)
                
        if bd.in_table(ID) == True:
            door_open()
            print("door open")
        else:
            print("Нет доступа")
        
        PortRF.close()
        time.sleep(2)
            
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