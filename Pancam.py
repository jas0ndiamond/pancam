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
        
        self.move_x_inc = 10
        self.move_y_inc = 10
        
        self.pan_x_inc = 2
        self.pan_y_inc = 5
        
        #who knows at this point?
        self.servo_x_current_pos = None
        self.servo_y_current_pos = None

    def set_x_pan_inc(self, inc):
        if(inc > 2 and inc < 100):
            self.move_x_inc = inc
            print("Set X move inc to %i" % inc)
        else:
            print("Error setting X move inc")

    def set_y_pan_inc(self, inc):
        if(inc > 2 and inc < 100):
            self.move_y_inc = inc
            print("Set Y move inc to %i" % inc)
        else:
            print("Error setting Y move inc")

    def move_x_home(self):
        self.move_to(self.servo_x_num, self.servo_x_home_pos)
        
    def move_y_home(self):
        self.move_to(self.servo_y_num, self.servo_y_home_pos)
    
    def move_home(self):
        self.move_x_home()
        self.move_y_home()
    
    def move_left(self):
        self.move_to(self.servo_x_num, self.servo_x_current_pos - self.move_x_inc)

    def move_right(self):
        self.move_to(self.servo_x_num, self.servo_x_current_pos + self.move_x_inc)
        
    def move_up(self):
        self.move_to(self.servo_y_num, self.servo_y_current_pos - self.move_y_inc)

    def move_down(self):
        self.move_to(self.servo_y_num, self.servo_y_current_pos + self.move_y_inc)
    
    def move_to(self, servo_num, position):      
        #this could be a lot better
        if(servo_num == 0):
            if(self.servo_x_current_pos is None or position != self.servo_x_current_pos):    
                if(position > self.servo_x_max_pos):
                    self.servo_x_current_pos = self.servo_x_max_pos
                elif(position < self.servo_x_min_pos):
                    self.servo_x_current_pos = self.servo_x_min_pos
                else:
                    self.servo_x_current_pos = position
                    
                print( "Moved X servo to pos %i" % self.servo_x_current_pos)
    
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
               
                print( "Moved y servo to pos %i" % self.servo_y_current_pos)
                
                self.pwm.setPWM(servo_num, 0, self.servo_y_current_pos)
    
                #allow the servo to move into position
                time.sleep(.5)
            else:
                print("Y servo already in position %i" % position)
                
        else:
            print("Unknown servo %i" % servo_num)

    def pan_to_by_increment(self, servo_num, position, increment):       
        if(servo_num == 0):
            if(self.servo_x_current_pos > position):
                #moving left, negative
                while(self.servo_x_current_pos > position):
                    self.move_to(servo_num, self.servo_x_current_pos - increment)
                    
                    #want to arrive at min, then break the loop
                    if(self.servo_x_current_pos == self.servo_x_min_pos):
                        break
                    
            elif(self.servo_x_current_pos < position):
                #moving right, positive
                while(self.servo_x_current_pos < position):
                    self.move_to(servo_num, self.servo_x_current_pos + increment)

                    #want to arrive at max, then break the loop                    
                    if(self.servo_x_current_pos == self.servo_x_max_pos):
                        break
                
        elif(servo_num == 1):
            if(self.servo_y_current_pos > position):
                #moving up, negative
                while(self.servo_y_current_pos > position):
                    self.move_to(servo_num, self.servo_y_current_pos - increment)
                    
                    if(self.servo_y_current_pos == self.servo_y_min_pos):
                        break
            elif(self.servo_y_current_pos < position):
                #moving down, positive
                while(self.servo_y_current_pos < position):
                    self.move_to(servo_num, self.servo_y_current_pos + increment)
                    
                    if(self.servo_y_current_pos == self.servo_y_max_pos):
                        break
        else:
            print("Unknown servo %i" % servo_num)   

    def pan_to(self, servo_num, position):
        if(servo_num == 0):
            self.pan_to_by_increment(servo_num, position, self.pan_x_inc)
        elif(servo_num == 1):
            self.pan_to_by_increment(servo_num, position, self.pan_y_inc)
        else:
            print("Unknown servo %i" % servo_num)   
        
    def stop(self):
        self.pwm.softwareReset()
                
    def set_x_servo(self, servo_num, min_pos, max_pos, home_pos):
        #determine middle
        
        self.servo_x_num = servo_num
        #self.servo_x_middle = (max_pos - min_pos)/2
        self.servo_x_home_pos = home_pos
        self.servo_x_min_pos = min_pos
        self.servo_x_max_pos = max_pos
        
        self.move_x_home()
                
    def set_y_servo(self, servo_num, min_pos, max_pos, home_pos):
        #determine middle
        self.servo_y_num = servo_num
        #self.servo_y_middle = (max_pos - min_pos)/2
        self.servo_y_home_pos = home_pos

        self.servo_y_min_pos = min_pos
        self.servo_y_max_pos = max_pos
        
        self.move_y_home()

    def get_x_pos(self):
        return self.servo_x_current_pos
    
    def get_y_pos(self):
        return self.servo_y_current_pos
    
    