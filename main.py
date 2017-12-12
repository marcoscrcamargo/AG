#! /usr/bin/env python

import os, sys
import pygame
import time
import numpy as np
import math

from pygame.locals import *

from helpers import *
import random

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

# Cores.
WHITE = (255, 255, 255)
RED = (200, 50, 50)
YELLOW = (200, 200, 50)
BLACK = (0, 0, 0)
BLUE = (50, 50, 200)

# Titulo da janela
WINDOW_TITLE = "Path finder AG"

# Número máximo de turnos.
max_turn = 1500

# Posição da bolinha
pellet_x = 900
pellet_y = 344

# Número maximo de organismos
numOrganism = 300

# Caracteristicas de cruzamento (mutação)
elitism = 0.01
best_crossing = 0.2
worst_crossing = 0.2
death_rate = 0.05

# Geração atual
gen = 0

# FPS (acaba sendo limitado pelo poder de processamento do PC)
FPS = 0 # 0 é pra ignorar

# Função que roda uma imagem. 
# (Não coloquei no organism, pq talvez as outras classes precisem usar)
#  seria uma boa colocar depois.
def rot_center(image, angle):
	"""rotate an image while keeping its center and size"""
	orig_rect = image.get_rect()
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = orig_rect.copy()
	rot_rect.center = rot_image.get_rect().center
	# rot_image = rot_image.subsurface(rot_rect).copy()
	return rot_image

# Classe principal
class Main:
	# Construtor, inicializa a tela
	def __init__(self, width=1024, height=768):
		# Pygame init
		pygame.init()

		# Titulo da tela
		pygame.display.set_caption(WINDOW_TITLE)

		# Dimensões da janela
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

	def MainLoop(self):
		# Carrega os objetos da cena.
		self.LoadSprites()
		
		# Criando o background. 
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill(BLUE) # Escolhi azul, mas pode mudar

		# Variaveis auxiliares
		turn = 0 # Turno atual.
		deads = 0 # Quantidade de organismos mortos.
		clock = pygame.time.Clock() # Para controlar o FPS

		# GameLoop
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			
			# Verifica se acabou a geraçao atual (max_turn atingido ou todos organismos parados)
			if (turn == max_turn or deads == numOrganism):
				# Reseta os turnos
				turn = 0

				# Incrementa a geração
				global gen
				gen = gen + 1

				# Calcula o fitness de cada organismo
				for i in self.organism_list:
					i.update_fitness()

				# Ordena pelo fitness (Reverso, quanto maior melhor)
				self.organism_list.sort(key=lambda x: x.fitness, reverse=True)

				# Imprime a geração atual e o rank com os 10 melhores fitness.
				print("Geraçao %d" % gen)
				for i in range (0, 10):
					print("\t score: %.2f" % self.organism_list[i].fitness)

				# Calcula a elite da população e não mata ela.
				elite = int(elitism*numOrganism)

				# Criação da próxima geração.

				# Gera toda a populaçao utilizando os dois melhores.
				for i in range (elite, numOrganism):
					self.organism_list[i].child(self.organism_list[0], self.organism_list[1])


				# Gera a população com base em vários critérios.
				# for i in range(elite, numOrganism):
				# 	rand = random.random()

				# 	# Mata aleatóriamente alguns organismos.
				# 	if rand < death_rate:
				# 		self.organism_list[i].gen_genome()
				# 	else :
				# 		b = int(best_crossing*numOrganism)
				# 		w = int(worst_crossing*numOrganism)
				# 		count = 0
				# 		if count < w:
				# 			# Cruzamento entre os melhores e piores.
				# 			self.organism_list[i].child(self.organism_list[i],
				# 			 self.organism_list[(numOrganism - i-1)]) 
				# 			count = count + 1
				# 		elif count < b + w:
				# 			# Cruzamento entre os melhores.
				# 			self.organism_list[i].child(self.organism_list[i % elite],
				# 			 self.organism_list[i % elite]) 
				# 			count = count + 1
				# 		else :
				# 			# Cruzamento por torneio.
				# 			# Escolha da mãe
				# 			o1 = random.randint(0, numOrganism-1)
				# 			o2 = random.randint(0, numOrganism-1)
				# 			mon = o2
				# 			if self.organism_list[o1].fitness > self.organism_list[o2].fitness:
				# 				mon = o1
				# 			# Escolha do pai
				# 			o1 = random.randint(0, numOrganism-1)
				# 			o2 = random.randint(0, numOrganism-1)
				# 			dad = o2
				# 			if self.organism_list[o1].fitness > self.organism_list[o2].fitness:
				# 				dad = o1

				# 			self.organism_list[i].child(self.organism_list[mon],
				# 			 self.organism_list[dad])

				# Reseta os organismos para o estado inicial.
				for s in self.organism_sprites.sprites():
					s.reset()

			# Realiza os movimentos dos organismos.
			for s in self.organism_sprites.sprites():
				s.move(turn)

			# Verifica colisão com a bolinha 
			winners = pygame.sprite.spritecollide(self.pellet, self.organism_sprites, False)

			# Verifica colisão com as paredes
			dead_organisms = pygame.sprite.groupcollide(self.organism_sprites, self.walls_sprites, False, False)


			# Para a movimentaçao dos organismos mortos e vencedores.
			for dead in dead_organisms:
				dead.stop_organism(turn, -1)
			for w in winners:
				w.stop_organism(turn, 1)

			# Conta a quantidade de organismos mortos e vencedores.
			deads = len(dead_organisms) + len(winners)


			# Desenha background.
			self.screen.blit(self.background, (0, 0))
			   
			# Desenha os sprites
			self.pellet_sprites.draw(self.screen)
			self.organism_sprites.draw(self.screen)
			self.walls_sprites.draw(self.screen)
			pygame.display.flip()

			# Incremento do turno atual.
			turn = (turn + 1)

			# FPS
			if(FPS > 0):
				clock.tick(FPS)

	def LoadSprites(self):
		# Tamanho da bola
		pellet_width = 64
		# Carrega a Bola de destino.
		self.pellet = Pellet(YELLOW, pellet_width, pellet_x, pellet_y)
		# Adiciona a bola ao conjunto de sprites
		self.pellet_sprites = pygame.sprite.RenderPlain(self.pellet)

		# Carrega os organismos.
		self.organism_sprites = pygame.sprite.Group()
		# Lista com os organismos (para ordenação)
		self.organism_list = list()
		# Gera cada organismo
		for i in range(numOrganism):
			organism = Organism()
			# Adiciona ao conjunto de sprites.
			self.organism_sprites.add(organism)
			# Adiciona a lista de organismos.
			self.organism_list.append(organism)

		# Carrega os limites do cenário.
		# Pontos para a contrução da borda 
		p1 = (0, 0)
		p2 = (self.width, 0)
		p3 = (0, self.height)
		w = 10 # Wide da linha da borda

		# Desenha as bordas
		self.walls_sprites = pygame.sprite.Group()

		# Linhas horizontal
		self.walls_sprites.add(Line(self.screen.get_size(), p1, p2, wide=w))
		self.walls_sprites.add(Line(self.screen.get_size(), p1, p2, x=0, y=self.height-(w/2), wide=w))

		# Linhas vertical
		self.walls_sprites.add(Line(self.screen.get_size(), p3, p1, wide=w))
		self.walls_sprites.add(Line(self.screen.get_size(), p3, p1, x=self.width-(w/2), y=0, wide=w))

		# Carrega os obstaculos
		# Isso precisa ser melhorado.
		self.walls_sprites.add(Wall(200, 0))
		self.walls_sprites.add(Wall(300, 344))
		self.walls_sprites.add(Wall(200, 664))



