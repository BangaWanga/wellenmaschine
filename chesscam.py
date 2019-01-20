import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame


    ret, frame = cap.read()

    #Corner the Harris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    gray = cv2.blur(gray, (20,20))


    ret, dst = cv2.threshold(gray, 0.8 * gray.max(), 255, 0)
    dst = np.uint8(dst)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst, 4)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    #Sorting centroidss
    centroids = np.flip(centroids.astype(np.int), axis=1).sort(2)
    centroids = centroids.sort(1)
    print(centroids)
    break
    # Display the resulting frame
    cv2.imshow('frame',dst)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

