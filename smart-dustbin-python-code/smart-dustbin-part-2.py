# include libraries
import RPi.GPIO as GPIO
import time
import thingspeak

# set gpio mode and warnings
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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
channel_id = xxxxxxx # input your Channel ID
write_key  = 'xxxxxxx' # input your write key
channel = thingspeak.Channel(id=channel_id, api_key=write_key)

# function to re-map a number from one range to another
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
        showLED("red")
    elif capacity > 50:
        showLED("blue")
    else:
        showLED("green")
    
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

    
GPIO.cleanup()