# Classe do organismo (triangulo)
class Organism(pygame.sprite.Sprite):
	# Construtor
	def __init__(self, color=RED, width=30, height=15, x=64, y=344):
		# Construtor do pai.
		super().__init__()
		
		# AG
		self.min_mutation = 0.0001;
		self.max_mutation = 0.1;
		self.mutation = (self.max_mutation - self.min_mutation) * np.random.random_sample() + self.min_mutation

		# Cor de background transparente.
		self.original_image = pygame.Surface([width, height])
		self.original_image.fill(WHITE)
		self.original_image.set_colorkey(WHITE)
 		
		# Calculo da cor de acordo com a mutação
		chunk = (self.max_mutation-self.min_mutation)/3
		if(self.mutation < self.min_mutation + chunk):
			b = 178/(1 - ((self.min_mutation + chunk)/self.min_mutation))
			a = -b/self.min_mutation
			color = (244, 66+(a*self.mutation+b), 66)
		elif (self.mutation < self.min_mutation + 2*chunk):
			b = 178/(1 - ((self.min_mutation + chunk)/(self.min_mutation + 2*chunk)))
			a = -b/(self.min_mutation + 2*chunk)
			color = (66+(a*self.mutation+b), 244, 66)
		else:
			b = 178/(1 - (self.max_mutation/(self.min_mutation + 2*chunk)))
			a = -b/(self.min_mutation + 2*chunk)
			color = (66, 244, 66 + (a*self.mutation+b))

		# Desenhando o organismo (triangulo)
		pygame.draw.polygon(self.original_image, color,  [[0, 0], [0, height],[width, height/2]], 0)
		
		# Retangulo com as mesmas dimensões da imagem.
		self.rect = self.original_image.get_rect()
		self.image = self.original_image # Original image é usado para as transformações

		# Movimentação
		self.angle = 0
		# Posiçao inicial do organismo (base)
		self.x = x
		self.y = y
		self.rect.move_ip(self.x, self.y)

		# tamanho da hitbox
		self.rect.inflate_ip(-4,-4) # Encontrar valor bom ( tamanho da hitbox do organismo )

		# AG
		self.state = 0 # 0 - Continua vivo    negative - Turno de morte     positive - Turno em que chega ao objetivo.
		self.genome = np.random.uniform(low=-0.2, high=0.2, size=max_turn)
		self.fitness = 0


	# Funçao de movimento do organismo.
	def move(self, turn):
		if(self.state == 0):
			# Novo angulo
			self.angle = self.angle + self.genome[turn]
			# Calculo do x,y
			xMove = int(2*math.cos(self.angle))
			yMove = int(2*math.sin(self.angle))

			# Realiza movimento e a rotação do objeto.
			self.rect.move_ip(xMove, yMove)
			self.image = rot_center(self.original_image, math.degrees(self.angle))


	# Função que calcula o fitness de cada organismo
	def update_fitness(self):
		# score = 1*(max_turn-final_distance)+0.5*(max_turn-closest_distance)+1*(1000-goal_turn)+0.3*(1000-last_of_dead_or_goal_turn)

		x = self.rect.x
		y = self.rect.y
		dist = math.sqrt((x - pellet_x)**2 + (y - pellet_y)**2)

		# Se continua vivo e não parou.
				# #Turnos - distancia + 0.5 (#Turnos - Fitness anterior)
		score = (max_turn - dist) + 0.5 * (max_turn - self.fitness)

		# Se chegou ao objetivo.
		if self.state > 0 :
					# 1.5 * (#Turnos - dist) + 1.3 * (#Turnos - turno que chegou )
			score = 1.5 * (max_turn - dist) + 1.3 * (max_turn - self.state)
		# Se morrreu.
		elif self.state < 0:
					# (#Turnos - distancia) + 0.5 * (#Turnos - fitness anterior) + 0.3 * (#Turnos - turno que morreu )
			score = (max_turn - dist) + 0.5 * (max_turn - self.fitness) + 0.3 * (max_turn + self.state);

		self.fitness = score

		return self.fitness

	# Mata o organismo, faz ele parar de realizar os movimentos
	# signal deve ser 1 ou -1 para indicar se está vivo ou morto, respectivamente.
	def stop_organism(self, turn, signal):
		self.state = turn*signal

	# Volta o organismo para a posição original, estado e angulo
	def reset(self):
		self.rect.move_ip(self.x - self.rect.x, self.y - self.rect.y );
		self.state = 0
		self.angle = 0

	# Gera um genoma aleatório para o organismo.
	def gen_genome(self):
		self.genome = np.random.uniform(low=-0.2, high=0.2, size=max_turn)


	# Realiza o cruzamento entre dois organismos e salva no atual
	def child(self, mom, dad):
		for i in range(abs(dad.state)):
			# Cruzamento
			# Escolhe o organismo do pai ou da mãe
			rand = random.random()
			if(rand < 0.5):
				self.genome[i] = mom.genome[i]
			else:
				self.genome[i] = dad.genome[i]

			# Mutação.
			rand = random.random()
			if(rand < self.mutation):
				self.genome[i] = random.uniform(-0.2, 0.2)

		# Copia parte do gene do pai que não foi utilizada.
		for i in range(abs(dad.state) + 1, max_turn):
			self.genome[i] = random.uniform(-0.2, 0.2)

