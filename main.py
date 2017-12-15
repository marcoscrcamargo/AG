#!/usr/bin/env python
import sys, math, random, pygame

if not pygame.font: print("Warning, fonts disabled")

# Cores.
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PINK = (255, 0, 255)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)

# Constantes da janela.
SCREEN_TITLE = "Path finder Genetic Algorithm"
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000
BORDER_WIDTH = 1

# Número máximo de turnos.
MAX_TURNS = 2000

# Constantes
DEAD = -1
ALIVE = 0
WINNER = 1
POPULATION_SIZE = 300
ELITE_SIZE = 5
MIN_MUTATION = 0.001
MAX_MUTATION = 0.1
MAX_TURN = 0.25
STEP = 5

MIN_ROLLBACK = 10
MAX_ROLLBACK = 50

# Posição da bolinha
PELLET_X = 1300
PELLET_Y = SCREEN_HEIGHT // 2
PELLET_RADIUS = 32

# Posição inicial dos organismos
INITIAL_X = 100
INITIAL_Y = SCREEN_HEIGHT // 2

CHANCE_TO_RESET_GENOME = 0.005
CHANCE_TO_MUTATE_AT_DEATH = 0.25

# Cor de acordo com a taxa de mutação.
def get_color(mutation):
	return (((mutation - MIN_MUTATION) / (MAX_MUTATION - MIN_MUTATION)) * 255 , 0, 0)
	
# Cálculo da distância ao quadrado.
def distance(p, q):
	return math.sqrt((p[0] - q[0]) * (p[0] - q[0]) + (p[1] - q[1]) * (p[1] - q[1]))

