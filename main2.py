from ultralytics import YOLO
import random
from deepsort import Tracker


# importing the Computer Vision module
import cv2
from flask import Flask,Response,render_template,request,redirect
import mysql.connector
import numpy as np
from flask_socketio import SocketIO, emit

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.sql import func #import sqlalchemy functions
from sqlalchemy import update,create_engine,select #import sqlalchemy update function and create_engine function
from sqlalchemy.orm import sessionmaker #import sqlalchemy session maker function

app=Flask(__name__,static_url_path='/static') #initializing the flask app with the name 'app' and static_url_path for static files
socketio=SocketIO(app) #socketio initialization for real-time communication

# ========== DB CONNECTION -- SQLALCHEMY (START) ===========
#Database Configuration with MySQL
#     -->     db type | username: password | path to database name    
engine_url='mysql+pymysql://root:''@localhost/enpemo'
if not database_exists(engine_url):
    create_database(engine_url)
app.config['SQLALCHEMY_DATABASE_URI']=engine_url
engine=create_engine(engine_url)
Session=sessionmaker(engine)
db=SQLAlchemy(app) #initializing the database with the name 'db'
class PolygonCoordinates(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    preference_num=db.Column(db.Integer,nullable=False)
    x1=db.Column(db.Integer,nullable=False)
    y1=db.Column(db.Integer,nullable=False)
    x2=db.Column(db.Integer,nullable=False)
    y2=db.Column(db.Integer,nullable=False)
    x3=db.Column(db.Integer,nullable=False)
    y3=db.Column(db.Integer,nullable=False)
    x4=db.Column(db.Integer,nullable=False)
    y4=db.Column(db.Integer,nullable=False)
    createdAt=db.Column(db.DateTime,nullable=False)
    updatedAt=db.Column(db.DateTime,nullable=False)

    def __init__(self,preference_num,x1,y1,x2,y2,x3,y3,x4,y4,createdAt,updatedAt):
        self.preference_num=preference_num
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.x3=x3
        self.y3=y3
        self.x4=x4
        self.y4=y4
        self.createdAt=createdAt
        self.updatedAt=updatedAt
# ========== DB CONNECTION -- SQLALCHEMY (END) ===========


# ========== GETTER AND SETTER [COORDINATES] FUNCTION (START) ===========
'''Getting Coordinate from The Database'''

def getCoordinates():
    poly_coordinates={} #default value for polygon coordinates 
    with app.app_context(): # create a context for the database access
        # query for getting the last row of coordinates
        # Using ORM Approach
        result=PolygonCoordinates.query.filter_by(id=1).first()
        if result:
            #assigning the result to the global variable
            poly_coordinates['x1'] = result.x1
            poly_coordinates['y1'] = result.y1
            poly_coordinates['x2'] = result.x2
            poly_coordinates['y2'] = result.y2
            poly_coordinates['x3'] = result.x3
            poly_coordinates['y3'] = result.y3
            poly_coordinates['x4'] = result.x4
            poly_coordinates['y4'] = result.y4
        else:
            newPolyCoordinates = PolygonCoordinates(1,200,300,500,300,500,100,200,100,func.now(),func.now())
            db.session.add(newPolyCoordinates)
            db.session.commit()
            print("No data found, inserting default data...")
    return poly_coordinates


@app.route('/submit_coordinates',methods=['POST'])
def submitCoordinates():
    # get the hidden input form value from the html templates
    coordinates=request.form.get('coordinates')
    print(coordinates)
    # split the coordinates value into array
    coordinates=coordinates.split(' ')
    print ("received coordinates -> ",coordinates)
    # query for updating the coordinates value
    # ORM Approach for Update Coordinate
    updated_coordinates = {
        'x1': coordinates[0].split(',')[0],
        'y1': coordinates[0].split(',')[1],
        'x2': coordinates[1].split(',')[0],
        'y2': coordinates[1].split(',')[1],
        'x3': coordinates[2].split(',')[0],
        'y3': coordinates[2].split(',')[1],
        'x4': coordinates[3].split(',')[0],
        'y4': coordinates[3].split(',')[1]
    }
    with app.app_context(): # create a context for the database access
        PolygonCoordinates.query.filter_by(id=1).update(updated_coordinates)
        db.session.commit()
  
    return redirect('/')


# ========== GETTER AND SETTER [COORDINATES] FUNCTION (END) ===========

# ========== VIDEO STREAM (START) ===========
# cap = cv2.VideoCapture("rtsp://admin:admin123@id.labkom.us:3693/Streaming/Channels/201") #indoor office cctv
# cap = cv2.VideoCapture(2) #using webcam
cap = cv2.VideoCapture('rtsp://admin:admin123@192.168.22.176:554/Streaming/Channels/201') #using ip camera
# cap = cv2.VideoCapture('CCTV_Footage.mp4') #using webcam
tracker=Tracker()

people_list = {}
enter_list = {}
out_list = {}

colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]


