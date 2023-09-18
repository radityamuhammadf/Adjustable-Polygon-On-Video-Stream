# importing the Computer Vision module
import cv2

def stream():
    # capturing the video from webcam
    cap = cv2.VideoCapture(0)

    # running infinite loop
    while True:
        # reading frames from the video
        ret, frame = cap.read()

        frame=cv2.resize(frame,(640,480))
        # displaying the video
        cv2.imshow('frame', frame)

        # exiting the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # closing the stream
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    stream()
