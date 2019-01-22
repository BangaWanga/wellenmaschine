import pygame
import pygame.midi
import time
# from threading import Thread
from track import Track
import random
from chesscam import ChessCam

class Sequencer:
    def __init__(self):
        pygame.init()
        pygame.midi.init()

        self.midiOut = self.ask_for_midi_device(kind="output")  # prompt the user to choose MIDI input ...
        self.midiIn = self.ask_for_midi_device(kind="input")    # ... and output device

        # initialize state
        self.count = 0  # current step based on clock sync
        self.clockTicks = 0  # counter for received clock ticks
        self.running = True
        self.randomness = 0.

        self.track = Track()
        self.chesscam = ChessCam()

        self.updateGrid = False
        self.updateSeq = False
        self.calibrateColor = -1

        # initialize window geometry
        self.initBoardRects(left=50, top=50, width=400)     # init chessboard
        self.resetButtonRect = pygame.Rect(200, 500, 100, 50)   # init rect of reset button
        self.notchDownButtonRect = pygame.Rect(100, 500, 50, 50)   # init rect of notch down button
        self.notchUpButtonRect = pygame.Rect(350, 500, 50, 50)   # init rect of noth up button

    def run(self):
        # initialize the pygame screen
        (width, height) = (500, 600)
        screen = pygame.display.set_mode((width, height))
        screen.fill((255, 255, 255))
        
        currentStep = 0
        while self.running:
            self.pygame_io()
            self.clock()
            self.chesscam.update(self.updateGrid)
            if self.updateGrid == True:
                self.updateGrid = False
            if self.updateSeq:
                self.track.update(self.chesscam.gridToState())
                self.updateSeq = False
            if currentStep != self.count:
                self.play()
                currentStep = (currentStep + 1) % 16

            # draw the window
            self.drawBoard(screen)
            self.drawButtons(screen)
            pygame.display.flip()

        self.quit()


    def ask_for_midi_device(self, kind="input"):
        """ Let the user choose the midi device to use """
        # Check, if we are looking for a valid kind:
        assert (kind in ("input", "output")), "Invalid MIDI device kind: {0}".format(kind)

        is_input = (kind == "input")
        # First, print info about the available devices:
        print()
        print("Available MIDI {0} devices:".format(kind))
        device_ids = []  # list to hold all available device IDs
        device_id = 0
        info_tuple = ()
        # print info about all the devices
        while not pygame.midi.get_device_info(device_id) is None:
            info_tuple = pygame.midi.get_device_info(device_id)
            if info_tuple[2] == is_input:  # this holds 1 if device is an input device, 0 if not
                print("ID: {0}\t{1}\t{2}".format(device_id, info_tuple[0], info_tuple[1]))
                device_ids.append(device_id)
            device_id += 1
        assert (device_id > 0), "No {0} devices found!".format(kind)

        user_input_id = -1
        while not user_input_id in device_ids:  # ask for the desired device ID until one of the available ones is given
            user_input = input("Which device would you like to use as {0}? Please provide its ID: ".format(kind))
            try:  # try to cast the user input into an int
                user_input_id = int(user_input)
            except ValueError:  # if it fails because of incompatible input, let them try again
                pass
        info_tuple = pygame.midi.get_device_info(user_input_id)
        print("Chosen {0} device: ID: {1}\t".format(kind, user_input_id) + str(info_tuple[0]) + "\t" + str(info_tuple[1]))
        # Open port from chosen device
        if kind == "input":
            return pygame.midi.Input(device_id=user_input_id)
        elif kind == "output":
            return pygame.midi.Output(device_id=user_input_id, latency=0)

    def pygame_io(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                # check if one of the buttons was clicked
                if self.resetButtonRect.collidepoint(event.pos):
                    self.clockTicks = 0
                if self.notchDownButtonRect.collidepoint(event.pos):
                    self.clockTicks = (self.clockTicks - 1) % 12
                if self.notchUpButtonRect.collidepoint(event.pos):
                    self.clockTicks = (self.clockTicks + 1) % 12
                # check if one of the board fields was clicked
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
            if event.type == pygame.QUIT:
                self.running = False

    def play(self):
        #print(self.count)
        velocity = 100

        # create timestamp for this step with an option of a random delay
        currentTimeInMs = pygame.midi.time()
        randomDelay = int(self.randomness*random.random())
        timestamp = currentTimeInMs + randomDelay

        # loop through the sequences and create the MIDI events of this step
        midiEvents = []  # collect them in this list, then send all at once
        for i, seq in enumerate(self.track.sequences):
            midiEvents.append([[0x80, 36 + i, 0], timestamp - 1])  # note off for all notes (note 36: C0). Reduce timestamp to make sure note off occurs before next note on.
            #self.midiOut.note_off(36 + i)
            #time.sleep(random.random()*0.1)
            if seq[self.count] == 1:
                midiEvents.append([[0x90, 36 + i, velocity], timestamp])  # note on, if a 1 is set in the respective sequence
                # self.midiOut.note_on(36 + i, velocity)

        self.midiOut.write(midiEvents)  # write the events to the MIDI output port

    # def midi_note(self, duration =.01
    #     ,note = 36
    #     ,velocity = 100):
    #     self.midiOut.note_on(note, velocity)
    #     time.sleep(duration)
    #     self.midiOut.note_off(note, velocity)

    def quit(self):
        self.midiOut.close()
        self.midiIn.close()
        self.chesscam.quit()
        pygame.quit()

    def clock(self):
        for midiEvent in self.midiIn.read(5):  # read 5 MIDI events from the buffer. TODO: Good number?
            if (midiEvent[0][0]) == 248:
                self.clockTicks = (self.clockTicks + 1) % 12  # count the clock ticks
                if (self.clockTicks == 0):  # 12 clock ticks are one 16th note
                    self.clockTicks = 0  # reset the tick counter
                    self.count = (self.count + 1) % 16  # advance the 16th note counter

    def initBoardRects(self, left, top, width):
        rectWidth = int(width/8.)
        self.boardRects = []
        for yIndex in range(8):
            for xIndex in range(8):
                self.boardRects.append(pygame.Rect((left + xIndex*rectWidth, left + yIndex*rectWidth, rectWidth, rectWidth)))

    def drawBoard(self, screen):
        """ Method for optionally drawing the current state of the sequencer """

        # below, draw a light green where the current step is (blit this surface there)
        currentStepSurf = pygame.Surface((self.boardRects[0].width, self.boardRects[0].width))
        currentStepSurf.set_alpha(100)
        currentStepSurf.fill((0, 255, 0))

        # loop through the chessboard fields (stored in self.boardRects list, row-wise)
        for i, currentRect in enumerate(self.boardRects):
            # Check if the corresponding sequence has a 1 for the current field
            isRed = self.track.sequences[3*(i // 16), i % 16]
            isGreen = self.track.sequences[3*(i // 16) + 1, i % 16]
            isBlue = self.track.sequences[3*(i // 16) + 2, i % 16]
            
            if isRed or isGreen or isBlue:
                pygame.draw.rect(screen, (isRed*255, isGreen*255, isBlue*255), currentRect)
            else:  # if not set, just draw black or white chessboard-style
                isWhite = ((i + (i//8)%2) % 2 == 0)
                pygame.draw.rect(screen, (isWhite*255, isWhite*255, isWhite*255), currentRect)

            # draw a light green where the current step is
            if i % 16 == self.count:
                screen.blit(currentStepSurf, currentRect)

    def drawButtons(self, screen):
        bgcol = (90,155,255)
        
        # draw reset (or 'tap' button)
        pygame.draw.rect(screen, bgcol, self.resetButtonRect)
        # draw label
        font = pygame.font.SysFont('Times New Roman', 20)
        text_surface = font.render('Tap Beat', True, (255, 255, 255, 255), bgcol)
        textrect = text_surface.get_rect()
        textrect.centerx = self.resetButtonRect.x + self.resetButtonRect.width/2
        textrect.centery = self.resetButtonRect.y + 0.9*self.resetButtonRect.height/2
        screen.blit(text_surface, textrect)

        # draw notch down button
        pygame.draw.rect(screen, bgcol, self.notchDownButtonRect)
        # draw label
        font = pygame.font.SysFont('Times New Roman', 20)
        text_surface = font.render('<<', True, (255, 255, 255, 255), bgcol)
        textrect = text_surface.get_rect()
        textrect.centerx = self.notchDownButtonRect.x + self.notchDownButtonRect.width/2
        textrect.centery = self.notchDownButtonRect.y + self.notchDownButtonRect.height/2
        screen.blit(text_surface, textrect)

        # draw notch up button
        pygame.draw.rect(screen, bgcol, self.notchUpButtonRect)
        # draw label
        font = pygame.font.SysFont('Times New Roman', 20)
        text_surface = font.render('>>', True, (255, 255, 255, 255), bgcol)
        textrect = text_surface.get_rect()
        textrect.centerx = self.notchUpButtonRect.x + self.notchUpButtonRect.width/2
        textrect.centery = self.notchUpButtonRect.y + self.notchUpButtonRect.height/2
        screen.blit(text_surface, textrect)

if __name__=="__main__":
    sequencer = Sequencer()
    sequencer.run()
