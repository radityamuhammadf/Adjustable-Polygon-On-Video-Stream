# importing the Computer Vision module
import cv2
from flask import Flask,Response,render_template
import mysql.connector
import numpy as np

app=Flask(__name__,static_url_path='/static')

# ========== DB CONNECTION (START) ===========

# Will check if there's database named Enpemo exist on those server (server isn't it?)
def checkDatabaseExistance(database_name):
    check_db_query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database_name}' " #sql query for checking if database named on 'database_name' variable is exist
    cursor.execute(check_db_query)
    result = cursor.fetchone()
    return result is not None

# Create a database 
def createDatabase(database_name):
    create_database_query = f"CREATE DATABASE {database_name}"#sql query for creating database named on 'database_name' variable
    cursor.execute(create_database_query)
    print(f"The database '{database_name}' has been created.")

# Function to execute the SQL Query which will be creating a new table if there's no table  
def createTableIfNotExist(table_name):
    # query for automatically checking and creating a table
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `preference_num` INT NOT NULL,
            `x1` INT NOT NULL,
            `y1` INT NOT NULL,
            `x2` INT NOT NULL,
            `y2` INT NOT NULL,
            `x3` INT NOT NULL,
            `y3` INT NOT NULL,
            `x4` INT NOT NULL,
            `y4` INT NOT NULL,
            `createdAt` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updatedAt` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=3;
    """
    cursor.execute(create_table_query)

def checkTableExistence(table_name):
    check_table_query = f"SHOW TABLES LIKE '{table_name}'" #sql query for searching table name
    cursor.execute(check_table_query) 
    result = cursor.fetchone() #fetch the search result -> 
    return result is not None #if the search result is not empty result, it'll returning not None value  

# Initiate connection to MySQL server
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password=''
)
# Instantiate cursor class for executing SQL commands
cursor = mydb.cursor()
database_name = "enpemo"
coordinates_db = "polygon_coordinates"
# Global Logic -- Checking database existence then creating a database if there's no database found in the server
if not checkDatabaseExistance(database_name):
    createDatabase(database_name)
# Select the 'enpemo' database
cursor.execute(f"USE {database_name}")
createTableIfNotExist(coordinates_db)
# ========== DB CONNECTION (END) ===========

cap = cv2.VideoCapture(0) #using webcam
# cap = cv2.VideoCapture('http://id.labkom.us:9357/') #using ip camera
# cap = cv2.VideoCapture('People.mp4') #using video footage for testing
def stream():

    # running infinite loop
    while True:
        # reading frames from the video
        success, frame = cap.read()

        if not success:
            break
        else:
            # converting the collected frame to image
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=cv2.resize(frame,(640,480))
            frame=buffer.tobytes()# converting the image to bytes
            yield(b'--frame\r\n' # yielding the frame for display
                  b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n')
            
# ========== VIDEO STREAM (END) ===========
# polygon zone preview
polygon_zone=np.array([[200,300],[500,300],
                        [500,100],[200,100]],np.int32)
def annotatedStream():
    while True:
        # reading frames from the video
        success, frame = cap.read()

        if not success:
            break
        else:
            # converting the collected frame to image
            frame=cv2.resize(frame,(640,480))
            # annotate the frame using polygon
            frame=cv2.polylines(frame,[np.array(polygon_zone,np.int32)],True,(0,0,255),4,cv2.LINE_AA)
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()# converting the image to bytes
            yield(b'--frame\r\n' # yielding the frame for display
                  b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n')



if __name__ == '__main__':
    stream()
    app.run(debug=True)

@app.route('/')
def hello_world():
    # will render the index.html file present in templates folder
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(annotatedStream(),mimetype='multipart/x-mixed-replace; boundary=frame')