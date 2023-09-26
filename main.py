# importing the Computer Vision module
import cv2
from flask import Flask,Response,render_template,request,redirect
import mysql.connector
import numpy as np

app=Flask(__name__,static_url_path='/static')

# ========== DB CONNECTION (START) ===========

# Will check if there's database named Enpemo exist on those server (server isn't it?)
def checkDatabaseExistance(database_name):
    check_db_query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database_name}';" #sql query for checking if database named on 'database_name' variable is exist
    cursor.execute(check_db_query)
    result = cursor.fetchone()
    return result is not None

# Create a database 
def createDatabase(database_name):
    create_database_query = f"CREATE DATABASE {database_name};"#sql query for creating database named on 'database_name' variable
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(create_table_query)

def checkTableExistence(table_name):
    check_table_query = f"SHOW TABLES LIKE '{table_name}';" #sql query for searching table name
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
cursor = mydb.cursor(buffered=True)
database_name = "enpemo"
coordinates_db = "polygon_coordinates"
# Global Logic -- Checking database existence then creating a database if there's no database found in the server
if not checkDatabaseExistance(database_name):
    createDatabase(database_name)
# Select the 'enpemo' database
cursor.execute(f"USE {database_name}")
createTableIfNotExist(coordinates_db)
# ========== DB CONNECTION (END) ===========

# ========== GETTER AND SETTER [COORDINATES] FUNCTION (START) ===========

'''Getting Coordinate from The Database'''
def getCoordinates():
    poly_coordinates={} #default value for polygon coordinates 
    # query for getting the last row of coordinates
    try:
        # get_coordinates_query = f"SELECT * FROM {coordinates_db} WHERE preference_num = 2 LIMIT 0,1;"
        get_coordinates_query = f"SELECT * FROM {coordinates_db} WHERE preference_num = 2;"
        cursor.execute(get_coordinates_query)
        result = cursor.fetchone()
        if result:
            #assigning the result to the global variable
            poly_coordinates['x1'] = result[2]
            poly_coordinates['y1'] = result[3]
            poly_coordinates['x2'] = result[4]
            poly_coordinates['y2'] = result[5]
            poly_coordinates['x3'] = result[6]
            poly_coordinates['y3'] = result[7]
            poly_coordinates['x4'] = result[8]
            poly_coordinates['y4'] = result[9]
        else:
            insert_coordinates_query = f"INSERT INTO {coordinates_db} (preference_num,x1,y1,x2,y2,x3,y3,x4,y4) VALUES (2,200,300,500,300,500,100,200,100);"
            cursor.execute(insert_coordinates_query)
            get_coordinates_query = f"SELECT * FROM {coordinates_db} WHERE preference_num = 2;"
            cursor.execute(get_coordinates_query)
            result = cursor.fetchone() 
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")

    return poly_coordinates

@app.route('/submit_coordinates',methods=['POST'])
def submitCoordinates():
    # get the hidden input form value from the html templates
    
    coordinates=request.form.get('coordinates')
    print ("received coordinates -> ",coordinates)
    # split the coordinates value into array
    coordinates=coordinates.split(' ')
    # query for updating the coordinates value
    update_coordinates_query = f"UPDATE polygon_coordinates SET x1={coordinates[0]},y1={coordinates[1]},x2={coordinates[2]},y2={coordinates[3]},x3={coordinates[4]},y3={coordinates[5]},x4={coordinates[6]},y4={coordinates[7]} WHERE preference_num=2;"
    # cursor.execute(update_coordinates_query,multi=True)
    cursor.execute(update_coordinates_query)
    mydb.commit()
    return redirect('/')


# ========== GETTER AND SETTER [COORDINATES] FUNCTION (END) ===========

# ========== VIDEO STREAM (START) ===========
cap = cv2.VideoCapture(0) #using webcam
# cap = cv2.VideoCapture('rtsp://admin:admin@id.labkom.us:6643/Streaming/Channels/101') #using ip camera
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

def annotatedStream():
    # temporarily stored here
    while True:
        poly_zone=getCoordinates()
        polygon_zone=np.array([[poly_zone['x1'],poly_zone['y1']],
                            [poly_zone['x2'],poly_zone['y2']],
                            [poly_zone['x3'],poly_zone['y3']],
                            [poly_zone['x4'],poly_zone['y4']]],
                            np.int32)    
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
    settings_coordinates=getCoordinates()
    # will render the index.html file present in templates folder
    return render_template('index.html',data=settings_coordinates)

@app.route('/video_feed')
def video_feed():
    return Response(annotatedStream(),mimetype='multipart/x-mixed-replace; boundary=frame')