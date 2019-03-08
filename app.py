import pygame
import pygame.midi
from midilib import utils

from Sequencer.seq import seq

class App:
    def __init__(self):
        pygame.init()
        pygame.midi.init()

        # TODO: move default_value to user config
        midiOut = utils.ask_for_midi_device(kind="output",default_value=10)  # prompt the user to choose MIDI input ...
        midiIn = utils.ask_for_midi_device(kind="input",default_value=1)  # ... and output device

        self.sequnecer = seq(midiIn, midiOut)

        self.running = True
        self.updateGrid = False
        self.updateSeq = False

    def run(self):
        currentStep = 0
        while self.running:
            self.sequnecer.pygame_io()
            self.sequnecer.clock()
            self.sequnecer.chesscam.update(self.updateGrid)
            if self.updateGrid == True:
                self.updateGrid = False
            if self.updateSeq:
                self.sequnecer.track.update(self.sequnecer.chesscam.gridToState())
                self.updateSeq = False
            if currentStep != self.sequnecer.count:
                self.sequnecer.play()
                currentStep = (currentStep + 1) % 16
        self.sequnecer.quit()


if __name__=="__main__":
    app = App()
    app.run()