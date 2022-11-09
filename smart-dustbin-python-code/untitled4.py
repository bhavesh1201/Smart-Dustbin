import RPi.GPIO as GPIO
import time

servoPIN = 17
TRIG = 18
ECHO = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)



p = GPIO.PWM(servoPIN, 50) 
p.start(2.5) 

GPIO.output(TRIG, False)
print ("Calibrating.....")
time.sleep(2)


try:
    while True:
       GPIO.output(TRIG, True)
       time.sleep(0.00001)
       GPIO.output(TRIG, False)

       while GPIO.input(ECHO)==0:
          pulse_start = time.time()

       while GPIO.input(ECHO)==1:
          pulse_end = time.time()

       pulse_duration = pulse_end - pulse_start

       distance = pulse_duration * 17150

       distance = round(distance+1.15, 2)
  
       if distance<=15 and distance>=5:
          p.ChangeDutyCycle(10)
          time.sleep(0.5)
          
       if distance>15:
           print ("OBJECT DETECTED")
           p.ChangeDutyCycle(7.5)
           time.sleep(0.5)
         
          


except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()