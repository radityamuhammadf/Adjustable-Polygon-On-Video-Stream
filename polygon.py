import cv2
import numpy as np

def printCoordinate(event, x, y,flags, params):
  if event == cv2.EVENT_LBUTTONDOWN:
    # draw circle dots
    cv2.circle(
      img,
      (x,y), # coordinates cursor point
      3, # radius (large)
      (255,255,255),
      -1 # line thickness
    )

    # add coordinates cursor point
    area.append((x,y))

    # set the annotation coordinates clicked
    strXY = '(' + str(x) + ',' + str(y) + ')'
    fontXY = cv2.FONT_HERSHEY_PLAIN
    cv2.putText(img,strXY,(x+10,y-10),fontXY,1,(255,255,255))

    if len(area) >= 2: # clicked 2 points
      cv2.line(img,area[-1],area[-2],(0,0,255),3,cv2.LINE_AA) # AA = Anti Aliase
      if len(area) == 4: # clicked 4 points then draw polygons area
        cv2.polylines(img,[np.array(area,np.int32)],True,(0,0,255),4,cv2.LINE_AA)
        area.clear()

    print(area)
    cv2.imshow("image", img)

img = np.zeros( # initiate array with 0 values
  (700,800,3), # shape (height, width, color RGB)
  dtype=np.uint8
)
cv2.imshow("image", img) # (window name, declared window)

area = [] # coordinate points of area container

cv2.setMouseCallback("image", printCoordinate) # set callback function when mouse interact with "image" window

cv2.waitKey()
cv2.destroyAllWindows()