

import time


from lib.Adafruit_PWM_Servo_Driver import PWM

class Pancam :
    
    def __init__(self, hat_addr, pwm_freq):
        
        print("Initializing pancam with hat %s and freq %i" % (hat_addr, pwm_freq) )
        
        self.hat_addr = int(hat_addr,16)
        self.pwm_freq = pwm_freq
        
        #self.pwm = PWM(self.hat_addr, debug=True)
        self.pwm = PWM(self.hat_addr)
        
        self.pwm.setPWMFreq(self.pwm_freq)
        
        self.pan_x_inc = 10
        self.pan_y_inc = 10
        
        self.span_x_inc = 2
        self.span_y_inc = 5
        
        #who knows at this point?
        self.servo_x_current_pos = None
        self.servo_y_current_pos = None
    
#     def setServoPulse(self, channel, pulse):
#         pulseLength = 1000000                   # 1,000,000 us per second
#         pulseLength /= 60                       # 60 Hz
#         print("%d us per period" % pulseLength)
#         pulseLength /= 4096                     # 12 bits of resolution
#         print( "%d us per bit" % pulseLength)
#         pulse *= 1000
#         pulse /= pulseLength
#         self.pwm.setPWM(channel, 0, pulse)

    def set_x_pan_inc(self, inc):
        if(inc > 2 and inc < 100):
            self.pan_x_inc = inc
            print("Set X pan inc to %i" % inc)
        else:
            print("Error setting X pan inc")

    def set_y_pan_inc(self, inc):
        if(inc > 2 and inc < 100):
            self.pan_y_inc = inc
            print("Set Y pan inc to %i" % inc)
        else:
            print("Error setting Y pan inc")

    def pan_x_home(self):
        self.pan_to(self.servo_x_num, self.servo_x_home_pos)
        
    def pan_y_home(self):
        self.pan_to(self.servo_y_num, self.servo_y_home_pos)
    
    def pan_home(self):
        self.pan_x_home()
        self.pan_y_home()
    
    def pan_left(self):
        self.pan_to(self.servo_x_num, self.servo_x_current_pos - self.pan_x_inc)

    def pan_right(self):
        self.pan_to(self.servo_x_num, self.servo_x_current_pos + self.pan_x_inc)
        
    def pan_up(self):
        self.pan_to(self.servo_y_num, self.servo_y_current_pos - self.pan_y_inc)

    def pan_down(self):
        self.pan_to(self.servo_y_num, self.servo_y_current_pos + self.pan_y_inc)
    
    def pan_to(self, servo_num, position):      
        #this could be a lot better
        if(servo_num == 0):
            if(self.servo_x_current_pos is None or position != self.servo_x_current_pos):    
                if(position > self.servo_x_max_pos):
                    self.servo_x_current_pos = self.servo_x_max_pos
                elif(position < self.servo_x_min_pos):
                    self.servo_x_current_pos = self.servo_x_min_pos
                else:
                    self.servo_x_current_pos = position
                    
                print( "Panned X servo to pos %i" % self.servo_x_current_pos)
    
                self.pwm.setPWM(servo_num, 0, self.servo_x_current_pos)
                
                #allow the servo to move into position
                time.sleep(.5)
            else:
                print("X servo already in position %i" % position)
            
        elif(servo_num == 1):
            if(self.servo_y_current_pos is None or position != self.servo_y_current_pos):
                if(position > self.servo_y_max_pos):
                    self.servo_y_current_pos = self.servo_y_max_pos
                elif(position < self.servo_y_min_pos):
                    self.servo_y_current_pos = self.servo_y_min_pos
                else:
                    self.servo_y_current_pos = position
               
                print( "Panned y servo to pos %i" % self.servo_y_current_pos)
                
                self.pwm.setPWM(servo_num, 0, self.servo_y_current_pos)
    
                    #allow the servo to move into position
                time.sleep(.5)
            else:
                print("Y servo already in position %i" % position)
                
        else:
            print("Unknown servo %i" % servo_num)

    def span_to_by_increment(self, servo_num, position, increment):       
        if(servo_num == 0):
            if(self.servo_x_current_pos > position):
                print("spanning left")
                #moving left, negative
                while(self.servo_x_current_pos > position):
                    print("panning left")
                    self.pan_to(servo_num, self.servo_x_current_pos - increment)
                    
                    #want to arrive at min, then break the loop
                    if(self.servo_x_current_pos == self.servo_x_min_pos):
                        break
                    
            elif(self.servo_x_current_pos < position):
                #moving right, positive
                print("spanning right")
                while(self.servo_x_current_pos < position):
                    print("panning right")
                    self.pan_to(servo_num, self.servo_x_current_pos + increment)

                    #want to arrive at max, then break the loop                    
                    if(self.servo_x_current_pos == self.servo_x_max_pos):
                        break
                
        elif(servo_num == 1):
            if(self.servo_y_current_pos > position):
                #moving up, negative
                while(self.servo_y_current_pos > position):
                    self.pan_to(servo_num, self.servo_y_current_pos - increment)
                    
                    if(self.servo_y_current_pos == self.servo_y_min_pos):
                        break
            elif(self.servo_y_current_pos < position):
                #moving down, positive
                while(self.servo_y_current_pos < position):
                    self.pan_to(servo_num, self.servo_y_current_pos + increment)
                    
                    if(self.servo_y_current_pos == self.servo_y_max_pos):
                        break
        else:
            print("Unknown servo %i" % servo_num)   

    def span_to(self, servo_num, position):
        if(servo_num == 0):
            self.span_to_by_increment(servo_num, position, self.span_x_inc)
        elif(servo_num == 1):
            self.span_to_by_increment(servo_num, position, self.span_y_inc)
        else:
            print("Unknown servo %i" % servo_num)   
        

                
    def set_x_servo(self, servo_num, min_pos, max_pos, home_pos):
        #determine middle
        
        self.servo_x_num = servo_num
        #self.servo_x_middle = (max_pos - min_pos)/2
        self.servo_x_home_pos = home_pos
        self.servo_x_min_pos = min_pos
        self.servo_x_max_pos = max_pos
        
        self.pan_x_home()
                
    def set_y_servo(self, servo_num, min_pos, max_pos, home_pos):
        #determine middle
        self.servo_y_num = servo_num
        #self.servo_y_middle = (max_pos - min_pos)/2
        self.servo_y_home_pos = home_pos

        self.servo_y_min_pos = min_pos
        self.servo_y_max_pos = max_pos
        
        self.pan_y_home()


    
    