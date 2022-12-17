import time
import serial
import bd

def polling():
    
    try:
        while bd.kostyl_status() == True:

            print('Scan Your Card')
            # PortRF = serial.Serial('/dev/ttyS0', 9600)

            # ID = ""
            # read_byte = (PortRF.read())

            # for Counter in range(12):
            #     read_byte = (PortRF.read()).decode("utf-8")
            #     ID = ID + read_byte
            # print(ID)
            # PortRF.close()
            ID = '9308475982'

            # if bd.in_table(ID) == True:
            #     print('Open')
            # else:
            #     print('Close')

            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped")

def new_card():
    try:
        for i in range(30):
            ID = '349857394'
            # PortRF = serial.Serial('/dev/ttyS0', 9600)

            # ID = ""
            # read_byte = (PortRF.read())

            # for Counter in range(12):
            #     read_byte = (PortRF.read()).decode("utf-8")
            #     ID = ID + read_byte
            # PortRF.close()
            print('working')
            time.sleep(1)
            return(ID)      

    except BaseException:
        return("Ошибка")