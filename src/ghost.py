# PATH
# CSE 30332
# Gerard Martinez, Marshall Sprigg, and Yucheng Lin
# ghost.py

import sys
import os
import math
import pygame
from maze import Maze
from pygame.locals import *
from random import randint
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import cPickle as pickle
from pmessage import PlayerMessage

# GLOBAL VARIABLES
WALL_SIZE = 36
SCALE = 1
MAZE_SIZE = 20
START_X = (MAZE_SIZE/2 - 1) * WALL_SIZE * SCALE
START_Y = 0
SCREEN_SIZE = WALL_SIZE * MAZE_SIZE * SCALE
GHOST_PORT = 9001
MAZE_FLAG = 1

# Ghost Connection
class GhostConn(Protocol):
	def __init__(self, gs=None):
		self.gs = gs

	def connectionMade(self):
		print "ghost connected"
		self.gs.connected = 1
		self.gs.ghostProtocol = self

	def dataReceived(self, data):
		obj = pickle.loads(data)

		global MAZE_FLAG
		if MAZE_FLAG == 1:
		# set game maze
			self.gs.maze = obj

		# turn flag off
			MAZE_FLAG = 0
		else:
			self.gs.opponent = [obj.xPos, obj.yPos, obj.image]

class GhostFactory(ClientFactory):
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

class Ghost(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.collide = 0	
		self.img_list = ['../images/ghost_up.png', '../images/ghost_left.png', '../images/ghost_right.png', '../images/ghost_down.png'];
		self.image = pygame.image.load(self.img_list[3])
		self.imagePath = self.img_list[3]
		self.x = START_X
		self.y = START_Y
		self.rect = self.image.get_rect()
		self.orig_image = self.image
		self.rect = self.rect.move(self.x, self.y)
		self.last_position = []
		self.velocity = 5

	def move(self, event):
		if (event == K_RIGHT and self.collide == 0):
			self.image = pygame.image.load(self.img_list[2])
			self.imagePath = self.img_list[2]
			self.rect = self.rect.move(self.velocity, 0)

		elif (event == K_LEFT and self.collide == 0):
			self.image = pygame.image.load(self.img_list[1])
			self.imagePath = self.img_list[1]
			self.rect = self.rect.move(-self.velocity, 0)

		elif (event == K_UP and self.collide == 0):
			self.image = pygame.image.load(self.img_list[0])
			self.imagePath = self.img_list[0]
			self.rect = self.rect.move(0, -self.velocity)

		elif (event == K_DOWN and self.collide == 0):
			self.image = pygame.image.load(self.img_list[3])
			self.imagePath = self.img_list[3]
			self.rect = self.rect.move(0, self.velocity)

class GameSpace:
	def __init__(self, mazesize=20):
		# game characters
		self.exit = 'E'

		# game maze
		self.maze = None
		self.boot = 1
		self.size = int()

		# game objects
		self.ghost = None
		self.clock = None

		# game objects
		pygame.init()
                #self.exit_sprite = pygame.image.load("../images/exit.png")
                #self.exit_rect = self.exit_sprite.get_rect()
                self.gameover_sprite = pygame.image.load("../images/gameover.png")
                self.gameover_rect = self.gameover_sprite.get_rect()
                self.gameover_rect = self.gameover_rect.move(SCREEN_SIZE/4, SCREEN_SIZE/4)
                self.bg = pygame.image.load("../images/background.png")
                self.bg_rect = self.bg.get_rect()
		self.wait_screen = pygame.image.load("../images/wait_screen.png")
                self.wait_rect = self.wait_screen.get_rect()

		self.size = self.width, self.height = SCREEN_SIZE, SCREEN_SIZE
                self.green = 0, 255, 0
		self.connected = 0

		self.opponent = [(MAZE_SIZE/2 - 1) * WALL_SIZE * SCALE, (MAZE_SIZE - 1) * WALL_SIZE * SCALE, "../images/up.png"]		
		self.humanImage = pygame.image.load(self.opponent[2])
		self.humanRect = self.humanImage.get_rect()
		self.humanRect.centerx = self.opponent[0] + 15
		self.humanRect.centery = self.opponent[1] + 15
		# network
		self.ghostProtocol = None

	def setup(self):
		size = self.maze.getSize()
		self.maze.display()

		# reset data
		self.walls = []
		self.game_over = 0
		self.break_flag = 0

		# music 
                pygame.mixer.music.load("../music/horror.wav")
                pygame.mixer.music.play(-1, 0.0)
		return

	def main(self):
		# establish connection with ghost
		ghostFactory = GhostFactory(self)
		reactor.connectTCP("localhost", GHOST_PORT, ghostFactory)

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
			global MAZE_FLAG
			if MAZE_FLAG == 1:
				return

			self.setup()

			# generate maze display
			r = 0
			while r < self.maze.getSize():
				c = 0
				while c < self.maze.getSize():
					if self.maze.getPos(r, c) == self.maze.wall:
						rockWall = Wall()
						height = rockWall.rect.size
						rockWall.rect = rockWall.rect.move(height[0] * c, height[0] * r)
						self.walls.append(rockWall)
					#elif self.maze.getPos(r,c) == self.exit:
					#	self.exit_rect = self.exit_rect.move_ip(WALL_SIZE * c, WALL_SIZE * r)
					c += 1
				r += 1

			# Pygame Objects
			self.clock = pygame.time.Clock()
			self.ghost = Ghost()
			self.boot = 0
		
		else:
			# Game Loop Logic	   
			if self.break_flag == 1:
				self.boot = 1
				MAZE_FLAG = 1
				return
		
			#frame rate
			self.clock.tick(60)

			#check user inputs
			for event in pygame.event.get():
				if event.type == KEYDOWN and self.game_over == 0:
					self.ghost.move(event.key)
					msg = PlayerMessage(self.ghost.rect.centerx, self.ghost.rect.centery, self.ghost.imagePath)
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

				#if self.player.rect.colliderect(self.exit_rect):
				#	pygame.mixer.music.stop()
				#	self.game_over = 1
				#	self.player.setLastPosition()
				#	pygame.mixer.music.load("../music/win.wav")
				#	pygame.mixer.music.play(1, 0.0)
					#sys.exit()

			#self.screen.blit(self.exit_sprite, self.exit_rect)
			self.screen.blit(self.ghost.image, self.ghost.rect)
			self.humanRect.centerx = self.opponent[0]
			self.humanRect.centery = self.opponent[1]
			if self.humanRect.colliderect(self.ghost.rect):
				print "collision"
			self.humanImage = pygame.image.load(self.opponent[2])
			self.screen.blit(self.humanImage, self.humanRect)
			
			if self.game_over == 1:
				self.screen.blit(self.gameover_sprite, self.gameover_rect)

			self.ghost.rect.clamp_ip(self.screen_rect)
			pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace(MAZE_SIZE)
	gs.main()
