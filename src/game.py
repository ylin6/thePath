# Gerard Martinez, Marshal Sprigg, and Yucheng Lin
import sys
import os
import math
import pygame
from pygame.locals import *

# Starting X and Y Variables
START_X = 100
START_Y = 100

# Flashlight class. Will Follow User Sprite.

class Light():
	def __init__(self, size):
		# Black Mask
		self.mask = pygame.surface.Surface(size).convert_alpha()
		# Light Mask
		self.light_radius = 100
		self.light_mask = pygame.surface.Surface((self.light_radius, self.light_radius)).convert_alpha()

		self.y = START_Y
		self.x = START_X
		
	def drawCircle(self):
		self.mask.fill((0,0,0,255))
		radius = 100
		t = 200
		delta = 3
		while radius > 50:
			pygame.draw.circle(self.mask, (0,0,0,t), (self.x, self.y), radius)
			t -= delta
			radius -= delta
		#pygame.draw.circle(self.mask, (0,0,0,95), (self.x, self.y), radius)
	def tick(self):
		print "tick"
	def move(self, key):
		if key == K_RIGHT:
			self.x +=5
			self.drawCircle()
		elif key == K_LEFT:
                        self.x -= 5
                        self.drawCircle()
		elif key == K_UP:
                        self.y -= 5
                        self.drawCircle()
		elif key == K_DOWN:
                        self.y += 5
                        self.drawCircle()	


class GameSpace:
	def main(self):
		# Initiation
		pygame.init()
		pygame.display.set_caption("PATH")
		self.size = self.width, self.height = 900, 900
		self.green = 0, 255, 0
		
		self.screen = pygame.display.set_mode(self.size)
		pygame.key.set_repeat(1, 100)

		# Pygame Objects
		self.clock = pygame.time.Clock()
		self.light = Light(self.size)
		# Game Loop
		while 1:
			#frame rate
			self.clock.tick(60)
			
			#handle user inputs
			for event in pygame.event.get():
				if event.type == KEYDOWN:
					self.light.move(event.key)
			

			#flush to screen and swap buffers
			self.light.tick()
			self.screen.fill(self.green)
			self.light.drawCircle()
			self.screen.blit(self.light.mask, (0,0))
			pygame.display.update()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()

		
