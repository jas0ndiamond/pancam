import time
import json
import logging
import Queue
import threading

from threading import Thread
from ServoManager import ServoManager

class Pancam:
    def __init__(self, hat_addr, pwm_freq):
        
        self.min_move_inc = 1
        self.max_move_inc = 100
        self.min_pan_inc = 1
        self.max_pan_inc = 100
        
        #increments go onto the work queue. have to set them after the work queue starts
        #move increment is the distance traveled after /left or /right is called
        self.move_x_inc = 10
        self.move_y_inc = 10
        
        #pan increment is the intermediate distance traveled in a panning op.
        #2 means servo moves 2 units between stops
        self.pan_x_inc = 2
        self.pan_y_inc = 5   
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        self.logger.info("Initializing pancam with hat %s and freq %i" % (hat_addr, pwm_freq) )

        #defaults possibly overriden by set_xy_servo
        self.servo_x_num = 0
        self.servo_y_num = 1

        self.hat_addr = int(hat_addr,16)
        self.pwm_freq = pwm_freq
                
        self.servo_mgr = ServoManager(self.hat_addr, self.pwm_freq)
        self.servo_mgr.start()
        
        #who knows at this point. position set when set_xy_servo is invoked later
        self.servo_x_current_pos = None
        self.servo_y_current_pos = None
        
        self.running = True
        
        self.job_running = False
        
        self.work_queue_max_size = 50
        self.work_queue = Queue.Queue(maxsize=self.work_queue_max_size)
        self.work_queue.mutex = threading.Lock()
                
        self.queueMgr = Thread(target=self.manage_work_queue)
        self.queueMgr.start()

    def add_work(self, thread):
        if(self.running):
            self.work_queue.put(thread)
        else:
            self.logger.warn("Ignoring new work- shutdown in progress")
    
    def manage_work_queue(self):
        while self.running:
            if(self.work_queue.empty()):
                self.logger.debug("waiting for moves")
                time.sleep(.25) 
            else:
                self.logger.debug("Dequeuing move operation")
                    
                try:
                    self.work_queue.mutex.acquire()
                    
                    job = self.work_queue.get()
                   
                    #run task and wait for completion
                    self.logger.debug("Dequeued job started")
                    
                    self.job_running = True
                    job.start()
                    job.join()
                    
                    self.work_queue.task_done()
                    
                    self.logger.debug("Dequeued job finished") 

                finally:
                    self.job_running = False
                    self.work_queue.mutex.release()
                    self.logger.debug("Completed move operation")
                    
        self.logger.info("Exiting manage_work_queue")

    def set_x_move_inc(self, inc):
        if(inc > self.min_move_inc and inc < self.max_move_inc):
            if(self.work_queue.empty()):
                try:
                    self.work_queue.mutex.acquire()
                    self.move_x_inc = inc
                    self.logger.info("Set X move inc to %i" % inc)
                finally:
                    self.work_queue.mutex.release()
            else:
                self.logger.error("Skipping change of x move inc: work queue is not empty or work is in progress")
        else:
            self.logger.error("Error setting X move inc: Invalid value")

    def set_y_move_inc(self, inc):
        if(inc > self.min_move_inc and inc < self.max_move_inc):
            if(self.work_queue.empty() and self.job_running == False):
                try:
                    self.work_queue.mutex.acquire()
                    self.move_y_inc = inc
                    self.logger.info("Set Y move inc to %i" % inc)
                finally:
                    self.work_queue.mutex.release()
            else:
                self.logger.error("Skipping change of y move inc: work queue is not empty or work is in progress")
        else:
            self.logger.error("Error setting Y move inc: Invalid value")
    
    def set_x_pan_inc(self, inc):
        if(inc > self.min_pan_inc and inc < self.max_pan_inc):
            if(self.work_queue.empty() and self.job_running == False):
                try:
                    self.work_queue.mutex.acquire()
                    self.pan_x_inc = inc
                    self.logger.info("Set X pan inc to %i" % inc)
                finally:
                    self.work_queue.mutex.release()
            else:
                self.logger.error("Skipping change of X pan inc: work queue is not empty or work is in progress")
        else:
            self.logger.error("Error setting X pan inc: Invalid value")

    def set_y_pan_inc(self, inc):
        if(inc > self.min_pan_inc and inc < self.max_pan_inc):
            if(self.work_queue.empty() and self.job_running == False):
                try:
                    self.work_queue.mutex.acquire()
                    self.pan_y_inc = inc
                    self.logger.info("Set Y pan inc to %i" % inc)
                finally:
                    self.work_queue.mutex.release()
            else:
                self.logger.error("Skipping change of Y pan inc: work queue is not empty or work is in progress")
        else:
            self.logger.error("Error setting Y pan inc: Invalid value")

    def move_x_home(self):
        self.add_work(Thread(target=self._move_to, 
            args=(self.servo_x_num, self.servo_x_home_pos))) 
        
    def move_y_home(self):
        self.add_work(Thread(target=self._move_to, 
            args=(self.servo_y_num, self.servo_y_home_pos))) 
    
    def move_home(self):
        def my_move():            
            self._move_to(self.servo_x_num, self.servo_x_home_pos)
            
            self._move_to(self.servo_y_num, self.servo_y_home_pos)
    
        self.add_work(Thread(target=my_move))
        
    def move_up_left(self):
        
        def my_move():            
            my_x, my_y = self._get_pos()
            my_move_x, my_move_y = self._get_move_incs() 
            
            #left
            self._move_to(self.servo_x_num, my_x - my_move_x)
            
            #up
            self._move_to(self.servo_y_num, my_y - my_move_y)

    
        self.add_work(Thread(target=my_move))
        
    def move_left(self):
        def my_move():
            my_x = self._get_pos()[0]
            my_move_x = self._get_move_incs()[1]
            
            self._move_to(self.servo_x_num, my_x - my_move_x)
        
        self.add_work(Thread(target=my_move))    

    def move_down_left(self):
        
        def my_move():            
            my_x, my_y = self._get_pos()
            my_move_x, my_move_y = self._get_move_incs() 
            
            #left
            self._move_to(self.servo_x_num, my_x - my_move_x)
            
            #down
            self._move_to(self.servo_y_num, my_y + my_move_y)

    
        self.add_work(Thread(target=my_move))

    def move_up_right(self):
        
        def my_move():         
            my_x, my_y = self._get_pos()
            my_move_x, my_move_y = self._get_move_incs() 
            
            self._move_to(self.servo_x_num, my_x + my_move_x)
            
            self._move_to(self.servo_y_num, my_y - my_move_y)

    
        self.add_work(Thread(target=my_move))

    def move_right(self):
        
        def my_move():
            my_x = self._get_pos()[0]
            my_move_x = self._get_move_incs()[0]
            
            self._move_to(self.servo_x_num, my_x + my_move_x)
        
        self.add_work(Thread(target=my_move))     
    
    def move_down_right(self):
        
        def my_move():          
            my_x, my_y = self._get_pos()  
            my_move_x, my_move_y = self._get_move_incs() 
            
            self._move_to(self.servo_x_num, my_x + my_move_x)
            
            self._move_to(self.servo_y_num, my_y + my_move_y)

    
        self.add_work(Thread(target=my_move))
        
    def move_up(self):

        def my_move():
            my_y = self._get_pos()[1]
            my_move_y = self._get_move_incs()[1]
            
            self._move_to(self.servo_y_num, my_y - my_move_y)

        self.add_work(Thread(target=my_move))

    def move_down(self):
        def my_move():
            my_y = self._get_pos()[1]
            my_move_y = self._get_move_incs()[1]
            
            self._move_to(self.servo_y_num, my_y + my_move_y)

        self.add_work(Thread(target=my_move))
    
    def _move_to(self, servo_num, position):      
        
        self.logger.info("_move_to called")
        
        my_x, my_y = self._get_pos()
        new_position = None
        
        # this could be a lot better
        if(servo_num == self.servo_x_num):
            if(my_x is None or position != my_x):
                    
                if(position > self.servo_x_max_pos):
                    new_position = self.servo_x_max_pos
                elif(position < self.servo_x_min_pos):
                    new_position = self.servo_x_min_pos
                else:
                    new_position = position
    
                self.logger.info("Moved X servo to pos %i" % new_position)
    
                self.servo_mgr.move_to(servo_num, new_position)
                self._set_x_pos(new_position)

                time.sleep(.5)
            else:
                self.logger.info("X servo already in position %i" % position)
            
        elif(servo_num == self.servo_y_num):
            if(my_y is None or position != my_y):
                if(position > self.servo_y_max_pos):
                    new_position = self.servo_y_max_pos
                elif(position < self.servo_y_min_pos):
                    new_position = self.servo_y_min_pos
                else:
                    new_position = position
               
                self.logger.info("Moved Y servo to pos %i" % new_position)
                
                self.servo_mgr.move_to(servo_num, new_position)
                self._set_y_pos(new_position)
                        
            else:
                self.logger.info("Y servo already in position %i" % position)
        else:
            # throw exception
            self.logger.error("Unknown servo %i" % servo_num)
                

    def pan_to_by_increment(self, servo_num, position, increment):
        def my_move(servo_num, position, increment):
            
            my_x, my_y = self._get_pos()
                   
            if(servo_num == self.servo_x_num):
                if(my_x > position):
                    #moving left, negative
                    while(self.my_x > position):
                        self._move_to(servo_num, my_x - increment)
                        my_x = self._get_pos()[0]
                        #want to arrive at min, then break the loop
                        if(my_x == self.servo_x_min_pos):
                            break
                        
                elif(my_x < position):
                    #moving right, positive
                    while(my_x < position):
                        self._move_to(servo_num, my_x + increment)
                        my_x = self._get_pos()[0]
                        
                        #want to arrive at max, then break the loop                    
                        if(my_x == self.servo_x_max_pos):
                            break
                    
            elif(servo_num == self.servo_y_num):
                if(my_y > position):
                    #moving up, negative
                    while(my_y > position):
                        self._move_to(servo_num, my_y - increment)
                        my_y = self._get_pos()[1]
                        
                        if(my_y == self.servo_y_min_pos):
                            break
                elif(my_y < position):
                    #moving down, positive
                    while(my_y < position):
                        self._move_to(servo_num, my_y + increment)
                        my_y = self._get_pos()[1]
                        
                        if(my_y == self.servo_y_max_pos):
                            break
            else:
                self.logger.error("Unknown servo %i" % servo_num)   
            
            
        self.add_work(Thread(target=my_move, 
               args=(servo_num, position, increment))) 

    def pan_to(self, servo_num, position):
        
        #safely get increments
        my_pan_x, my_pan_y = self._get_pan_incs()
        
        if(servo_num == self.servo_x_num):
            self.pan_to_by_increment(servo_num, position, my_pan_x)
        elif(servo_num == self.servo_y_num):
            self.pan_to_by_increment(servo_num, position, my_pan_y)
        else:
            self.logger.error("Unknown servo %i" % servo_num)   
        
    def stop(self):
        self.logger.info("Stopping pancam")   
        
        if(self.running):
            #signal that we're stopped after the avoid close operation is completed    
            self.running = False
                
            #clear work queue
            self.logger.debug("Clearing work queue")   
            self.work_queue.queue.clear()
                    
            #explicitly move to home position, bypassing the work queue
            #since we hold the mutex nothing should supplant move_home 
            self.logger.debug("Returning to home position")
            self._move_to(self.servo_x_num, self.servo_x_home_pos)
            self._move_to(self.servo_y_num, self.servo_y_home_pos)
                            
            #shutdown the servo manager which will issue pwm reset
            self.logger.debug("Shutting down servo manager")
            self.servo_mgr.stop()
        else:
            self.logger.warn("Pancam already stopped")
                
    def set_x_servo(self, servo_num, min_pos, max_pos, home_pos):
        
        self.logger.info("Loading x servo with %s " % json.dumps({"servo_num":servo_num, "min_pos":min_pos, "max_pos":max_pos,"home_pos":home_pos}))
        
        self.servo_x_num = servo_num
        self.servo_x_home_pos = home_pos
        self.servo_x_min_pos = min_pos
        self.servo_x_max_pos = max_pos
        
        self.move_x_home()
                
    def set_y_servo(self, servo_num, min_pos, max_pos, home_pos):
        
        self.logger.info("Loading y servo with %s " % json.dumps({"servo_num":servo_num, "min_pos":min_pos, "max_pos":max_pos,"home_pos":home_pos}))

        self.servo_y_num = servo_num
        self.servo_y_home_pos = home_pos

        self.servo_y_min_pos = min_pos
        self.servo_y_max_pos = max_pos
        
        self.move_y_home()
    
    def get_move_incs(self):
        #this should leapfrog the work queue to determine where the servo is between moves
        try:
            self.work_queue.mutex.acquire()
            (x,y) = self._get_move_incs()
        finally:
            self.work_queue.mutex.release()
        
        return (x,y)
    
    def _get_move_incs(self):
        x = self.move_x_inc
        y = self.move_y_inc
        return (x,y)
    
    def get_pan_incs(self):
        #this should leapfrog the work queue to determine where the servo is between moves
        try:
            self.work_queue.mutex.acquire()
            (x,y) = self._get_pan_incs()
        finally:
            self.work_queue.mutex.release()
        
        return (x,y)
    
    def _get_pan_incs(self):
        x = self.pan_x_inc
        y = self.pan_y_inc
        return (x,y)
    
    def get_pos(self):
        
        #this should leapfrog the work queue to determine where the servo is between moves
        try:
            self.work_queue.mutex.acquire()
        #prevent moves from occuring
        #with self.work_queue.mutex:
            x,y = self._get_pos()
        finally:
            self.work_queue.mutex.release()
        
        return (x,y)
    
    def _get_pos(self):
        #expect the invoker to hold lock
        x = self.servo_x_current_pos
        y = self.servo_y_current_pos
        return (x,y)
    
    def _set_x_pos(self, new_x):
        self.servo_x_current_pos = new_x
        
    def _set_y_pos(self, new_y):
        self.servo_y_current_pos = new_y
            
