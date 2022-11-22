#Libraries
import RPi.GPIO as GPIO
import time
import thingspeak
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)



 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
servoPIN = 17


# declare pins
trigPin = 20
echoPin = 21
redLedPin = 17
blueLedPin = 27
greenLedPin = 22


# initialize pins
GPIO.setup(trigPin,GPIO.OUT)
GPIO.setup(echoPin,GPIO.IN)
GPIO.setup(redLedPin,GPIO.OUT)
GPIO.setup(blueLedPin,GPIO.OUT)
GPIO.setup(greenLedPin,GPIO.OUT)

# declare variable
lastSyncTime = 0

# setup thingspeak parameters
channel_id = 1943325 # input your Channel ID
write_key  = '8ILSIB37AUS9WGD5' # input your write key
channel = thingspeak.Channel(id=channel_id, api_key=write_key)



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
        
        
        
def translate(x, in_min, in_max, out_min, out_max):
     return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min       

def get_capacity():
    # create a 10 microsecond pulse to trigger the ultrasonic module
    
    # set ultrasonic trigger pin to high
    GPIO.output(trigPin, True)
    # wait for 10 microsecond
    time.sleep(0.00001)
    # set ultrasonic trigger pin to low
    GPIO.output(trigPin, False)
    
    # after pulsing, we need to listen for a signal
    
    # record start time of no signal
    while GPIO.input(echoPin) == 0:
        pulse_start = time.time()
        
    # record end time of a received signal
    while GPIO.input(echoPin) == 1:
        pulse_end = time.time()
        
    # find the time difference between the signals
    pulse_duration = pulse_end - pulse_start
    
    # multiply with the speed of sound (34300 cm/s)
    # and divide by 2 to get distance, because there and back
    distance = (pulse_duration * 34300) / 2
    
    # map distance range into percentage range
    percentage = translate(distance, 35, 15, 0, 100)
    
    # return the constrained values of min and max to 0 and 100
    return max(min(100, percentage), 0)

def millis():
    return time.time() * 1000

def show_LED(colour):
    # show only red LED
    if colour == "red":
        GPIO.output(redLedPin, True)
        GPIO.output(blueLedPin, False)
        GPIO.output(greenLedPin, False)
    # show only blue LED
    elif colour == "blue":
        GPIO.output(redLedPin, False)
        GPIO.output(blueLedPin, True)
        GPIO.output(greenLedPin, False)
    # show only green LED
    elif colour == "green":
        GPIO.output(redLedPin, False)
        GPIO.output(blueLedPin, False)
        GPIO.output(greenLedPin, True)

# main loop
while True:
    # get distance from the ultrasonic sensor
    capacity = get_capacity()
    print("Dustbin Capacity: %i%%" % capacity)
    
    if capacity > 75:
        show_LED("red")
    elif capacity > 50:
        show_LED("blue")
    else:
        show_LED("green")
    
    # send data to ThingSpeak every 15s
    # free account has an api limit of 15s
    if (millis() - lastSyncTime > 15000):
        try:
            # send data to ThingSpeak
            channel.update({'field1': capacity})
            print("Update success! Data: %i" % capacity)
        except:
            print("Connection to ThingSpeak failed!")
        lastSyncTime = millis()
    
    # add some delay so the previous signal does not interfere with new signal
    time.sleep(0.1)