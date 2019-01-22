import numpy as np
import pyaudio
import pygame
import scipy.signal as signal

class Oscilloscope:

	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
		self.width = self.screen.get_width()
		self.height = self.screen.get_height()
		print("Screen size:", (self.width, self.height))
		self.xs = np.arange(0, self.width, dtype=np.int)
		self.angles = np.linspace(0, 2*np.pi, self.width)
		self.radius = 300
		self.yBuffer = np.zeros(self.width)
		self.bufferPos = 0
		self.triggered = False
		self.triggerThresh = 20.
		self.triggerSlopeThresh = 10.

		self.b, self.a = signal.butter(4, 0.5, 'lowpass')

		self.running = False
		self.p = pyaudio.PyAudio()

		self.stream = self.p.open(format=pyaudio.paFloat32,  # it is very important to always feed samples in the format specified here to this stream, can otherwise lead to distorted sound
                    channels=1,                             # mono
                    rate=16*19200,
                    input=True,
                    input_device_index=1,
                    frames_per_buffer=64,
                    stream_callback=self.draw)

	def run(self):
		self.running = True
		self.stream.start_stream()

		while self.running:
			for event in pygame.event.get():  # take all pygame events out of the event queue
				# look for the QUIT key "q"
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						self.running = False
		self.stop()

	def stop(self):
		self.stream.stop_stream()

	def draw(self, in_data, frame_count, time_info, status):
		# print(len(in_data))
		# print(self.bufferPos)

		if self.bufferPos < self.width:
			newStuff = 255.*np.fromstring(in_data, dtype=np.float32)
			newStuff = signal.filtfilt(self.b, self.a, newStuff)
			# newStuff = newStuff[::2]
			if (not self.triggered) and np.any(newStuff > self.triggerThresh) and (newStuff[-1]-newStuff[0]) > self.triggerSlopeThresh:
				self.bufferPos = 0
				self.triggered = True
			len_left = self.width - self.bufferPos
			advance = min(len(newStuff), len_left)
			self.yBuffer[self.bufferPos:self.bufferPos+advance] = newStuff[:advance]
			self.bufferPos += advance
		else:
			# draw the new oscillogram
			self.screen.fill((0, 0, 0))
			# linear
			# pointlist = [[self.xs[i], int(self.height/2. - self.yBuffer[i])] for i in range(self.width)]
			# circular
			xs = self.width/2 + (self.radius + self.yBuffer)*np.cos(self.angles)
			ys = self.height/2 + (self.radius + self.yBuffer)*np.sin(self.angles)
			pointlist = [[int(xs[i]), int(ys[i])] for i in range(self.width)]
			pointlist.append(pointlist[0])  # close the shape for circular plot
			if self.triggered:
				lineColor = (255, 0, 0)
			else:
				lineColor = (255, 255, 255)
			pygame.draw.lines(self.screen, lineColor, False, pointlist)
			self.bufferPos = 0
			self.triggered = False

			pygame.display.flip()

		return (None, pyaudio.paContinue)

if __name__ == "__main__":
	oszi = Oscilloscope()
	oszi.run()