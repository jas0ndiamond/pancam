from flask import Flask, redirect, request


import sys
import os
import json
from Pancam import Pancam

app = Flask(__name__, static_url_path='/www', static_folder=os.path.dirname(__file__) + "/www")

conf_file = os.path.dirname(__file__) + "/conf/config.json"
    
if(len(sys.argv) == 2):
    conf_file = sys.argv[1]
    
json_data=open(conf_file).read()

data = json.loads(json_data)
#print(data)
    
hat_addr = data["hat_addr"]
pwm_freq = data["pwm_freq"]

pancam_page = open(os.path.dirname(__file__) + "/www/index.html").read()

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
#             pancam.move_x_home()
#         elif(line == "yhome\n"):
#             pancam.move_y_home()
#         elif(line == "home\n"):
#             pancam.move_home()
#         elif(line == "p r\n"):
#             pancam.move_right()
#         elif(line == "p l\n"):
#             pancam.move_left()
#         elif(line == "p u\n"):
#             pancam.move_up()
#         elif(line == "p d\n"):
#             pancam.move_down()
#         elif( matcher.match(line) ):
#             servo_num, servo_pos = line.split(" ")
#             pancam.move_to(int(servo_num), int(servo_pos))
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
    return pancam_page     

@app.route('/pancam/get_pos')
def get_pos():
    return get_movement_response({"xPos": pancam.get_x_pos(), "yPos": pancam.get_y_pos()})

 
@app.route("/pancam/left")
def move_left():
    
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    pancam.move_left()
    
    return get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })
    
@app.route("/pancam/right")
def move_right():
    
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    pancam.move_right()
    
    return get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })
 
@app.route("/pancam/up")
def move_up():
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    pancam.move_up()
    
    return get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

    
 
@app.route("/pancam/down")
def move_down():
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    pancam.move_down()
    
    return get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

 
@app.route("/pancam/move_y_home")
def move_y_home():
    
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    pancam.move_y_home()
    
    return get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

     
@app.route("/pancam/move_x_home")
def move_x_home():
    
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    pancam.move_x_home()
    
    return get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

@app.route("/pancam/home")
def pan_reset():
        
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    pancam.move_home()
    
    return get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

@app.route("/pancam/set_x_pan_inc")
def set_x_pan_inc():
    inc = int(request.args.get("inc"))
    pancam.set_x_pan_inc(inc)
    
    return get_movement_response({"x_inc": inc})
    
@app.route("/pancam/set_y_pan_inc")
def set_y_pan_inc():
    inc = int(request.args.get("inc"))
    pancam.set_y_pan_inc(inc)

    return get_movement_response({"y_inc": inc})
     
@app.route("/pancam/move_to")
def move_to():
    newX = request.args.get("xPos")
    newY = request.args.get("yPos")
    
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    if(newX != ""):
        pancam.move_to(0, int(newX))

    if(newY != ""):
        pancam.move_to(1, int(newY))
        
    response = get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

    return response

@app.route("/pancam/pan_to", methods=['GET'])
def pan_to():
    newX = request.args.get("xPos")
    newY = request.args.get("yPos")
    
    oldx = pancam.get_x_pos()
    oldy = pancam.get_y_pos()
    
    if(newX != ""):
        pancam.pan_to(0, int(newX))

    if(newY != ""):
        pancam.pan_to(1, int(newY))
        
    response = get_movement_response({"oldX":oldx, "oldY":oldy, "newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

    return response
    
@app.route("/pancam/stop", methods=['GET'])
def stop():
    pancam.move_home()
    pancam.stop()
    
    return get_movement_response({"newX":pancam.get_x_pos(), "newY":pancam.get_y_pos() })

    
def get_movement_response(result):
    return app.response_class(
        response=json.dumps(result, sort_keys=True),
        status=200,
        mimetype='application/json'
    )
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    #################################3
    #only ctrl-c gets you to this point

    
    