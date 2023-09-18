# importing the Computer Vision module
import cv2
from flask import Flask,Response,render_template

app=Flask(__name__,static_url_path='/static')

# capturing the video from webcam
cap = cv2.VideoCapture(0)

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


if __name__ == '__main__':
    stream()
    app.run(debug=True)

@app.route('/')
def hello_world():
    # will render the index.html file present in templates folder
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(stream(),mimetype='multipart/x-mixed-replace; boundary=frame')