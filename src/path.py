# Gerard Martinez, Marshal Sprigg, and Yucheng Lin
import sys
import os
import math
import pygame
from maze import Maze
from pygame.locals import *
from random import randint

# GLOBAL VARIABLESi
WALL_SIZE = 36
SCALE = 1
MAZE_SIZE = 20
START_X = (MAZE_SIZE/2 - 1) * WALL_SIZE * SCALE
START_Y = (MAZE_SIZE - 1) * WALL_SIZE * SCALE
SCREEN_SIZE = WALL_SIZE * MAZE_SIZE * SCALE

# Flashlight class. Will Follow User Sprite.

class Wall(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../images/wall.png")
		self.rect = self.image.get_rect()
		self.orig_image = self.image
class Light():
	def __init__(self, size):
		# Black Mask
		self.mask = pygame.surface.Surface(size).convert_alpha()
		# Light Mask
		self.light_radius = 50
		self.light_mask = pygame.surface.Surface((self.light_radius, self.light_radius)).convert_alpha()
		self.collide = 0
		self.y = START_Y
		self.x = START_X
	
	# Draw Light	
	def drawCircle(self):
		self.mask.fill((0,0,0,250))
		radius = 50
		t = 100
		delta = 10
		while radius > 25:
			pygame.draw.circle(self.mask, (0,0,0,t), (self.x, self.y), radius)
			t -= delta
			radius -= delta
	def tick(self):
		pass
		#print "tick"

class Player(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.light = Light((SCREEN_SIZE, SCREEN_SIZE))
		self.collide = 0	
		self.img_list = ['../images/up.png', '../images/left.png', '../images/right.png', '../images/down.png'];
		self.gs = gs
		self.image = pygame.image.load(self.img_list[0])
		self.x = START_X
		self.y = START_Y
		self.rect = self.image.get_rect()
		self.orig_image = self.image
		self.rect = self.rect.move(self.x, self.y)
		self.last_position = []
		self.updateLastPosition()

	def move(self, event):
		if (event == K_RIGHT and self.collide == 0):
			self.image = pygame.image.load(self.img_list[2])
			self.updateLastPosition()
			self.rect = self.rect.move(5, 0)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

		elif (event == K_LEFT and self.collide == 0):
			self.image = pygame.image.load(self.img_list[1])
			self.updateLastPosition()
			self.rect = self.rect.move(-5, 0)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

		elif (event == K_UP and self.collide == 0):
			self.image = pygame.image.load(self.img_list[0])
			self.updateLastPosition()
			self.rect = self.rect.move(0, -5)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

		elif (event == K_DOWN and self.collide == 0):
			self.image = pygame.image.load(self.img_list[3])
			self.updateLastPosition()
			self.rect = self.rect.move(0, 5)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

	def setLastPosition (self):
		print "called: " + str(self.last_position)
		self.rect.centerx = self.last_position[0]
		self.rect.centery = self.last_position[1]

	def updateLastPosition(self):
		self.last_position = [self.rect.centerx, self.rect.centery]
	
class GameSpace:
	def __init__(self, mazesize=20):
		# game characters
		self.p1 = 'H'
		self.p2 = 'G'
		self.exit = 'E'

		# game maze
		self.maze = Maze(mazesize)
		self.maze.generate()
		
		size = self.maze.getSize()

		# set character start positions
		self.maze.setPos(size-1, size/2-1, self.p1)	# human
		self.maze.setPos(0, size/2-1, self.p2)		# ghost

		# set exit (try middle if path, otherwise on edge)
		if self.maze.getPos(size/2-1, size/2-1) == self.maze.path:
			self.maze.setPos(size/2-1, size/2-1, self.exit)
		else:
			side = randint(0,1)
			i = 0
			
			if side == 0:
				# set on left side
				while i < size:
					if self.maze.getPos(i, 0) == self.maze.path:
						self.maze.setPos(i, 0, self.exit)
						break
					i += 1
			else:
				# set on right side
				while i < size:
					if self.maze.getPos(i, size-1) == self.maze.path:
						self.maze.setPos(i, size-1, self.exit)
						break
					i += 1
	
		self.maze.display()

		# game walls
		self.walls = []

		# gameover variable
		self.game_over = 0 

	def main(self):
		# Initiation
		pygame.init()
		pygame.display.set_caption("PATH")
		self.size = self.width, self.height = SCREEN_SIZE, SCREEN_SIZE
		self.green = 0, 255, 0
		
		self.screen = pygame.display.set_mode(self.size)
		pygame.key.set_repeat(1, 100)
		self.screen_rect = self.screen.get_rect()

		self.exit_sprite = pygame.image.load("../images/exit.png")
		self.exit_rect = self.exit_sprite.get_rect()
	
		self.gameover_sprite = pygame.image.load("../images/gameover.png")
                self.gameover_rect = self.gameover_sprite.get_rect()
	
		self.bg = pygame.image.load("../images/background.png")
		self.bg_rect = self.bg.get_rect()
		#self.bg_rect = self.bg_rect.move(SCREEN_SIZE/2, SCREEN_SIZE/2)	
		# Music 
		pygame.mixer.music.load("../music/horror.wav")
		pygame.mixer.music.play(-1, 0.0)
		# maze display
		r = 0
		while r < self.maze.getSize():
			c = 0
			while c < self.maze.getSize():
				if self.maze.getPos(r, c) == self.maze.wall:
					rockWall = Wall()
					height = rockWall.rect.size
					rockWall.rect = rockWall.rect.move(height[0] * c, height[0] * r) 
					self.walls.append(rockWall)
				elif self.maze.getPos(r,c) == self.exit:
					self.exit_rect = self.exit_rect.move(WALL_SIZE * c, WALL_SIZE * r)
				c += 1
			r += 1

		# Pygame Objects
		self.clock = pygame.time.Clock()
		self.player = Player()
		# Game Loop
		while 1:
			#frame rate
			self.clock.tick(60)
			#handle user inputs
			for event in pygame.event.get():
				if event.type == KEYDOWN and self.game_over == 0:
					self.player.move(event.key)
				elif event.type == pygame.QUIT:
					sys.exit()
			
		

			#flush to screen and swap buffers
			self.screen.fill(self.green)
			self.screen.blit(self.bg, self.bg_rect)
			for w in self.walls:
				self.screen.blit(w.image, w.rect)

				# check for wall collisions
				if self.player.rect.colliderect(w.rect):
					self.player.setLastPosition() # set to last non-collision position
			
			if self.player.rect.colliderect(self.exit_rect):
				pygame.mixer.music.stop()
				self.game_over = 1
				print "You Win"
				self.player.setLastPosition()
				pygame.mixer.music.load("../music/win.wav")
                		pygame.mixer.music.play(1, 0.0)
				#sys.exit()
			
			self.screen.blit(self.exit_sprite, self.exit_rect)
			self.screen.blit(self.player.image, self.player.rect)
			if self.game_over == 0:
                        	self.player.light.drawCircle()
				self.screen.blit(self.player.light.mask, (0,0))
			else:
				self.screen.blit(self.gameover_sprite, self.gameover_rect)

			
			self.player.rect.clamp_ip(self.screen_rect)
			pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace(MAZE_SIZE)
	gs.main()