# polygon zone preview
def annotatedStream():
    # temporarily stored here
    poly_zone=getCoordinates()
    polygon_zone=np.array([[poly_zone['x1'],poly_zone['y1']],
                        [poly_zone['x2'],poly_zone['y2']],
                        [poly_zone['x3'],poly_zone['y3']],
                        [poly_zone['x4'],poly_zone['y4']]],
                        np.int32)
    model = YOLO('yolov8n.pt')    
    while True:
        # reading frames from the video
        success, frame = cap.read()

        if not success:
            break
        else:
            # converting the collected frame to image
            frame=cv2.resize(frame,(640,480))
            results = model.predict(frame, classes=0)
            
            for result in results:
                detections = []
                for r in result.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = r
                    x1 = int(x1)
                    y1 = int(y1)
                    x2 = int(x2)
                    y2 = int(y2)
                    class_id = int(class_id)
                    detections.append([x1, y1, x2, y2, score])
                tracker.update(frame, detections)
                for track in tracker.tracks:
                    bbox = track.bbox
                    x1, y1, x2, y2 = bbox
                    x1 = int(x1)
                    y1 = int(y1)
                    x2 = int(x2)
                    y2 = int(y2)
                    track_id = track.track_id

                    # Line counter
                    m1 = (poly_zone['y2'] - poly_zone['y1'])/(poly_zone['x2'] - poly_zone['x1'])
                    b1 = poly_zone['y1'] - (poly_zone['x1']*m1)
                    result1 = y2 - ((m1*x2)+b1)

                    m2 = (poly_zone['y4'] - poly_zone['y3'])/(poly_zone['x4'] - poly_zone['x3'])
                    b2 = poly_zone['y3'] - (poly_zone['x3']*m2)
                    result2 = y2 - ((m2*x2)+b2)

                    if (result1 <= 3 and result1 >= 0) or (result1 >= (-3) and result1 <= 0)  :
                        if track_id not in out_list.keys():
                            enter_list[track_id] = [x2, y2]
                    
                    if (result2 <= 3 and result2 >= 0) or (result2 >= (-3) and result2 <= 0)  :
                        if track_id not in enter_list.keys():
                            out_list[track_id] = [x2, y2]

                    dist = cv2.pointPolygonTest(polygon_zone, (x2,y2), False)
                    if dist == 1 and (track_id in out_list.keys() or track_id in enter_list.keys()):
                        people_list[track_id] = y2
                    cv2.putText(frame, (str(track_id)),(x1,y1),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (colors[track_id % len(colors)]), 3)
            print('Enter : ', enter_list)
            print('Out : ', out_list)
            # annotate the frame using polygon
            
            frame=cv2.polylines(frame,[np.array(polygon_zone,np.int32)],True,(0,0,0),4,cv2.LINE_AA)
            cv2.line(frame,(poly_zone['x1'], poly_zone['y1']),(poly_zone['x2'], poly_zone['y2']),(0,255,0),2)
            


            cv2.line(frame,(poly_zone['x3'], poly_zone['y3']),(poly_zone['x4'], poly_zone['y4']),(0,0,255),2)
            cv2.putText(frame, ("Passed Threshold :"+str(len(people_list))),(20,100),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),2)
            cv2.putText(frame, ("Entered :"+str(len(enter_list))),(20,150),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),2)
            cv2.putText(frame, ("Out :"+str(len(out_list))),(20,200),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),2)
            cv2.putText(frame, ("In Room :"+str(len(enter_list)-len(out_list))),(20,250),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),2)
            buffer=cv2.imencode('.jpg',frame)[1] # change to index 1 to get the buffer
            frame=buffer.tobytes()# converting the image to bytes
            yield(b'--frame\r\n' # yielding the frame for display
                  b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n')
    


@app.route('/')
def landing_page():
    settings_coordinates=getCoordinates()
    # will render the index.html file present in templates folder
    return render_template('index.html',data=settings_coordinates)

@app.route('/video_feed')
def video_feed():
    return Response(annotatedStream(),mimetype='multipart/x-mixed-replace; boundary=frame')
# # socketio for listening disconnected client
# @socketio.on('disconnect')
# def destroy():
#     cap.release()
#     cv2.destroyAllWindows()
#     cursor.close()
#     mydb.close()
if __name__ == '__main__':
    app.run(debug=True)