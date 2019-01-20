import cv2
import numpy as np


index = 0

while(True):
    # Capture frame-by-frame
    cap = cv2.VideoCapture(0)
    try:
        ret, frame = cap.read()


        # Display the resulting frame
        cv2.imshow('frame',frame)
        print(index)

    except:
        pass


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    #index += 1
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

