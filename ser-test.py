import serial
import sys


# line is a comma seperated string with two integer fields
def readValues(serialPort):
    line = serialPort.readline()
    dec = line.decode('utf-8')
    stringvals =  dec.replace('\n','').split(',')
    
    # We may sometimes get a partial line, like when the program first
    # opens the serial port. If this happens we can just return and
    # ignore that line
    if len(stringvals) != 3:
        return('',0,0)

    # Return a tuple that contains our fields
    return (stringvals[0], int(stringvals[1]), int(stringvals[2]))

# Open the serial port. You can specify the port's
# operating system path using the first arguemnt to the script.
# or a default will be used.
def openSerialPort():
    portPath = '/dev/ttyACM1'
    if len(sys.argv) > 1:
        portPath = sys.argv[1]
    serialPort = serial.Serial(portPath)
    return serialPort

# Start by opening the serial port
serialPort = openSerialPort()

# Now just run the game loop
while True:
    vals = readValues(serialPort)
    print('{},{:d},{:d}'.format(vals[0], vals[1], vals[2]))


