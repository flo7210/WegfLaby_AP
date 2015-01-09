import serial;
import time;

ser = serial.Serial(0)

for i in range(5):
    time.sleep(0.5)
    print(ser.read(2))

ser.close()