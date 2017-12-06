#! /usr/bin/env python

import os, sys
import pygame
import time
import numpy as np
import math

from pygame.locals import *

WHITE = (255, 255, 255)
RED = (255, 0, 0)
from helpers import *
from random import randint

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')



max_turn = 2000

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    # rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class Main:
	def __init__(self, width=1024, height=768):
		pygame.init()
		pygame.display.set_caption("AG")
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.numOrganism = 10

	def MainLoop(self):
		self.LoadSprites()
		
		# Criando o background. 
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((0,0,0))
		turn = 0
		clock = pygame.time.Clock()
		while True:
			turn = (turn + 1) % 2000
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			
			for s in self.organism_sprites.sprites():
				s.move(turn)

			# Verifica colisão com a bolinha (precisa mudar)
			lstCols = pygame.sprite.spritecollide(self.pellet
												 , self.organism_sprites
												 , True)
			# Verifica colisão com as paredes(precisa mudar)
			for w in self.walls_sprites.sprites():
				pygame.sprite.spritecollide(w, self.organism_sprites, True)

			# Contador de comidas
			# self.organism.pellets = self.organism.pellets + len(lstCols)
						
			# Desenha			   
			self.screen.blit(self.background, (0, 0))	 

			# Escreve na tela
			# if pygame.font:
			# 	font = pygame.font.Font(None, 36)
			# 	text = font.render("Pellets %s" % self.organism.pellets
			# 						, 1, (255, 0, 0))
			# 	textpos = text.get_rect(centerx=self.background.get_width()/2)
			# 	self.screen.blit(text, textpos)
			   
			# Desenha os objetos
			self.pellet_sprites.draw(self.screen)
			self.organism_sprites.draw(self.screen)
			self.walls_sprites.draw(self.screen)
			pygame.display.flip()
			#Number of frames per secong e.g. 60
			clock.tick(60)

	def LoadSprites(self):
		# Load Pellet
		self.pellet = Pellet(pygame.Rect(900,344,64,64))
		self.pellet_sprites = pygame.sprite.RenderPlain(self.pellet)

		# Load numOrganism Organisms
		self.organism_sprites = pygame.sprite.Group()
		for i in range(self.numOrganism):
			self.organism_sprites.add(Organism(RED, 30, 15))

		# Load Walls
		self.walls_sprites = pygame.sprite.Group()
		
		self.walls_sprites.add(Wall(pygame.Rect(200, 0, 64, 64)))
		self.walls_sprites.add(Wall(pygame.Rect(300, 344, 64, 64)))
		self.walls_sprites.add(Wall(pygame.Rect(200, 664, 64, 64)))

class Organism(pygame.sprite.Sprite):
	def __init__(self, color, width, height, rect=None):
		# Construtor do pai.
		super().__init__()
		
		# Cor de background transparente.
		self.original_image = pygame.Surface([width, height])
		self.original_image.fill(WHITE)
		self.original_image.set_colorkey(WHITE)
 
		# Desenhando o organismo (triangulo)
		pygame.draw.polygon(self.original_image, color,  [[0, 0], [0, height],[width, height/2]], 0)
		
		# Retangulo com as mesmas dimensões da imagem.
		self.rect = self.original_image.get_rect()

		self.image = self.original_image
	# Antigo (usando imagem)
	# def __init__(self, rect=None):
	# 	pygame.sprite.Sprite.__init__(self)

	# 	# Imagem do organismo.
	# 	self.original_image, self.original_rect = load_image('triangle.png', -1)
	# 	self.image = self.original_image
	# 	self.rect = self.original_rect

		# Passo
		self.angle = 0

		# AG
		self.mutation = 0
		self.genome = np.random.uniform(low=-0.2, high=0.2, size=max_turn)
		
		# Posiçao inicial do organismo (base)
		if rect != None:
			self.rect = rect
		self.rect.move_ip(64, 344) 

	# Funçao de movimento do organismo.
	def move(self, turn):
		self.angle = self.angle + self.genome[turn]
		xMove = int(2*math.cos(self.angle));
		yMove = int(2*math.sin(self.angle));
		# self.image = pygame.transform.rotate(self.original_image, math.degrees(self.angle))
		self.rect.move_ip(xMove, yMove);
		self.image = rot_center(self.original_image, math.degrees(self.angle))

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
	MainWindow = Main()
	MainWindow.MainLoop()
