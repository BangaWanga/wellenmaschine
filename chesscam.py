import cv2
import numpy as np

class ChessCam:

    def __init__(self):
        self.grid = np.zeros((8, 8, 2), dtype=np.int)
        self.cap = cv2.VideoCapture(0)
        ret, self.frame = self.cap.read()
        self.frame = np.flip(self.frame, axis=1)
        self.frame = np.flip(self.frame, axis=2)

    def start(self):
        self.cap = cv2.VideoCapture(0)
        ret, self.frame = self.cap.read()

    def update(self):

        # Capture frame-by-frame
        ret, self.frame = self.cap.read()

        self.frame = np.flip(self.frame, axis = 1)
        self.frame = np.flip(self.frame, axis=2)


        #Corner the Harris
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        gray = np.float32(gray)
        gray = cv2.blur(gray, (20,20))


        ret, dst = cv2.threshold(gray, 0.5 * gray.max(), 255, 0)
        dst = np.uint8(dst)
        ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst, 4)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        blackLabels = []
        for label in range(len(centroids)):
            lblIndices = np.where(labels == label)
            if dst[lblIndices][0] == 0:
                blackLabels.append(label)

        centroids = np.delete(centroids, blackLabels, axis=0)

        #Sorting and rearranging centroidss
        #centroids = np.flip(centroids.astype(np.int), axis=1)
        centroids = centroids[np.argsort(centroids[:,1])]
        try:
            self.make_grid(centroids)
            # Write coordinates to the screen
            for i in range(8):
                for j in range(8):
                    cv2.putText(dst, "({0}, {1})".format(i, j), tuple(self.grid[i, j]), fontScale=0.2,
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                color=(255, 255, 255))
        except:
            pass
            #print('fuck this shit')

        # Display the resulting frame
        cv2.imshow('frame', dst)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    def make_grid(self, centroids):
        #We assume that the field at the upper left corner is white
        #That means we should have 32 centroids in total (only for white fields)
        self.grid = np.zeros((8,8,2))
        for i in range(8):
            isodd = i%2
            white_fields = centroids[i*4:i*4+4]
            white_fields= white_fields[np.argsort(white_fields[:, 0])]
            for j in range(4):
                self.grid[j * 2 + isodd , i] =white_fields[j]

        # Calculate black field coordinates
        for i in range(8):
            isodd = i%2
            if isodd:
                for j in range(1,4):
                    self.grid[2 * j, i] = (self.grid[2 * j - 1, i] + self.grid[2 * j + 1, i]) / 2.
                self.grid[0, i] = self.grid[1, i] - (self.grid[2, i] - self.grid[1, i])
            else:
                for j in range(3):
                    self.grid[2 * j + 1, i] = (self.grid[2 * j, i] + self.grid[2 * j + 2, i]) / 2.
                self.grid[7, i] = self.grid[6, i] + (self.grid[6, i] - self.grid[5, i])

        self.grid = self.grid.astype(np.int)



    def gridToState(self):
        tolerance = 80

        self.grid = self.grid.astype(np.int)
        states = np.zeros(self.grid.shape[:2], dtype=np.int)
        for i in range(8):
            for j in range(8):
                try:
                    currColor = self.frame[self.grid[j, i, 1], self.grid[j, i, 0]]
                    if (currColor[0] > 255 - tolerance) and (currColor[1] < tolerance) and (currColor[2] < tolerance):
                        state = 1
                    elif (currColor[0] < tolerance) and (currColor[1] > 255 - tolerance) and (currColor[2] < tolerance):
                        state = 2
                    elif (currColor[0] < tolerance) and (currColor[1] < tolerance) and (currColor[2] > 255 - tolerance):
                        state = 3
                    else:
                        state = 0
                    states[j, i] = state
                except:
                    pass
        seq1 = np.concatenate( (states[:,0], states[:,1])  )
        seq2 = np.concatenate( (states[:,2], states[:,3])  )
        seq3 = np.concatenate( (states[:,4], states[:,5])  )
        seq4 = np.concatenate( (states[:,6], states[:,7])  )
        return (seq1, seq2, seq3, seq4)



    def quit(self):
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

