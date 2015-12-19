import Adafruit_BMP.BMP085 as BMP085
import json
import os

bmp = BMP085.BMP085()
graphDataFile = "/home/pi/code/data/weather.json"

temp = bmp.read_temperature()
pressure = bmp.read_pressure()

result = {}
result["PressureMb"]=pressure/100.00
result["Pressure"]=pressure * 1.0
result["TempC"]=temp
result["TempF"]=(temp * 9)/5 + 32

with open(graphDataFile, 'w') as fileObj:
	json.dump(result, fileObj)

# run the view model builder
os.system("python3 makeBarometerViewModel.py")
