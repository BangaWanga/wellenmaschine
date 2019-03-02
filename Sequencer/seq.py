import pygame
import pygame.midi
import random
from Sequencer.gui import Gui

from Sequencer.track import Track
from chesscam import ChessCam

class seq:
    def __init__(self, midiInDevice, midiOutDevice):
        self.midiIn = midiInDevice
        self.midiOut = midiOutDevice

        self.gui = Gui()

        # initialize state
        self.count = 0  # current step based on clock sync
        self.clockTicks = 0  # counter for received clock ticks
        self.running = True
        self.randomness = 0.

        self.track = Track()
        self.chesscam = ChessCam()  # TODO: operate camera in separate thread to update non-blockingly

        self.calibrateColor = -1

        self.resetButtonRect = pygame.Rect(200, 500, 100, 50)   # init rect of reset button
        self.notchDownButtonRect = pygame.Rect(100, 500, 50, 50)   # init rect of notch down button
        self.notchUpButtonRect = pygame.Rect(350, 500, 50, 50)   # init rect of noth up button

    def pygame_io(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:

                for fieldIndex in range(64):
                    if self.boardRects[fieldIndex].collidepoint(event.pos):
                        # if clicked and a calibration key was pressed before ("r", "g" or "b"), calibrate the color detection
                        if self.calibrateColor > -1:
                            self.chesscam.setRange(self.calibrateColor, fieldIndex % 8, fieldIndex // 8)
                            self.calibrateColor = -1
                        else:
                            # if clicked without prior calibration key, print out the colors in its area of interest
                            self.chesscam.printColors(fieldIndex % 8, fieldIndex // 8)
                        break  # if a field was found to be clicked, don't check the remaining ones

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.updateGrid = True
                if event.key == pygame.K_u:
                    self.updateSeq = True
                if event.key == pygame.K_r:
                    self.calibrateColor = 0
                if event.key == pygame.K_g:
                    self.calibrateColor = 1
                if event.key == pygame.K_b:
                    self.calibrateColor = 2
                if event.key == pygame.K_s:
                    self.chesscam.save_calibrated()
                if event.key == pygame.K_l:
                    self.chesscam.load_calibrated()                    
                if event.key == pygame.K_ESCAPE:  # abort color calibration with ESC
                    self.calibrateColor = -1
            if event.type == pygame.QUIT:
                self.running = False

    def play(self):
        velocity = 100

        # create timestamp for this step with an option of a random delay
        currentTimeInMs = pygame.midi.time()
        randomDelay = int(self.randomness*random.random())
        timestamp = currentTimeInMs + randomDelay

        # loop through the sequences and create the MIDI events of this step
        midiEvents = []  # collect them in this list, then send all at once
        for i, seq in enumerate(self.track.sequences):
            midiEvents.append([[0x80, 36 + i, 0], timestamp - 1])  # note off for all notes (note 36: C0). Reduce timestamp to make sure note off occurs before next note on.
            if seq[self.count] == 1:
                midiEvents.append([[0x90, 36 + i, velocity], timestamp])  # note on, if a 1 is set in the respective sequence

        self.midiOut.write(midiEvents)  # write the events to the MIDI output port

    def clock(self):
        for midiEvent in self.midiIn.read(5):  # read 5 MIDI events from the buffer. TODO: Good number?
            if (midiEvent[0][0]) == 248:
                self.clockTicks = (self.clockTicks + 1) % 12  # count the clock ticks
                if (self.clockTicks == 0):  # 12 clock ticks are one 16th note
                    self.clockTicks = 0  # reset the tick counter
                    self.count = (self.count + 1) % 16  # advance the 16th note counter

    def quit(self):
        self.midiOut.close()
        self.midiIn.close()
        self.chesscam.quit()
        pygame.quit()
