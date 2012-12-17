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

# open the serial ports
print "OPENING SERIAL PORTS"
ser = [serial.Serial() for s in range(4)]
for i in range(4):
    print "PORT %d" % (i)
    ser[i].port = "/dev/ttyUSB%d" % (i)
    ser[i].baudrate = 115200
    ser[i].open()
    time.sleep(0.5)
    ser[i].setRTS(True)
    time.sleep(0.5)
    ser[i].setRTS(False) # hello bird
    time.sleep(0.5)
    n = ser[i].inWaiting()
    if n>0: dum = ser[i].read(n)
    time.sleep(0.5)

# auto-configure flock
print "AUTO-CONFIGURE FLOCK"
time.sleep(1)
ser[0].write('P')
ser[0].write(chr(50))
ser[0].write(chr(4))
time.sleep(1)

# tell bird we want it to send us 12-byte position/angle data
print "WANT POSITION/ANGLE DATA"
for i in range(4):
    print "PORT %d" % (i)
    time.sleep(1)
    ser[i].write('Y') # send POSITION / ANGLES command

time.sleep(1)

# open a data file
print "OPENING DATA FILE"
fid = open("datafile.txt","w")

# sampling rate and recording length
samprate = 100.0 # Hz
samptime = 20.0 # seconds

# loop to record data
t0 = time.time()
tp = time.time()
while time.time()-t0 < samptime:
    ti = time.time()
    if ti-i0 >= (1.0/samprate):
        ti0 = time.time()
        for i in range(4):
            tp = time.time()
            ser[i].write('B')
            while ser[i].inWaiting() < 12:
                continue
            data = ser[i].read(12)
            x,y,z,roll,pitch,yaw = dataconvert(data)
            print "%d %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f" % (i,tp-t0,x,y,z,roll,pitch,yaw)
            fid.write("%d %8.4f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f\n" % (i,tp-t0,x,y,z,roll,pitch,yaw))
fid.close()
print "DATA FILE CLOSED"

# goodbye bird
print "GOODBYE BIRDS"
for i in range(4):
    ser[i].setRTS(True)
    time.sleep(0.5)
    ser[i].close()

