import pygame
import pygame.midi
from midilib import utils

from Sequencer.seq import seq

class App:
    def __init__(self):
        pygame.init()
        pygame.midi.init()

        midiOut = utils.ask_for_midi_device(kind="output")  # prompt the user to choose MIDI input ...
        midiIn = utils.ask_for_midi_device(kind="input")  # ... and output device

        self.sequnecer = seq(midiIn, midiOut)

    def run(self):
        self.sequnecer.run()


if __name__=="__main__":
    app = App()
    app.run()