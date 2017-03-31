from flask import Flask, redirect, request
app = Flask(__name__)

import sys
import os
import json
from Pancam import Pancam

conf_file = os.path.dirname(__file__) + "/conf/config.json"
    
if(len(sys.argv) == 2):
    conf_file = sys.argv[1]
    
json_data=open(conf_file).read()

data = json.loads(json_data)
#print(data)
    
hat_addr = data["hat_addr"]
pwm_freq = data["pwm_freq"]

#x
#min -> left
#max -> right
servo_x_id = data["servox"]["id"]
servo_x_min_pos = data["servox"]["min"]
servo_x_max_pos = data["servox"]["max"]
servo_x_home_pos = data["servox"]["home"]
         
#y
#min -> up
#max -> down 
servo_y_id = data["servoy"]["id"]
servo_y_min_pos = data["servoy"]["min"]
servo_y_max_pos = data["servoy"]["max"]
servo_y_home_pos = data["servoy"]["home"]

    
pancam = Pancam(hat_addr, pwm_freq)
pancam.set_x_servo(servo_x_id, servo_x_min_pos, servo_x_max_pos, servo_x_home_pos)
pancam.set_y_servo(servo_y_id, servo_y_min_pos, servo_y_max_pos, servo_y_home_pos)
    
#def main(sys):
    
    #     while (True):
    #         # Change speed of continuous servo on channel O
    # #         pancam.pan_to(0, servo_x_min_pos)
    # #         time.sleep(1)
    # #         
    # #         pancam.pan_to(0, servo_x_home_pos )
    # #         time.sleep(1)
    # #         
    # #         pancam.pan_to(0, servo_x_max_pos)
    # #         time.sleep(1)
    # #         
    # #         pancam.pan_to(0, servo_x_home_pos )
    # #         time.sleep(1)
    #         pos = servo_y_min_pos
    #         while(pos < servo_y_max_pos):
    #             pancam.pan_to(1, pos)
    #             pos += 10
    #             
    #         while(pos > servo_y_min_pos):
    #             pancam.pan_to(1, pos)
    #             pos -= 10
                
        
#     matcher = re.compile("^\s*\d+\s+\d+\s*$")
#          
#     runshell = True
#          
#     while(runshell):
#         sys.stdout.write(">")
#         line = sys.stdin.readline()
#                      
#         if(line == "q\n" or line == "quit\n" or line == "exit\n"):
#             print("Take care!")
#             #pancam.shutdown()
#             runshell = False
#         elif(line == "xhome\n"):
#             pancam.pan_x_home()
#         elif(line == "yhome\n"):
#             pancam.pan_y_home()
#         elif(line == "home\n"):
#             pancam.pan_home()
#         elif(line == "p r\n"):
#             pancam.pan_right()
#         elif(line == "p l\n"):
#             pancam.pan_left()
#         elif(line == "p u\n"):
#             pancam.pan_up()
#         elif(line == "p d\n"):
#             pancam.pan_down()
#         elif( matcher.match(line) ):
#             servo_num, servo_pos = line.split(" ")
#             pancam.pan_to(int(servo_num), int(servo_pos))
#         else:
#             print("Malformed move command")
    
#

#main(sys)

#####################################

@app.route('/')
def root():
    return redirect("/pancam")
 
 
@app.route('/pancam')
def home():
     
    #main ui
     
    #launch v4dl process. check first
     
    out = "hey"
     
    return out
 
@app.route("/pancam/left")
def pan_left():
    pancam.pan_left()
 
@app.route("/pancam/right")
def pan_right():
    pancam.pan_right()
 
@app.route("/pancam/up")
def pan_up():
    pancam.pan_up()
 
@app.route("/pancam/down")
def pan_down():
    pancam.pan_down()
 
@app.route("/pancam/reset_y")
def pan_y_home():
    pancam.pan_y_home()
     
@app.route("/pancam/reset_x")
def pan_x_home():
    pancam.pan_x_home()
     
@app.route("/pancam/pan_to")
def pan_to():
    servo = request.args.get("servo")
    position = request.args.get("position")
     
    if(servo == "x"):
        pancam.pan_to(servo_x_id, int(position))
    elif(servo == "y"):
        pancam.pan_to(servo_y_id, int(position))
    
@app.route("/pancam/span_to", methods=['GET'])
def span_to():
    servo = request.args.get("servo")
    position = request.args.get("position")
    
    if(servo == "x"):
        pancam.span_to(servo_x_id, int(position))
    elif(servo == "y"):
        pancam.span_to(servo_y_id, int(position))
    else:
        print("Unknown servo %s" % servo)
     
@app.route("/pancam/reset")
def pan_reset():
    pancam.pan_home()
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    #################################3
    #only ctrl-c gets you to this point

    
    