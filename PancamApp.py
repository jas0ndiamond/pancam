from flask import Flask, redirect, request

import atexit
import sys
import os
import json
import logging
import signal

from Pancam import Pancam

app = Flask(__name__, static_url_path='/www', static_folder=os.path.dirname(__file__) + "/www")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Pancam starting up...")

conf_file = os.path.dirname(__file__) + "/conf/config.json"    
    
if(len(sys.argv) == 2):
    conf_file = sys.argv[1]

logger.info("Loading config from: %s", conf_file)
    
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
    
def sig_int_handler(signal, frame):    
    pancam.stop()
    
    sys.exit()
    
signal.signal(signal.SIGINT, sig_int_handler)
    

    
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
    
    (x,y) = pancam.get_pos()
    return get_movement_response({"xPos": x, "yPos": y})

@app.route('/pancam/get_status')
def get_status():
    
    (x,y) = pancam.get_pos()
    (xMove, yMove) = pancam.get_move_incs()
    (xPan, yPan) = pancam.get_pan_incs()
    return get_movement_response({"xPos": x, "yPos": y, "xPan": xPan, "yPan": yPan, "xMove": xMove, "yMove": yMove})
 
@app.route("/pancam/up_left")
def move_up_left():
    pancam.move_up_left()
    
    return get_response()
    
 
@app.route("/pancam/left")
def move_left():
    pancam.move_left()
    
    return get_response()
    
@app.route("/pancam/down_left")
def move_down_left():
    pancam.move_down_left()
    
    return get_response()
    

@app.route("/pancam/up_right")
def move_up_right():
    pancam.move_up_right()

    return get_response()
 
  
@app.route("/pancam/right")
def move_right():
   
    pancam.move_right()
    
    return get_response()
 
@app.route("/pancam/down_right")
def move_down_right():
    
    pancam.move_down_right()
    
    return get_response()
 
 
@app.route("/pancam/up")
def move_up():
    
    pancam.move_up()

    return get_response()    
 
@app.route("/pancam/down")
def move_down():   
    pancam.move_down()
    
    return get_response()

 
@app.route("/pancam/move_y_home")
def move_y_home():
    pancam.move_y_home()
    
    return get_response()
     
@app.route("/pancam/move_x_home")
def move_x_home():
    pancam.move_x_home()
    
    return get_response()

@app.route("/pancam/home")
def move_home():
    
    pancam.move_home()
    
    return get_response()

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
     
@app.route("/pancam/set_x_move_inc")
def set_x_move_inc():
    inc = int(request.args.get("inc"))
    pancam.set_x_move_inc(inc)
    
    return get_movement_response({"x_inc": inc})
    
@app.route("/pancam/set_y_move_inc")
def set_y_move_inc():
    inc = int(request.args.get("inc"))
    pancam.set_y_move_inc(inc)

    return get_movement_response({"y_inc": inc})
     
@app.route("/pancam/move_to")
def move_to():
    newX = request.args.get("xPos")
    newY = request.args.get("yPos")

    if(newX != ""):
        pancam._move_to(0, int(newX))

    if(newY != ""):
        pancam._move_to(1, int(newY))

    response = get_response()

    return response

@app.route("/pancam/pan_to", methods=['GET'])
def pan_to():
    newX = request.args.get("xPos")
    newY = request.args.get("yPos")
    
    if(newX != None and newX != ""):
        pancam.pan_to(0, int(newX))

    if(newY != None and newY != ""):
        pancam.pan_to(1, int(newY))
        
    response = get_response()

    return response
    
@app.route("/pancam/stop", methods=['GET'])
def stop():
    pancam.stop()
        
    return get_response()

    
def get_movement_response(result):
    return app.response_class(
        response=json.dumps(result, sort_keys=True),
        status=200,
        mimetype='application/json'
    )
    
def get_response():
    return app.response_class(
        response=json.dumps({}, sort_keys=True),
        status=200,
        mimetype='application/json'
    )
    
##############################
#flask seems to require this here, after the endpoints are defined above
if __name__ == '__main__':
    
    #probably won't need to do this since sigint is caught
    #still worth it though
    atexit.register(pancam.stop)
    
    #run flask app
    app.run(host='0.0.0.0', port=5000)