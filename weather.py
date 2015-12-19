import smbus
import time
import ctypes
bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x77
BMP180_REG_CONTROL = 0xF4
BMP180_REG_RESULT = 0xF6
BMP180_COMMAND_TEMPERATURE = 0x2E
BMP180_COMMAND_PRESSURE = 0x34
BMP180_PRESSURE_OVERSAMPLE0 = 0
BMP180_PRESSURE_OVERSAMPLE1 = 1
BMP180_PRESSURE_OVERSAMPLE2 = 2
BMP180_PRESSURE_OVERSAMPLE3 = 3

def readword(address):
	byte1 = bus.read_byte_data(DEVICE_ADDRESS, address)
	byte2 = bus.read_byte_data(DEVICE_ADDRESS, address+1)
	return ((byte1 << 8)|byte2)

calAC1 = ctypes.c_int16(readword(0xAA))
calAC2 = ctypes.c_int16(readword(0xAC))
calAC3 = ctypes.c_int16(readword(0xAE))
calAC4 = ctypes.c_uint16(readword(0xB0))
calAC5 = ctypes.c_uint16(readword(0xB2))
calAC6 = ctypes.c_uint16(readword(0xB4))
calVB1 = ctypes.c_int16(readword(0xB6))
calVB2 = ctypes.c_int16(readword(0xB8))
calMB =  ctypes.c_int16(readword(0xBA))
calMC =  ctypes.c_int16(readword(0xBC))
calMD =  ctypes.c_int16(readword(0xBE))

def readRawTemp():
	bus.write_byte_data(DEVICE_ADDRESS, 
		BMP180_REG_CONTROL, 
		BMP180_COMMAND_TEMPERATURE)
	time.sleep(.010)

	AC6 = calAC6.value
	AC5 = calAC5.value
	MC = calMC.value
        MD = calMD.value

        UT = readword(BMP180_REG_RESULT)
	X1 = ((UT - AC6) * AC5) >> 15
	X2 = (MC << 11) / (X1 + MD)
	B5 = X1 + X2
	T = (B5 + 8) / 16.0
        # temp is returned in .1 degree C
	return T

def readRawPressure():
        OSS = BMP180_PRESSURE_OVERSAMPLE0

	bus.write_byte_data(DEVICE_ADDRESS, 
		BMP180_REG_CONTROL, 
                BMP180_COMMAND_PRESSURE + (OSS<<6))
	time.sleep(.014)

	msb = bus.read_byte_data(DEVICE_ADDRESS, BMP180_REG_RESULT)
	lsb = bus.read_byte_data(DEVICE_ADDRESS, BMP180_REG_RESULT+1)
	xlsb = bus.read_byte_data(DEVICE_ADDRESS, BMP180_REG_RESULT+2)
	raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8-OSS)
	return raw

def calculateTruePressure(UP, UT, OSS):
        '''	
	AC1 = 408
	AC2 = -72
	AC3 = -14383
        AC4 = 32741
	AC6 = 23153
	AC5 = 32757
	MC = -8711
        MD = 2868
        B1 = 6190
        B2 = 4
        UT = 27898
        UP = 23843
        OSS = 0
        '''
	AC1 = calAC1.value
	AC2 = calAC2.value
	AC3 = calAC3.value
        AC4 = calAC4.value
	AC6 = calAC6.value
	AC5 = calAC5.value
	MC = calMC.value
        MD = calMD.value
        B1 = calVB1.value
        B2 = calVB2.value

	X1 = ((long(UT) - AC6) * AC5) >> 15
	X2 = (MC << 11) / (X1 + MD)
	B5 = X1 + X2
	B6 = B5-4000
 	#print B6
	X1 = (B2 * (B6 * B6 >> 12))>>11
        #print X1
        X2 = AC2 * B6 >> 11
 	#print X2
	X3 = X1 + X2
	#print X3
	B3 = (((AC1*4 + X3)<<OSS)+2)/4
        #print B3
        X1 = AC3 * B6 >> 13
        #print X1
        X2 = (B1 * (B6 * B6 >> 12)) >> 16
        #print X2
        X3 = ((X1 + X2) + 2) >> 2
        #print X3
        B4 = AC4 * (X3 + 32768) >> 15
        #print B4
        B7 = (UP - B3) * (50000>>OSS)
        #print B7
        p = 0
	if B7 < 0x80000000 :
          p = (B7*2) / B4
        else : 
          p = (B7 / B4)*2
        #print p
	X1 = (p >> 8) * (p >> 8)
        #print X1
        X1 = (X1 * 3038) >> 16
        #print X1
        X2 = (-7357 * p) >> 16
        #print X2
        P  = p + ((X1 + X2 + 3791)>>4)
        #print P
        return P


UT = readRawTemp()
print UT * .1
print ((UT*.1) * 1.8) + 32

UP = readRawPressure()
print UP
pt = calculateTruePressure(UP, UT, BMP180_PRESSURE_OVERSAMPLE0)
print pt
