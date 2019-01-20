import pygame
import pygame.midi
import time
from threading import Thread
from track import *
class midi:
    def __init__(self):
        pygame.midi.init()
        #self.midiOut.set_instrument(10)
        print(pygame.midi.get_default_input_id())
        for i in range(pygame.midi.get_count()):
            print(pygame.midi.get_device_info(i))
        self.midiOut = pygame.midi.Output(7, 0)
        self.midiIn = pygame.midi.Input(3)
        self.count = 0  # Beats played
        self.clockc = 0  # Beats played
        self.playing=False
        self.running=True
        self.track = track()

        ##SCREEN

        (width, height) = (300, 200)
        screen = pygame.display.set_mode((width, height))
        screen.fill((255, 255, 255))  #
        pygame.draw.rect(screen, (90,155,255), (200, 150, 100, 50))
        pygame.display.flip()


        sechzehntel =0
        while self.running:
            self.pygame_io()
            self.clock()
            if sechzehntel < self.count or sechzehntel ==15 and self.count ==0:
                self.play()
                sechzehntel = (sechzehntel+1)%16
            # if self.playing:
            #     print("Woop")
            #     t1 = Thread(target=self.play(0.1))
            #     t1.start()

    def pygame_io(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                if (200<=x<=300 and 150<=y<=200):
                    self.clockc = 0
            if event.type == pygame.QUIT:
                self.running = False
                return


    #note 36 = C0
    def play(self):
        print(self.count)


        if self.track.kick[self.count]==1:
            Thread(target=self.midi_note()).start()
        elif self.track.snare[self.count]==1:
            Thread(target=self.midi_note(note=37)).start()
        elif self.track.hh[self.count]==1:
            Thread(target=self.midi_note(note=38)).start()
    def midi_note(self, duration =.01
        ,note = 36
        ,velocity = 100):
        self.midiOut.note_on(note, velocity)
        time.sleep(duration)
        self.midiOut.note_off(note, velocity)

    def quit(self):
        self.midiOut.close()
        self.midiIn.close()

    def clock(self):
        for info in self.midiIn.read(5):
            if (info[0][0]) == 248:
                print(info)

                self.clockc +=1

                if (self.clockc>=6):
                    self.clockc = 0
                    self.count+=1
                    if (self.playing==False):
                        self.playing=True

                if self.count >15:
                    self.count=0
            else:
                pass




if __name__=="__main__":
    midi = midi()
    time.sleep(1)

    midi.clock()
    midi.quit()
    print(midi.count)
    print(midi.clockc)