# Classe principal
class Main:
	# Construtor, inicializa a tela
	def __init__(self):
		# Inicializando a janela.
		pygame.init()
		pygame.font.init()
		pygame.display.set_caption(SCREEN_TITLE)
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

	def MainLoop(self):
		# Carrega os objetos da cena.
		self.LoadSprites()
		
		# Criando o background. 
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((100, 100, 100))

		# Variaveis auxiliares
		self.gen = 0
		self.turn = 0 # Turno atual.
		clock = pygame.time.Clock() # Para controlar o FPS

		dead_organisms = {}
		winner_organisms = {}
		
		# Desenha background.
		self.screen.blit(self.background, (0, 0))

		# GameLoop
		while True:
			# Para sair.
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			
			# Verifica se acabou a geraçao atual (MAX_TURNS atingido ou todos organismos parados)
			if self.turn == MAX_TURNS or len(dead_organisms) + len(winner_organisms) == POPULATION_SIZE:
				# Reseta os turnos e incrementa a geração
				self.turn = 0
				self.gen += 1

				# Calcula o fitness de cada organismo
				for i in self.organism_list:
					i.update_fitness()

				# Ordena decrescente pelo fitness
				self.organism_list.sort(key=lambda x: x.fitness, reverse=True)

				# Imprime a geração atual e o rank com os 10 melhores fitness.
				print("Gen.: %d" % self.gen)

				for i in range (0, 10):
					print("\t%d) fitness = %.2f" % (i + 1, self.organism_list[i].fitness))

				# Gera toda a população usando apenas a elite.
				for i in range(ELITE_SIZE, POPULATION_SIZE):
					p1 = random.randint(0, ELITE_SIZE - 1)
					p2 = random.randint(0, ELITE_SIZE - 1)

					self.organism_list[i].make_child(self.organism_list[p1], self.organism_list[p2])

				# Reseta os organismos para o estado inicial.
				for s in self.organism_sprites.sprites():
					s.reset()

			# Realiza os movimentos dos organismos.
			for s in self.organism_sprites.sprites():
				s.move(self.turn)

			# Verifica colisão com a bolinha 
			winner_organisms = pygame.sprite.spritecollide(self.pellet, self.organism_sprites, False)

			# Verifica colisão com as paredes
			dead_organisms = pygame.sprite.groupcollide(self.organism_sprites, self.wall_sprites, False, False)

			# Para a movimentaçao dos organismos mortos e vencedores.
			for dead in dead_organisms:
				dead.state = DEAD

			for winner in winner_organisms:
				winner.state = WINNER

			   
			# Desenha os sprites
			self.pellet_sprites.draw(self.screen)
			self.organism_sprites.draw(self.screen)
			self.wall_sprites.draw(self.screen)
			self.print_stuff()
			pygame.display.flip()

			# Incremento do turno atual.
			self.turn += 1

	def print_stuff(self):
		font = pygame.font.SysFont("Arial", 36)
		text = font.render("Generation: %d" % (self.gen), True, (0, 180, 0))
		self.screen.blit(text, (10, 10))
		text = font.render("Fitness: %.2f" % (self.organism_list[0].fitness), True, (0, 180, 0))
		self.screen.blit(text, (10, 50))

	def LoadSprites(self):
		# Gerando o objetivo.
		self.pellet = Pellet(PELLET_X, PELLET_Y, PELLET_RADIUS)

		# Adiciona o objetivo ao conjunto de sprites.
		self.pellet_sprites = pygame.sprite.RenderPlain(self.pellet)

		# Cria um grupo de organismos.
		self.organism_sprites = pygame.sprite.Group()

		# Lista com os organismos.
		self.organism_list = [Organism(random.uniform(MIN_MUTATION, MAX_MUTATION)) for i in range(POPULATION_SIZE)]

		# Gerando cada organismo.
		for i in self.organism_list:
			self.organism_sprites.add(i)

		# Desenha as bordas.
		self.wall_sprites = pygame.sprite.Group()

		# Upper border.
		self.wall_sprites.add(Wall(0, 0, 0, SCREEN_WIDTH, BORDER_WIDTH, BLACK))

		# Lower border.
		self.wall_sprites.add(Wall(0, SCREEN_HEIGHT - BORDER_WIDTH, 0, SCREEN_WIDTH, BORDER_WIDTH, BLACK))

		# Left border.
		self.wall_sprites.add(Wall(0, 0, 0, BORDER_WIDTH, SCREEN_HEIGHT, BLACK))

		# Right border.
		self.wall_sprites.add(Wall(SCREEN_WIDTH - BORDER_WIDTH, 0, 0, BORDER_WIDTH, SCREEN_HEIGHT, BLACK))

		# Carrega os obstaculos
		self.randomize_map()

		# self.wall_sprites.add(Wall(500, 0, 0, 50, 400))
		# self.wall_sprites.add(Wall(500, SCREEN_HEIGHT - 400, 0, 50, 400))

		# self.wall_sprites.add(Wall(700, 100, 0, 50, SCREEN_HEIGHT - 200))

		# self.wall_sprites.add(Wall(900, 0, 0, 50, 400))
		# self.wall_sprites.add(Wall(900, SCREEN_HEIGHT - 400, 0, 50, 400))

		# self.wall_sprites.add(Wall(1100, 100, 0, 50, SCREEN_HEIGHT - 200))

	def randomize_map(self):
		pos_x = [i for i in range(200, SCREEN_WIDTH + 1, 200)]
		pos_y = [i for i in range(0, SCREEN_HEIGHT - 200 + 1, 200)]

		PELLET_X = random.randrange(700, 1700 + 1, 200)
		PELLET_Y = random.randrange(100, 900 + 1, 100)

		for i in pos_x:
			k = 0

			for j in pos_y:
				if random.random() < 0.5 and k < len(pos_y) - 1:
					k += 1
					self.wall_sprites.add(Wall(i, j, 0, 50, 200))
					
