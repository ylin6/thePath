# PATH
# CSE 30332
# Gerard Martinez, Marshall Sprigg, and Yucheng Lin
# human.py

import sys
import os
import math
import pygame
from maze import Maze
from pmessage import PlayerMessage
from pygame.locals import *
from random import randint
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import cPickle as pickle

# GLOBAL VARIABLES
WALL_SIZE = 36
SCALE = 1
MAZE_SIZE = 20
START_X = (MAZE_SIZE/2 - 1) * WALL_SIZE * SCALE
START_Y = (MAZE_SIZE - 1) * WALL_SIZE * SCALE
SCREEN_SIZE = WALL_SIZE * MAZE_SIZE * SCALE
GHOST_PORT = 9001

# Ghost Connection
class GhostConn(Protocol):
	def __init__(self, gs=None):
		self.gs = gs

	def connectionMade(self):
		#print "ghost connected"
		self.gs.connected = 1
		self.gs.ghostProtocol = self

	def dataReceived(self, data):
		obj = pickle.loads(data)

		self.gs.opponent = [obj.xPos, obj.yPos, obj.image]

class GhostFactory(Factory):
	def __init__(self, gs=None):
		self.gs = gs

	def buildProtocol(self, addr):
		return GhostConn(self.gs)


# Flashlight class. Will Follow User Sprite.
class Wall(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
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

class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.light = Light((SCREEN_SIZE, SCREEN_SIZE))
		self.collide = 0	
		self.img_list = ['../images/up.png', '../images/left.png', '../images/right.png', '../images/down.png'];
		self.image = pygame.image.load(self.img_list[0])
		self.imagePath = self.img_list[0]
		self.x = START_X
		self.y = START_Y
		self.rect = self.image.get_rect()
		self.orig_image = self.image
		self.rect = self.rect.move(self.x, self.y)
		self.last_position = []
		self.updateLastPosition()
		self.velocity = 7

	def move(self, event):
		if (event == K_RIGHT and self.collide == 0):
			self.image = pygame.image.load(self.img_list[2])
			self.imagePath = self.img_list[2]
			self.updateLastPosition()
			self.rect = self.rect.move(self.velocity, 0)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

		elif (event == K_LEFT and self.collide == 0):
			self.image = pygame.image.load(self.img_list[1])
			self.imagePath = self.img_list[1]
			self.updateLastPosition()
			self.rect = self.rect.move(-self.velocity, 0)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

		elif (event == K_UP and self.collide == 0):
			self.image = pygame.image.load(self.img_list[0])
			self.imagePath = self.img_list[0]
			self.updateLastPosition()
			self.rect = self.rect.move(0, -self.velocity)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

		elif (event == K_DOWN and self.collide == 0):
			self.image = pygame.image.load(self.img_list[3])
			self.imagePath = self.img_list[3]
			self.updateLastPosition()
			self.rect = self.rect.move(0, self.velocity)
			self.light.x = self.rect.centerx
			self.light.y = self.rect.centery

	def setLastPosition (self):
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
		self.boot = 1
		self.size = int()

		# game objects
		self.player = None
		self.clock = None

		# game objects
		pygame.init()
                self.exit_sprite = pygame.image.load("../images/exit.png")
                self.exit_rect = self.exit_sprite.get_rect()
                self.gameover_sprite = pygame.image.load("../images/gameover.png")
                self.gameover_rect = self.gameover_sprite.get_rect()
                self.gameover_rect = self.gameover_rect.move(SCREEN_SIZE/4, SCREEN_SIZE/4)
		self.gameoverl_sprite = pygame.image.load("../images/gameover_l.png")
                self.gameoverl_rect = self.gameoverl_sprite.get_rect()
                self.gameoverl_rect = self.gameoverl_rect.move(SCREEN_SIZE/4, SCREEN_SIZE/4)
                self.bg = pygame.image.load("../images/background.png")
                self.bg_rect = self.bg.get_rect()
		self.wait_screen = pygame.image.load("../images/wait_screen.png")
                self.wait_rect = self.wait_screen.get_rect()
                #self.bg_rect = self.bg_rect.move(SCREEN_SIZE/2, SCREEN_SIZE/2)

		self.size = self.width, self.height = SCREEN_SIZE, SCREEN_SIZE
                self.green = 0, 255, 0
		self.connected = 0

		self.opponent = [(MAZE_SIZE/2 - 1) * WALL_SIZE * SCALE, 0, "../images/ghost_down.png"]
		self.ghostImage = pygame.image.load(self.opponent[2])
		self.ghostRect = self.ghostImage.get_rect()		
		self.ghostRect.centerx = self.opponent[0]
		self.ghostRect.centery = self.opponent[1]
		
		# network
		self.ghostProtocol = None

	def setup(self):
		# generate maze
		self.maze.generate()
		size = self.maze.getSize()

		# send data to ghost
		pd = pickle.dumps(self.maze)
		self.ghostProtocol.transport.write(pd)

		# set character start positions
		self.maze.setPos(size-1, size/2-1, self.p1)	# human
		self.maze.setPos(0, size/2-1, self.p2)	   	# ghost

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
				while i < self.size:
					if self.maze.getPos(i, size-1) == self.maze.path:
						self.maze.setPos(i, size-1, self.exit)
						break
					i += 1

		#self.maze.display()

		# reset data
		self.walls = []
		self.game_over = 0
		self.lose = 0
		self.break_flag = 0

		# music 
                pygame.mixer.music.load("../music/horror.wav")
                pygame.mixer.music.play(-1, 0.0)
		return

	def main(self):
		# establish connection with ghost
		ghostFactory = GhostFactory(self)
		reactor.listenTCP(GHOST_PORT, ghostFactory)

		# Initialize screen window
		pygame.display.set_caption("PATH")
		
		self.screen = pygame.display.set_mode(self.size)
		pygame.key.set_repeat(1, 100)
		self.screen_rect = self.screen.get_rect()

		# set looping call tick
                tick = LoopingCall(self.gameloop)
                tick.start(1/60)

		reactor.run()

	def gameloop(self):
		if self.connected != 1:
			self.screen.blit(self.wait_screen, self.wait_rect)
                        pygame.display.flip()

		elif self.boot == 1:
			self.setup()

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
			self.boot = 0
		
		else:
			# Game Loop Logic	   
			if self.break_flag == 1:
				self.boot = 1
				# temporary
				os._exit(0)
		
			#frame rate
			self.clock.tick(60)

			#check user inputs
			for event in pygame.event.get():
				if event.type == KEYDOWN and self.game_over == 0:
					self.player.move(event.key)
					msg = PlayerMessage(self.player.rect.centerx, self.player.rect.centery, self.player.imagePath)
					self.ghostProtocol.transport.write(pickle.dumps(msg))
				elif event.type == KEYDOWN and self.game_over == 1:
					if event.key == K_n:
						sys.exit()
					elif event.key == K_y:
						self.break_flag = 1
				elif event.type == pygame.QUIT:
					os._exit(0)

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
					self.player.setLastPosition()
					pygame.mixer.music.load("../music/win.wav")
					pygame.mixer.music.play(1, 0.0)
					#sys.exit()

			self.screen.blit(self.exit_sprite, self.exit_rect)
			self.screen.blit(self.player.image, self.player.rect)
			self.ghostImage = pygame.image.load(self.opponent[2])
			self.ghostRect.centerx = self.opponent[0]
			self.ghostRect.centery = self.opponent[1]
			self.screen.blit(self.ghostImage, self.ghostRect)
			if self.ghostRect.colliderect(self.player.rect):
				self.game_over = 1
				self.lose = 1
			if self.game_over == 0:
				self.player.light.drawCircle()
				self.screen.blit(self.player.light.mask, (0,0))
			elif self.game_over == 1 and self.lose == 0:
				self.player.light.mask.fill((0,0, 0, 190))
				self.screen.blit(self.player.light.mask, (0,0))
				self.screen.blit(self.gameover_sprite, self.gameover_rect)
			elif self.game_over == 1 and self.lose == 1:
				self.player.light.mask.fill((0,0, 0, 190))
                                self.screen.blit(self.player.light.mask, (0,0))
                                self.screen.blit(self.gameoverl_sprite, self.gameoverl_rect)

			self.player.rect.clamp_ip(self.screen_rect)
			pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace(MAZE_SIZE)
	gs.main()
