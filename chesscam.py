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
    #dst = cv2.cornerHarris(gray, 2, 25, 0.04)

    #Paint red dots on corners
    #frame[dst > 0.05 * dst.max()] = [0, 0, 255]


    ret, dst = cv2.threshold(gray, 0.8 * gray.max(), 255, 0)
    dst = np.uint8(dst)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst, 4)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    #corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria).astype(np.int)
    #corners = np.flip(corners, axis=1)
    try:
        centroids = np.flip(centroids.astype(np.int), axis=1)
        dst[:,:] = labels[:,:]
        for i in centroids:
            dst[i[0],i[1]] = 255
        print('yo')
    except:
        raise
    for i in centroids:
        print(i)


    # Display the resulting frame
    cv2.imshow('frame',dst)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()







#frame[dst > 0.01 * dst.max()] = [0, 0, 255]
    # edges = np.where(dst > 0.01 * dst.max())
    # edges = list(zip(edges[0], edges[1]))
    # print (edges)
