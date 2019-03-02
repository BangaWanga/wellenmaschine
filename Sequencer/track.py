import numpy as np

class Track:
    # TODO: Try variations like patterns with different lengths (maybe on smaller raster)
    def __init__(self):
        #self.kick = [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]
        #self.hh = [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
        #self.snare = [1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0]

        # We have 12 sequences with 16 steps each
        self.sequences = np.zeros((12, 16), dtype=np.int)
        # self.sequences[0, 0] = 1
        # self.sequences[1, 4] = 1

    def update(self, sequences):
        self.sequences = np.zeros((12, 16), dtype=np.int)
        for i, seq in enumerate(sequences):
            for j, val in enumerate(seq):
                if val:  # if the val is not zero
                    # The encoding works like this:
                    # The sequences 0 to 2 belong to the first two rows on the chessboard.
                    # The sequences 3 to 5 belong to the third and fourth row on the chessboard.
                    # ...
                    # The vals range from 0 to 3: 0 is off, 1 to 3 (red, green, blue) are the sub-voices
                    self.sequences[3*i + val - 1, j] = 1
        #if (np.any(sequences)):
         #   print(self.sequences)