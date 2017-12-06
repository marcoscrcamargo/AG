#! /usr/bin/env python

import os, sys
import pygame
import time
import numpy as np
import math

from pygame.locals import *

from helpers import *
from random import randint

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

# Cores.
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

WINDOW_TITLE = "Path finder AG"
max_turn = 2000

pellet_x = 900
pellet_y = 344

numOrganism = 10

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
		pygame.display.set_caption(WINDOW_TITLE)
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

	def MainLoop(self):
		self.LoadSprites()
		
		# Criando o background. 
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill(BLUE)
		turn = 0
		clock = pygame.time.Clock()
		while True:
			turn = (turn + 1) % 2000
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			
			for s in self.organism_sprites.sprites():
				s.move(turn)

			# Verifica colisão com a bolinha 
			winners = pygame.sprite.spritecollide(self.pellet, self.organism_sprites, False)

			# Verifica colisão com as paredes
			dead_organisms = pygame.sprite.groupcollide(self.organism_sprites, self.walls_sprites, False, False)
			for dead in dead_organisms:
				dead.stop_organism(kill=True)
			for w in winners:
				w.stop_organism(kill=False)

			# Para a movimentaçao dos organismos mortos e vencedores.
			# print(dead_organisms)
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
			   
			# Desenha os sprites
			self.pellet_sprites.draw(self.screen)
			self.organism_sprites.draw(self.screen)
			self.walls_sprites.draw(self.screen)
			pygame.display.flip()

			#Number of frames per secong e.g. 60
			clock.tick(60)

	def LoadSprites(self):
		pellet_width = 64
		# Carrega a Bola de destino.
		self.pellet = Pellet(YELLOW, pellet_width, pellet_x, pellet_y)
		self.pellet_sprites = pygame.sprite.RenderPlain(self.pellet)

		# Carrega os organismos.
		self.organism_sprites = pygame.sprite.Group()
		for i in range(numOrganism):
			self.organism_sprites.add(Organism()) #Descobrir como definir o spectro de cores aqui xD

		# Carrega os limites do cenário.
		p1 = (0, 0)
		p2 = (self.width, 0)
		p3 = (0, self.height)
		self.walls_sprites = pygame.sprite.Group()
		# Linha horizontal
		self.walls_sprites.add(Line(self.screen.get_size(), p1, p2, wide=10))
		self.walls_sprites.add(Line(self.screen.get_size(), p1, p2, x=0, y=self.height-5, wide=10))

		# Linha vertical
		self.walls_sprites.add(Line(self.screen.get_size(), p3, p1, wide=10))
		self.walls_sprites.add(Line(self.screen.get_size(), p3, p1, x=self.width-5, y=0, wide=10))

		# Carrega as paredes
		self.walls_sprites.add(Wall(200, 0))
		self.walls_sprites.add(Wall(300, 344))
		self.walls_sprites.add(Wall(200, 664))

class Organism(pygame.sprite.Sprite):
	def __init__(self, color=RED, width=30, height=15, x=64, y=344):
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
		self.image = self.original_image # Original image é usado para as transformações

		# Movimentação
		self.angle = 0
		self.state = True
		# Posiçao inicial do organismo (base)
		self.rect.move_ip(x, y)
		self.rect.inflate_ip(-4,-4) # Encontrar valor bom ( tamanho da hitbox do organismo )
		
		# AG
		self.min_mutation = 0.0001;
		self.max_mutation = 0.01;

		self.mutation = (self.max_mutation - self.min_mutation) * np.random.random_sample() + self.min_mutation
		self.genome = np.random.uniform(low=-0.2, high=0.2, size=max_turn)
		self.fitness = 0


	# Funçao de movimento do organismo.
	def move(self, turn):
		if(self.state == True):
			self.angle = self.angle + self.genome[turn]
			xMove = int(2*math.cos(self.angle));
			yMove = int(2*math.sin(self.angle));

			# self.image = pygame.transform.rotate(self.original_image, math.degrees(self.angle))
			self.rect.move_ip(xMove, yMove);
			self.image = rot_center(self.original_image, math.degrees(self.angle))


	def update_fitness(self):
		# fitness calculation
		# score = 1*(max_turn-final_distance)+0.5*(max_turn-closest_distance)+1*(1000-goal_turn)+0.3*(1000-last_of_dead_or_goal_turn)
		x = self.rect.x
		y = self.rect.y
		dist = math.sqrt((x - pellet_x)**2 + (y - pellet_y)**2)

		fitness = dist 
		return fitness

	def stop_organism(self, kill):
		self.state = False

class Pellet(pygame.sprite.Sprite):
	def __init__(self, color, width, x, y):
		# Construtor do pai.
		super().__init__()
		
		# Cor de background transparente.
		self.image = pygame.Surface([width, width])
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE)
 
		# Desenhando a bolinha
		pygame.draw.circle(self.image, color, (width//2, width//2), width//2, 0)

		# Retangulo com as mesmas dimensões da imagem.
		self.rect = self.image.get_rect()
		
		self.rect.move_ip(x, y)


class Wall(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('wall.png', -1)
		# if rect != None:
		# 	self.rect = rect
		self.rect.move_ip(x, y)

class Line(pygame.sprite.Sprite):
	def __init__(self, size, p1, p2, x=0, y=0, wide=3):
		# Construtor do pai.
		super().__init__()
		
		# Cor de background transparente.
		width = abs(p2[0] - p1[0]) if p2[0] - p1[0] != 0 else wide
		height = abs(p2[1] - p1[1]) if p2[1] - p1[1] != 0 else wide

		print(width)
		print(height)
		self.image = pygame.Surface([width, height])
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE)
	
		# Desenhando a linha

		pygame.draw.line(self.image, BLACK, p1, p2, wide)
	
		# Retangulo com as mesmas dimensões da imagem.
		self.rect = self.image.get_rect()
		self.rect.move_ip(x, y)


if __name__ == "__main__":
	MainWindow = Main()
	MainWindow.MainLoop()
