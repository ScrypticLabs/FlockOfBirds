# Flock of Birds (Ascension Technology Corporation)
# Code by Paul Gribble
# December 2012
# note you may have to run this as the su

def dataconvert(data):
    """
    converts 12-bytes of data read from the serial port
    into x,y,z,roll,pitch,yaw (mm,mm,mm,deg,deg,deg)
    for a single bird
    """
    xLS,xMS = data[0], data[1]
    yLS,yMS = data[2], data[3]
    zLS,zMS = data[4], data[5]
    yawLS,yawMS = data[6], data[7]
    pitchLS,pitchMS = data[8], data[9]
    rollLS,rollMS = data[10], data[11]
    #
    xLS = ord(xLS)-128 # change leading bit to zero
    xLS = xLS<<1 # shift bits left
    x = ((    xLS  + (ord(xMS) * 256))<<1)
    y = (((ord(yLS)<<1) + (ord(yMS) * 256))<<1)
    z = (((ord(zLS)<<1) + (ord(zMS) * 256))<<1)
    yaw = (((ord(yawLS)<<1) + (ord(yawMS) * 256))<<1)
    pitch = (((ord(pitchLS)<<1) + (ord(pitchMS) * 256))<<1)
    roll = (((ord(rollLS)<<1) + (ord(rollMS) * 256))<<1)
    if x>32767: x-=65536
    if y>32767: y-=65536
    if z>32767: z-=65536
    if yaw>32767: yaw-=65536
    if pitch>32767: pitch-=65536
    if roll>32767: roll-=65536
    # convert to mm and deg
    x = x * 36.0 * 25.4 / 32768.0
    y = y * 36.0 * 25.4 / 32768.0
    z = z * 36.0 * 25.4 / 32768.0
    yaw = yaw * 180.0 / 32768.0
    pitch = pitch * 180.0 / 32768.0
    roll = roll * 180.0 / 32768.0
    return x,y,z,roll,pitch,yaw

import serial
import time
import struct

# open the serial port
# (I am using a Belkin F5U109 Serial RS-232 to USB adapter)
ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 115200
ser.open()

# toggle RTS (hello bird)
ser.setRTS(True)
ser.setRTS(False)

# read any junk that might be waiting for us
n = ser.inWaiting()
if n>0:
    dum = ser.read(n)

# tell bird we want it to send us 12-byte position/angle data
ser.write('Y') # send POSITION / ANGLES command
time.sleep(3)

# open a data file
fid = open("datafile.txt","w")

# sampling rate and recording length
samprate = 100.0 # Hz
samptime = 10.0 # seconds

# loop to record data
t0 = time.time()
tp = time.time()
while time.time()-t0 < samptime:
    ti = time.time()
    if ti-tp >= (1.0/samprate):
        tp = time.time()
        ser.write('B')
        while ser.inWaiting() < 12:
            continue
        data = ser.read(12)
        x,y,z,roll,pitch,yaw = dataconvert(data)
        print "%8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f" % (tp-t0,x,y,z,roll,pitch,yaw)
        fid.write("%8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f\n" % (tp-t0,x,y,z,roll,pitch,yaw))
fid.close()

# goodbye bird
ser.setRTS(True)

# close the serial port
ser.close()

