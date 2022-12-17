import time
import serial
import RPi.GPIO as GPIO

table = []

def in_table(id):
    if id in table:
        return(True)
    else:
        return(False)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)

GPIO.output(23,GPIO.HIGH)

def open_door():
    GPIO.output(23,GPIO.LOW)
    time.sleep(30)

try:
    while True:
        print('Scan Your Card')
        PortRF = serial.Serial('/dev/ttyS0', 9600)

        ID = ""
        read_byte = (PortRF.read())

        for Counter in range(12):
            read_byte = (PortRF.read()).decode("utf-8")
            ID = ID + read_byte
            if not in_table():
                table.append(ID)

        PortRF.close()
        if in_table(ID) == True:
            print('Open')
            open_door()
            
        else:
            print('Close')

except KeyboardInterrupt:
    print("Stopped")
finally:
    GPIO.cleanup()