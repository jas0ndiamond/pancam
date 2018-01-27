import time
import logging

import threading

from threading import Thread
from datetime import datetime

from lib.Adafruit_PWM_Servo_Driver import PWM

class ServoManager:
    
    def __init__(self, hat_addr, pwm_freq):
        #self.hat_addr = int(hat_addr,16)
        self.hat_addr = hat_addr
        self.pwm_freq = pwm_freq
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        #constuctor call. does not actually lock here
        self.mutex = threading.Lock()
        
        #maybe unhardcode this. or not- panning only needs xy. 
        #will likely not need more than 2 servos, let alone 17.
        self.hat_id = 0
        
        self.started = False
        self.running = True
        
        self.keepalive_sleep = 30
        
        #poweroff after 10 minutes
        self.timeout = 10
        
    def start(self):
        self.last_move = datetime.now()
        
        self.logger.info("ServoManager Starting...")
        
        self.pwm = PWM(self.hat_addr)
        self.pwm.setPWMFreq(self.pwm_freq)
        self.started = True
        self.running = True
        
        self.keepalive_thread = Thread(target=self.keepalive)
        self.keepalive_thread.start()
        
    def move_to(self, servo_num, position):
        
        self.logger.info("_move_to called")

        if(self.started is not True):
            self.start()

        try:
            self.mutex.acquire()

            self.logger.info("Have PWM lock. Moving servo %d to position %d" % (servo_num, position))
            
            self.pwm.setPWM(servo_num, self.hat_id, position)
            self.last_move = datetime.now()
            
            # allow the servo to move into position
            time.sleep(.5)
        finally:
            self.logger.info("Releasing PWM lock")
            self.mutex.release()

    def stop(self):
        self.logger.info("ServoManager Stopping")            
        self.pwm.softwareReset()
        self.started = False
    
            
        
    def isRunning(self):
        return self.running
        
    def keepalive(self):
        #every 10 seconds, check the last move date. if too old, self.stop
        
        self.logger.debug("Keepalive")
        
        while(self.started):            
            if( (datetime.now() - self.last_move).seconds / 60 > self.timeout):
                self.stop()
                self.logger.debug("keepalive stop")
            else:
                self.logger.debug("keepalive alive")
                
                #wish i knew a better way
                i = 0
                while(self.started and i< self.keepalive_sleep):
                    i += 1
                    time.sleep(1)
               
        self.running = False 
        self.logger.debug("Exiting keepalive")
        