# Classe da bolinha de destino.
class Pellet(pygame.sprite.Sprite):
	# Construtor.
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
		
		# Movimenta para a posiçao inicial
		self.x = x
		self.y = y
		self.rect.move_ip(self.x, self.y)

# Classe dos obstaculos (Parede)
class Wall(pygame.sprite.Sprite):
''' 
	Essa classe deve ser melhorada para suportar melhor os obstaculos
		(ou desenhar melhor as imagens, ou fazer por meio do pygame (igual os outros objetos))

	Também deve ser adicionadas mais instâncias dessa classe na função LoadSprites, 
		para dificultar o movimento dos organismos.
'''

	# Construtor
	def __init__(self, x, y):
		# Construtor do pai.
		super().__init__()

		# Carrega a imagem do arquivo.
		self.image, self.rect = load_image('wall.png', -1)


		# if rect != None:
		# 	self.rect = rect
		self.rect.move_ip(x, y)

# Linhas que representam as bordas do espaço.
class Line(pygame.sprite.Sprite):
	# Contrutor
	def __init__(self, size, p1, p2, x=0, y=0, wide=3):
		# Construtor do pai.
		super().__init__()

		# Calculo da espessura da linha 
		width = abs(p2[0] - p1[0]) if p2[0] - p1[0] != 0 else wide

		height = abs(p2[1] - p1[1]) if p2[1] - p1[1] != 0 else wide
		# Cor de background transparente.
		self.image = pygame.Surface([width, height])
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE)
	
		# Desenhando a linha.
		pygame.draw.line(self.image, BLACK, p1, p2, wide)
	
		# Retangulo com as mesmas dimensões da imagem.
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.rect.move_ip(self.x, self.y)

# Chamada da main.
if __name__ == "__main__":
	MainWindow = Main()
	MainWindow.MainLoop()
