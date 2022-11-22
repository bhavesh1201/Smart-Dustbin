#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)



 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
servoPIN = 17



GPIO.setup(servoPIN, GPIO.OUT)
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


 
p = GPIO.PWM(servoPIN, 50) 
p.start(0) 

def setMotorAngle(angle: int):
    duty = angle / 18 + 2

    p.start(duty)
    time.sleep(1)

    p.ChangeDutyCycle(0)
    

def ctrlMotor(command):
    if command == "open":
        setMotorAngle(90)
    elif command == "close":
        setMotorAngle(0)
        

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            if (dist > 12):
                print("closed")
                status = "close"
                ctrlMotor("close")
                   
            else:
                print("opened")
                status = "open"
                ctrlMotor("open")
                
            
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()