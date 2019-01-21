import cv2
import numpy as np

class ChessCam:

    def __init__(self):
        self.grid = np.zeros((8, 8, 2), dtype=np.int)
        self.cap = cv2.VideoCapture(0)
        ret, self.frame = self.cap.read()
        self.frame = np.flip(self.frame, axis=1)
        self.frame = np.flip(self.frame, axis=2)

        # define color boundaries (lower, upper) (in RGB, since we always flip the frame)
        self.colorBoundaries = [
            (np.array([100, 15, 17]), np.array([200, 56, 50])), # red
            (np.array([4, 86, 31]), np.array([50, 220, 88])),   # green
            (np.array([4, 31, 86]), np.array([50, 88, 220]))    # blue
        ]
        self.states = np.zeros(self.grid.shape[:2], dtype=np.int)   # array that holds a persistent state of the chessboard

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
        # tolerance = 80
        aoiHalfWidth = 5  # half width in pixels of the area of interest around the centroids

        self.grid = self.grid.astype(np.int)
        # states = np.zeros(self.grid.shape[:2], dtype=np.int)
        for i in range(8):
            for j in range(8):
                try:
                    state = 0  # initially, state is Off
                    # now loop through the colors to see if there is a significant amount of any
                    for colorNum, (lower, upper) in enumerate(self.colorBoundaries):
                        areaOfInterest = self.frame[self.grid[j, i, 1]-aoiHalfWidth:self.grid[j, i, 1]+aoiHalfWidth, self.grid[j, i, 0]-aoiHalfWidth:self.grid[j, i, 0]+aoiHalfWidth]
                        mask = cv2.inRange(areaOfInterest, lower, upper)  # returns binary mask: pixels which fall in the range are white (255), others black (0)
                        if np.mean(mask) > 100:  # if some significant amount of pixels in the mask is 255, we consider it colored
                            state = colorNum + 1  # +1 because colorNum is zero-based, but state zero is Off
                    self.states[j, i] = state

                    # currColor = self.frame[self.grid[j, i, 1], self.grid[j, i, 0]]
                    # if (currColor[0] > 255 - tolerance) and (currColor[1] < tolerance) and (currColor[2] < tolerance):
                    #     state = 1
                    # elif (currColor[0] < tolerance) and (currColor[1] > 255 - tolerance) and (currColor[2] < tolerance):
                    #     state = 2
                    # elif (currColor[0] < tolerance) and (currColor[1] < tolerance) and (currColor[2] > 255 - tolerance):
                    #     state = 3
                    # else:
                    #     state = 0
                    # states[j, i] = state
                except:
                    pass

        # dissect the board into the four 16-step sequences (two rows for each sequence of 16 steps)
        seq1 = np.concatenate((self.states[:,0], self.states[:,1]))
        seq2 = np.concatenate((self.states[:,2], self.states[:,3]))
        seq3 = np.concatenate((self.states[:,4], self.states[:,5]))
        seq4 = np.concatenate((self.states[:,6], self.states[:,7]))
        return (seq1, seq2, seq3, seq4)



    def quit(self):
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

