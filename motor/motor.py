import RPi.GPIO as GPIO
import time

servoPIN = 17;

def MoveMotor():
	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(servoPIN, GPIO.OUT)
		p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
		p.start(8.5) # Initialization
		p.ChangeDutyCycle(2.5)
		time.sleep(1)
		p.ChangeDutyCycle(8.5)
		time.sleep(1)

	finally:
		print "motor: cleanup gpio"
		p.stop()
		GPIO.cleanup()
