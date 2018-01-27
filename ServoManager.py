import time

from threading import Thread
from datetime import datetime

from lib.Adafruit_PWM_Servo_Driver import PWM

class ServoManager:
    
    def __init__(self, hat_addr, pwm_freq):
        #self.hat_addr = int(hat_addr,16)
        self.hat_addr = hat_addr
        self.pwm_freq = pwm_freq
        
        self.hat_id = 0
        
        self.started = False
        
        #poweroff after 10 minutes
        self.timeout = 10
        
        #self.pwm = PWM(self.hat_addr, debug=True)
        self.start()
        
    def start(self):
        self.last_move = datetime.now()
        
        print("STARTING")
        
        
        
        self.pwm = PWM(self.hat_addr)
        self.pwm.setPWMFreq(self.pwm_freq)
        self.started = True
        

        self.keepalive_thread = Thread(target=self.keepalive)
        self.keepalive_thread.start()
        
    def move_to(self, servo_num, position):
        
        if(self.started is not True):
            self.start()
        
        self.pwm.setPWM(servo_num, self.hat_id, position)
        
        self.last_move = datetime.now()
        
        # allow the servo to move into position
        time.sleep(.5)

    def stop(self):
        print "Stopping"
        
        self.pwm.softwareReset()
        self.started = False
        
    def keepalive(self):
        #every 10 seconds, check the last move date. if too old, self.stop
        
        print "Keepalive"
        
        while(self.started):            
            if( (datetime.now() - self.last_move).seconds / 60 > self.timeout):
                self.stop()
                print "keepalive stop"
            else:
                time.sleep(30)
                print "keepalive alive"
                
        print "Exiting keepalive"
        