# Classe do organismo (triangulo)
class Organism(pygame.sprite.Sprite):
	# Construtor
	def __init__(self, mutation):
		# Construtor do pai.
		super().__init__()

		# Atributos do organismo.
		self.x = INITIAL_X
		self.y = INITIAL_Y
		self.angle = random.uniform(-math.pi, math.pi)
		self.width = 32
		self.height = 16
		self.mutation = mutation
		self.state = ALIVE
		self.genome = [random.uniform(-MAX_TURN, MAX_TURN) for i in range(MAX_TURNS)]
		self.fitness = 0

		# Cor de background transparente.
		self.original_image = pygame.Surface([self.width, self.height])
		self.original_image.fill(WHITE)
		self.original_image.set_colorkey(WHITE)
 		
		# Calculo da cor de acordo com a mutação
		self.color = get_color(mutation)

		# Desenhando o organismo.
		pygame.draw.polygon(self.original_image, self.color, [(0, 0), (0, self.height), (self.width, self.height // 2)])
		
		# Retângulo com as mesmas dimensões da imagem.
		self.rect = self.original_image.get_rect()
		self.image = self.original_image # Original image é usado para as transformações

		# Movendo para a posição inicial.
		self.rect.move_ip(self.x, self.y)

		# Tamanho da hitbox.
		self.rect.inflate_ip(-5, -5)

		# Métricas
		self.dist = self.min_dist = distance((self.rect.x, self.rect.y), (PELLET_X, PELLET_Y))
		self.dist_initial = 0
		self.time_to_dist = self.time_to_min_dist = -1

	# Funçao de movimento do organismo.
	def move(self, turn):
		if self.state == ALIVE:
			# Atualizando a distância atual
			self.dist = distance((self.rect.x, self.rect.y), (PELLET_X, PELLET_Y))
			self.dist_initial = distance((self.rect.x, self.rect.y), (INITIAL_X, INITIAL_Y))
			self.time_to_dist = turn

			# Atualizando a distância mínima
			if self.dist < self.min_dist:
				self.min_dist = self.dist
				self.time_to_min_dist = self.time_to_dist

			# Novo ângulo.
			self.angle += self.genome[turn]

			# Calculo do x,y
			xMove = STEP * math.cos(self.angle)
			yMove = STEP * math.sin(self.angle)

			# Realiza movimento e a rotação do objeto.
			self.rect.move_ip(xMove, yMove)
			self.image = pygame.transform.rotate(self.original_image, -math.degrees(self.angle))

	# Função que calcula o fitness de cada organismo
	def update_fitness(self):
		# O fitness inicial é a distância inicial
		self.fitness = distance((INITIAL_X, INITIAL_Y), (PELLET_X, PELLET_Y))

		# Bônus caso tenha alcançado o objetivo
		if self.state == WINNER:
			self.fitness *= (3 - self.time_to_min_dist / MAX_TURNS)
		else:
			self.fitness -= 0.4 * self.dist
			self.fitness -= 0.2 * self.min_dist
			self.fitness += 0.2 * self.time_to_dist * (1 - self.dist / distance((INITIAL_X, INITIAL_Y), (PELLET_X, PELLET_Y)))
			self.fitness += 0.3 * self.dist_initial

	# Volta o organismo para a posição original, estado e angulo
	def reset(self):
		self.rect.move_ip(self.x - self.rect.x, self.y - self.rect.y);
		self.state = ALIVE
		self.angle = 0

	# Realiza o cruzamento entre dois organismos e salva no atual
	def make_child(self, mom, dad):
		if random.random() < (1 + self.mutation) * CHANCE_TO_RESET_GENOME:
			self.genome = [random.uniform(-MAX_TURN, MAX_TURN) for i in range(MAX_TURNS)]
		else:
			self.genome = [dad.genome[i] if random.random() < 0.5 else mom.genome[i] for i in range(MAX_TURNS)]

			if random.random() < CHANCE_TO_MUTATE_AT_DEATH:
				s = max(0, min(mom.time_to_dist, dad.time_to_dist) - random.randint(MIN_ROLLBACK, MAX_ROLLBACK))
			else:
				s = 0

			# Mutação
			for i in range(s, MAX_TURNS):
				if random.random() < self.mutation * (1 + i / MAX_TURNS):
					if random.random() < 0.5:
						self.genome[i] = random.uniform(-MAX_TURN, MAX_TURN)
					else:
						self.genome[i] = -self.genome[i]

# Objetivo
class Pellet(pygame.sprite.Sprite):
	# Construtor.
	def __init__(self, x, y, radius = 32, color = YELLOW):
		# Construtor do pai.
		super().__init__()

		# Atributos do objetivo.
		self.x = x
		self.y = y
		self.radius = radius
		self.color = color
		
		# Cor do background.
		self.image = pygame.Surface((2 * self.radius, 2 * self.radius))
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE)
 
		# Desenhando o objetivo.
		pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

		# Retângulo com as mesmas dimensões da imagem.
		self.rect = self.image.get_rect()

		# Diminuindo a hitbox.
		# self.rect.inflate_ip(-10, -10)	

		# Movendo para a posição inicial.
		self.rect.move_ip(self.x, self.y)

# Paredes
class Wall(pygame.sprite.Sprite):
	# Construtor.
	def __init__(self, x, y, angle = 0, width = 50, height = 200, color = BLACK):
		# Construtor do pai.
		super().__init__()

		# Atributos da parede.
		self.x = x
		self.y = y
		self.angle = angle
		self.width = width
		self.height = height
		self.color = color
		
		# Pintando a superfície.
		self.image = pygame.Surface((width, height))
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE)
 		
		# Desenhando a parede.
		pygame.draw.polygon(self.image, color, [(0, 0), (0, height),(width, height), (width, 0)], 0)

		# Descomentar a linha de baixo quando arrumar a colisão com máscaras.
		# self.image = pygame.transform.rotate(self.image, -math.degrees(angle))
		self.rect = self.image.get_rect()
		self.rect.move_ip(x, y)

# Chamada da main.
if __name__ == "__main__":
	MainWindow = Main()
	MainWindow.MainLoop()
