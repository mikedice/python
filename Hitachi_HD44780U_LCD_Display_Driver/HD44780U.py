# This is a driver for the HD44780U that doesn't use automatic
# address incrementing. Trying to get all four display lines to work

import smbus
import time
 
### Setting up of the MCP23017 I2C Port Expander
### The port expander is used to communicate with the
### Display
bus = smbus.SMBus(1) # Rev 2 Pi uses 1
  
DEVICE = 0x20 # Device address (A0-A2)
IODIRA = 0x00 # Pin direction register for Bank A
IODIRB = 0x01 # Pin direction register for Bank B
OLATA  = 0x14 # Output, Bank A
OLATB  = 0x15 # Output, Bank B
SETTLEDELAY = .0001

LogEnabled = False

def log(message):
    if LogEnabled == True:
        print(message)
        
# Set all GPA pins as outputs by setting
# all bits of IODIRA and IODIRB register to 0
bus.write_byte_data(DEVICE, IODIRA, 0x00)
bus.write_byte_data(DEVICE, IODIRB, 0x00)
    
# Initialize all outputs to 0
bus.write_byte_data(DEVICE, OLATA, 0x00)
bus.write_byte_data(DEVICE, OLATB, 0x00)

log("Test MCP23017 Bank A")
for test in range(1,8):
    bus.write_byte_data(DEVICE, OLATA, test)
    val = bus.read_byte_data(DEVICE, OLATA)
    if test != val:
        log("failed bank A for test value {0:03b}".format(test))
    log("{0:03b}".format(val))

log("Test MCP23017 Bank B")
for test in range(1,8):
    bus.write_byte_data(DEVICE, OLATB, test)
    val = bus.read_byte_data(DEVICE, OLATB)
    if test != val:
        log("failed bank A for test value {0:03b}".format(test))
    log("{0:03b}".format(val))

log("{0:016b}".format(0x38))
log("{0:016b}".format(0x06))
log("{0:016b}".format(0x0E))
log("{0:016b}".format(0x01))

### Driving of the display using the I2C Port expander
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
DISPLAY_MODE = 0x38 # 8 bit interface, 2 display lines, 5x7 font
ENTRY_MODE = 0x06 # increment automatically, no dislpay shift
DISPLAY_CONTROL = 0x0E # turn display on, cursor on, no blinking
CLEAR_DISPLAY = 0x01 # clear the display

DDRAM_LINE_1 = 0X00
DDRAM_LINE_2 = 0X40
DDRAM_LINE_3 = 0X14
DDRAM_LINE_4 = 0X54
SHIFT_DISPLAY_LEFT = 0b00011000


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
    log("done sending command")

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
    
    log("done sending data")

def SendDisplayString(message):
    for c in message:
        SendDisplayData(ord(c))

def InitializeDisplay():
    SendDisplayCommand(DISPLAY_MODE)
    SendDisplayCommand(ENTRY_MODE)
    SendDisplayCommand(DISPLAY_CONTROL)
    SendDisplayCommand(CLEAR_DISPLAY)

def CursorOff():
    SendDisplayCommand(0x08) # display off
    SendDisplayCommand(0x0C) # display on, cursor off, cursor blink off

def WriteLine1(value):
    WriteLine(DDRAM_LINE_1, value)

def WriteLine2(value):
    WriteLine(DDRAM_LINE_2, value)

def WriteLine3(value):
    WriteLine(DDRAM_LINE_3, value)

def WriteLine4(value):
    WriteLine(DDRAM_LINE_4, value)

def WriteLine(lineno, value):
    length = 20 if len(value) > 20 else len(value)
    spacefill = 0 if length >= 20 else 20-length
    SendDisplayCommand(lineno| 0b10000000)
    for i in range(length):
        SendDisplayData(ord(value[i]))

    if spacefill > 0:
        for i in range(spacefill):
            SendDisplayData(ord(' '))
            
def DisplayTest():
    SendDisplayCommand(DDRAM_LINE_1 | 0b10000000)
    SendDisplayData(ord('1'))
    SendDisplayData(ord('a'))

    SendDisplayCommand(DDRAM_LINE_2 | 0b10000000)
    SendDisplayData(ord('2'))
    SendDisplayData(ord('b'))

    SendDisplayCommand(DDRAM_LINE_3 | 0b10000000)
    SendDisplayData(ord('3'))
    SendDisplayData(ord('c'))

    SendDisplayCommand(DDRAM_LINE_4 | 0b10000000)
    SendDisplayData(ord('4'))
    SendDisplayData(ord('d'))

    SendDisplayCommand(DDRAM_LINE_1 | 0b10000000)
    for c in range (ord('a'), ord('a')+20):
        SendDisplayData(c)

    SendDisplayCommand(DDRAM_LINE_2 | 0b10000000)
    for c in range (ord('A'), ord('A')+20):
        SendDisplayData(c)

    SendDisplayCommand(DDRAM_LINE_3 | 0b10000000)
    for c in range (ord('0'), ord('0')+20):
        SendDisplayData(c)

    SendDisplayCommand(DDRAM_LINE_4 | 0b10000000)
    for c in range (0b00100000, 0b00100000 + 0x14):
        SendDisplayData(c)

    while True:
        SendDisplayCommand(SHIFT_DISPLAY_LEFT)
        time.sleep(.5)


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
    #SendDisplayString('It rains in Seattle')
    #SendDisplayString('It rains in Seattle')
        
if __name__ == "__main__":

    InitializeDisplay()
    DisplayTest();
    
