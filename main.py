#! /usr/bin/env python

import os, sys
import pygame
import time
from pygame.locals import *

from helpers import *
from random import randint

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')


class SpermMain:
	def __init__(self, width=1024, height=768):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.numSperm = 4

	def MainLoop(self):
		self.LoadSprites()

		pygame.key.set_repeat(500, 30)
		
		"""Create the background"""
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((0,0,0))


		while True:
			time.sleep(0.01)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			
			for s in self.sperm_sprites.sprites():
				s.move()

			# """Check for collision"""
			lstCols = pygame.sprite.spritecollide(self.pellet
												 , self.sperm_sprites
												 , True)
			for w in self.walls_sprites.sprites():
				pygame.sprite.spritecollide(w, self.sperm_sprites, True)

			# """Update the amount of pellets eaten"""
			# self.sperm.pellets = self.sperm.pellets + len(lstCols)
						
			# """Do the Drawging"""			   
			self.screen.blit(self.background, (0, 0))	 
			# if pygame.font:
			# 	font = pygame.font.Font(None, 36)
			# 	text = font.render("Pellets %s" % self.sperm.pellets
			# 						, 1, (255, 0, 0))
			# 	textpos = text.get_rect(centerx=self.background.get_width()/2)
			# 	self.screen.blit(text, textpos)
			   


			self.pellet_sprites.draw(self.screen)
			self.sperm_sprites.draw(self.screen)
			self.walls_sprites.draw(self.screen)
			pygame.display.flip()

	def LoadSprites(self):
		# Load Pellet
		self.pellet = Pellet(pygame.Rect(900,344,64,64))
		self.pellet_sprites = pygame.sprite.RenderPlain(self.pellet)

		# Load numSperm Sperms
		self.sperm_sprites = pygame.sprite.Group()
		for i in range(self.numSperm):
			self.sperm_sprites.add(Sperm())

		# Load Walls
		self.walls_sprites = pygame.sprite.Group()
		
		self.walls_sprites.add(Wall(pygame.Rect(200, 0, 64, 64)))
		self.walls_sprites.add(Wall(pygame.Rect(300, 344, 64, 64)))
		self.walls_sprites.add(Wall(pygame.Rect(200, 664, 64, 64)))

class Sperm(pygame.sprite.Sprite):
	def __init__(self, rect=None):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('sperm.png', -1)
		self.x_dist = 5
		self.y_dist = 5

		if rect != None:
			self.rect = rect
		else:
			self.rect = pygame.Rect(64, 344, 64, 64) # Posiçao inicial do sperm

	def move(self):
		xMove = 0;
		yMove = 0;
		dirMove = randint(0, 3)

		if (dirMove == 0):
			xMove = self.x_dist
		elif (dirMove == 1):
			xMove = -self.x_dist
		elif (dirMove == 2):
			yMove = -self.y_dist
		elif (dirMove == 3):
			yMove = self.y_dist
		self.rect.move_ip(xMove,yMove);

class Pellet(pygame.sprite.Sprite):
	def __init__(self, rect=None):
		self.qnt = 0
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('pellet.png', -1)
		if rect != None:
			self.rect = rect

class Wall(pygame.sprite.Sprite):
	def __init__(self, rect=None):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('wall.png', -1)
		if rect != None:
			self.rect = rect



if __name__ == "__main__":
	MainWindow = SpermMain()
	MainWindow.MainLoop()
