# A simple clock app to test the display driver

import sys
from datetime import datetime
import time
sys.path.append('./Hitachi_HD44780U_LCD_Display_Driver')
import HD44780U as display

# initialize the display
display.InitializeDisplay()
display.CursorOff()

print('clock is running...')
while True:
    local = datetime.now()
    display.WriteLine1(local.strftime("%B %-m, %Y"))
    display.WriteLine2(local.strftime("%-I:%M:%S %p"))
    time.sleep(.25)

