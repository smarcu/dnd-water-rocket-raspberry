#!/usr/bin/python

import sys
import time
import subprocess
from multiprocessing import Process
from datetime import datetime
import os.path
sys.path.insert(1, 'pressure')
sys.path.insert(2, 'accel')
sys.path.insert(3, 'motor')
from accel import ADXL345
from motor import MoveMotor
from Adafruit_BMP085 import BMP085


# ======== PRESSURE SENSOR 
# Initialize the BMP085 and use STANDARD mode (default value)
# bmp = BMP085(0x77, debug=True)
bmp = BMP085(0x77)
# To specify a different operating mode, uncomment one of the following:
# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = BMP085(0x77, 1)  # STANDARD Mode
bmp = BMP085(0x77, 2)  # HIRES Mode
# bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

# ======== ACC SENSOR 
adxl345 = ADXL345();

# threshold to trigger the parachute
ACCELERATION_MIN_THRESHOLD = 0.4;

def uniqueFile(name, extension):
	while True:
		timestamp = time.strftime("%Y%m%d-%H%M%S");
		uniqueName = name + "-" + timestamp + "." + extension;
		if (os.path.exists(uniqueName)):
			time.sleep(1);
		else:
			return uniqueName;

def startVideo():
	videoFileName  = uniqueFile('video/rocket' , "h264");
	print "Video started! ", videoFileName;
	subprocess.call(["raspivid", "-o", videoFileName, "-t", "0", "-vf", "-w", "640", "-h", "480", "-fps", "25", "-b", "1200000", "-n"]);

videoRecordingProcess = Process(target = startVideo);

def startVideoProcess():
	print "Start video recording process...";
	videoRecordingProcess.start();


#=============== START MAIN 

try:
	logfilename = uniqueFile("logs/rocket", "log");
	log = open(logfilename, "a");
	print ("Start log %s" %logfilename);

# no video yet
#	startVideoProcess();

	# previous reading
	lastAltitude = -1000;
	# max altitude reached during this session
	maxAltitude = 0;

	
	while True:
		datetime = datetime.now()

		# pressure, altitude, temp
		temperature = bmp.readTemperature();
		pressure = bmp.readPressure();
		altitude = bmp.readAltitude();
		if (maxAltitude < altitude):
                        maxAltitude = altitude;
                if (altitude == -1000):
                        lastAltitude = altitude;
                diffAltitude = altitude - lastAltitude;
                diffToMaxAltitude = maxAltitude - altitude;

		# acceleration
		axes = adxl345.getAxes(True);
		accelerationTotal = abs(axes['x']) + abs(axes['y']) + abs(axes['z']);


		print "%s  T %.2fC  P %.2f hPa  X %.3fG  Y %.3fG  Z %.3fG  XYZ %.3f  ALT  %.2f  DIFF %.2f  MAX %.2f  DIFMAX %.2f" % (datetime, temperature, (pressure / 100.0), \
			axes['x'], axes['y'], axes['z'], accelerationTotal, altitude, diffAltitude, maxAltitude, diffToMaxAltitude);
		log.write("%s, %.2f, %.2f, %.3f, %.3f, %.3f, %.3f, %.2f, %.2f, %.2f, %.2f, \n" \
			% (datetime, temperature, (pressure / 100.0), \
			axes['x'], axes['y'], axes['z'], accelerationTotal,\
			altitude, diffAltitude, maxAltitude, diffToMaxAltitude));

		if (0 < accelerationTotal < ACCELERATION_MIN_THRESHOLD):
                        print "DESCENT DETECTED\n"
                        log.write("DESCENT DETECTED\n")
                        MoveMotor();
                        parachuteDeployed = True;

                lastAltitude = altitude;

		# take a short nap
		time.sleep(0.5);
except Exception as e: 
	print(e)
finally:
	print "rocket: cleanup file"
	log.close()
#	videoRecordingProcess.terminate()


