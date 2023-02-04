import bd
import time
import serial
import RPi.GPIO as GPIO

new_user = False

def door_new_user():
    PortRF = serial.Serial('/dev/ttyS0', 9600)
                
    new_ID = ""

    read_byte = (PortRF.read())

    for Counter in range(12):
        read_byte = (PortRF.read()).decode("utf-8")
        new_ID += read_byte

    PortRF.close()
    return(new_ID)

def door():

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(23, GPIO.OUT)

    GPIO.output(23, GPIO.HIGH)

    def open_door():
        GPIO.output(23, GPIO.LOW)
        time.sleep(5)
        GPIO.output(23, GPIO.HIGHT)
        return()


    try:
        while True:
            if new_user == False:
                PortRF = serial.Serial('/dev/ttyS0', 9600)

                ID = ""

                read_byte = (PortRF.read())

                for Counter in range(12):
                    read_byte = (PortRF.read()).decode("utf-8")
                    ID += read_byte

                if bd.in_table(ID) == True:
                    open_door()
                else:
                    print("Нет доступа")

                PortRF.close()
                time.sleep(0.5)
            else:
                time.sleep(2)

    except KeyboardInterrupt:
        print("Stopped")
    finally:
        GPIO.cleanup()
