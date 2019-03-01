import pygame
import pygame.midi

from Sequencer.midiAndSeqAndGFX_APP import Sequencer

def run_app():
    pygame.init()
    pygame.midi.init()

    sequnecer = Sequencer()
    sequnecer.run()


if __name__=="__main__":
    run_app()