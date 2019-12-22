import smbus
import time
 
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1
  
DEVICE = 0x20 # Device address (A0-A2)
IODIRA = 0x00 # Pin direction register for Bank A
IODIRB = 0x01 # Pin direction register for Bank B
OLATA  = 0x14 # Output, Bank A
OLATB  = 0x15 # Output, Bank B
SETTLEDELAY = .0001
   
# Set all GPA pins as outputs by setting
# all bits of IODIRA and IODIRB register to 0
bus.write_byte_data(DEVICE, IODIRA, 0x00)
bus.write_byte_data(DEVICE, IODIRB, 0x00)
    
# Initialize all outputs to 0
bus.write_byte_data(DEVICE, OLATA, 0x00)
bus.write_byte_data(DEVICE, OLATB, 0x00)

print("Test MCP23017 Bank A")
for test in range(1,8):
    bus.write_byte_data(DEVICE, OLATA, test)
    val = bus.read_byte_data(DEVICE, OLATA)
    if test != val:
        print("failed bank A for test value {0:03b}".format(test))
    print("{0:03b}".format(val))

print("Test MCP23017 Bank B")
for test in range(1,8):
    bus.write_byte_data(DEVICE, OLATB, test)
    val = bus.read_byte_data(DEVICE, OLATB)
    if test != val:
        print("failed bank A for test value {0:03b}".format(test))
    print("{0:03b}".format(val))

print("{0:016b}".format(0x38))
print("{0:016b}".format(0x06))
print("{0:016b}".format(0x0E))
print("{0:016b}".format(0x01))


# Electrical connections from MCP23017 to Display
#
# IO    Display
# ==    ===========================================================
# A0    Pin 4   RS, 0=Command, 1=Data
# A1    Pin 5   R/W, 1=Read, 0=Write
# A2    Pin 6   Enable, Normally low, set to high to perform action
# A3    Pin 7   DB0
# A4    Pin 8   DB1
# A5    Pin 9   DB2
# A6    Pin 10  DB3
# A7    Pin 11  DB4
# B0    Pin 12  DB5
# B1    Pin 13  DB6
# B2    Pin 14  DB7

# list of command values
displayMode = 0x38 # 8 bit interface, 2 display lines, 5x7 font
entryMode = 0x06 # increment automatically, no dislpay shift
displayControl = 0x0E # turn display on, cursor on, no blinking
clearDisplay = 0x01 # clear the display


# Function to send a command to the display
def SendDisplayCommand(command):
    # Set command value in bank A
    bus.write_byte_data(DEVICE, OLATA, command)

    # Enable the command in bank B to write a command
    writeCommand = 0b100
    bus.write_byte_data(DEVICE, OLATB, writeCommand)

    # Give the display time to latch everything
    time.sleep(SETTLEDELAY)

    # Complete the command by lowerig the Enable line
    writeCommand = 0x00
    bus.write_byte_data(DEVICE, OLATB, writeCommand)

    time.sleep(SETTLEDELAY)
    print("done sending command")

#Function to send data to the display
def SendDisplayData(data):
    # Set data value in bank A
    bus.write_byte_data(DEVICE, OLATA, data)

    #Enable the command in bank B to write data
    writeCommand = 0b101
    bus.write_byte_data(DEVICE, OLATB, writeCommand)

    # Give the display time to latch everything
    time.sleep(SETTLEDELAY)

    # Complete the command by lowerig the Enable line
    writeCommand = 0x00
    bus.write_byte_data(DEVICE, OLATB, writeCommand)

    time.sleep(SETTLEDELAY)
    
    print("done sending data")

def SendDisplayString(message):
    for c in message:
        SendDisplayData(ord(c))
        
SendDisplayCommand(displayMode)
SendDisplayCommand(entryMode)
SendDisplayCommand(displayControl)
SendDisplayCommand(clearDisplay)

#SendDisplayData(ord('h'))
#SendDisplayData(ord('e'))
#SendDisplayData(ord('l'))
#SendDisplayData(ord('l'))
#SendDisplayData(ord('o'))
#SendDisplayData(ord(' '))
#SendDisplayData(ord('w'))
#SendDisplayData(ord('o'))
#SendDisplayData(ord('r'))
#SendDisplayData(ord('l'))
#SendDisplayData(ord('d'))
while True:
    SendDisplayString('It rains in Seattle\n')
    SendDisplayString('It rains in Seattle')
    time.sleep(1)
    SendDisplayCommand(clearDisplay)

