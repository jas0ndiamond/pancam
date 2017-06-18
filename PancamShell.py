import sys
import re
from Pancam import Pancam

conf_file = "conf/config.json"
    
    
# if(len(sys.argv) == 2)
#     conf_file = argv[1]
    
        
#load_config(conf_file)
    
servo_x_min_pos = 200
servo_x_max_pos = 380
servo_x_home_pos = 320
        
#y
#min -> up
#max -> down 
servo_y_min_pos = 230
servo_y_max_pos = 470
servo_y_home_pos = 330
    
pancam = Pancam("0x40", 60)
pancam.set_x_servo(0, servo_x_min_pos, servo_x_max_pos, servo_x_home_pos)
pancam.set_y_servo(1, servo_y_min_pos, servo_y_max_pos, servo_y_home_pos)
    
def main(sys):
    
    #     while (True):
    #         # Change speed of continuous servo on channel O
    # #         pancam.move_to(0, servo_x_min_pos)
    # #         time.sleep(1)
    # #         
    # #         pancam.move_to(0, servo_x_home_pos )
    # #         time.sleep(1)
    # #         
    # #         pancam.move_to(0, servo_x_max_pos)
    # #         time.sleep(1)
    # #         
    # #         pancam.move_to(0, servo_x_home_pos )
    # #         time.sleep(1)
    #         pos = servo_y_min_pos
    #         while(pos < servo_y_max_pos):
    #             pancam.move_to(1, pos)
    #             pos += 10
    #             
    #         while(pos > servo_y_min_pos):
    #             pancam.move_to(1, pos)
    #             pos -= 10
                
        
    matcher = re.compile("^\s*\d+\s+\d+\s*$")
          
    runshell = True
          
    while(runshell):
        sys.stdout.write(">")
        line = sys.stdin.readline()
                      
        if(line == "q\n" or line == "quit\n" or line == "exit\n"):
            print("Take care!")
            #pancam.shutdown()
            runshell = False
        elif(line == "xhome\n"):
            pancam.move_x_home()
        elif(line == "yhome\n"):
            pancam.move_y_home()
        elif(line == "home\n"):
            pancam.move_home()
        elif(line == "p r\n"):
            pancam.move_right()
        elif(line == "p l\n"):
            pancam.move_left()
        elif(line == "p u\n"):
            pancam.move_up()
        elif(line == "p d\n"):
            pancam.move_down()
        elif( matcher.match(line) ):
            servo_num, servo_pos = line.split(" ")
            pancam.move_to(int(servo_num), int(servo_pos))
        else:
            print("Malformed move command")
    


main(sys)

    