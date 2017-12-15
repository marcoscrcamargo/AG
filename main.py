# Victor Forbes - 9293394
# Marcos Camargo - 9278045
# Gabriel Camargo - 9293456
#
# Dependências:
# 	- Python3: sudo apt-get install python3
# 	- Pip3: sudo apt-get install python3-pip
# 	- Pygame: sudo pip3 install pygame
#
# Para rodar: python3 main.py
#
# Altere as constantes globais SHOW_TRAIL e MAP! 

#!/usr/bin/env python
import sys, math, random, pygame

if not pygame.font: print("Warning, fonts disabled")

# Constantes.
RANDOM_MAP = 0

# Mudar esses parâmetros para visualização.
SHOW_TRAIL = False
MAP = RANDOM_MAP # Pode ser RANDOM_MAP, 1 ou 2.

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

# Parâmetros do AG.
MAX_TURNS = 2000
POPULATION_SIZE = 300
CANDIDATES = 60
ELITE_SIZE = 7
MIN_MUTATION = 0.001
MAX_MUTATION = 0.1
MAX_TURN = 0.25
STEP = 5
MIN_ROLLBACK = 10
MAX_ROLLBACK = 100
CHANCE_TO_RESET_GENOME = 0.01
CHANCE_TO_MUTATE_AT_DEATH = 0.4

# Constantes.
DEAD = -1
ALIVE = 0
WINNER = 1

# Objetivo em mapas não aleatórios
PELLET_RADIUS = 32

# Posição inicial dos indivíduos.
INITIAL_X = 100
INITIAL_Y = SCREEN_HEIGHT // 2

# Cor de acordo com a taxa de mutação.
def get_color(mutation):
	return (((mutation - MIN_MUTATION) / (MAX_MUTATION - MIN_MUTATION)) * 255 , 0, 0)
	
# Distância de dois pontos.
def distance(p, q):
	return math.sqrt((p[0] - q[0]) * (p[0] - q[0]) + (p[1] - q[1]) * (p[1] - q[1]))

# Classe principal.
class Main:
	# Construtor, inicializa a tela.
	def __init__(self):
		pygame.init()
		pygame.display.set_caption(SCREEN_TITLE)
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

	def MainLoop(self):
		global PELLET_X, PELLET_Y

		if MAP == 1:
			PELLET_X = 1400
			PELLET_Y = SCREEN_HEIGHT // 2
		elif MAP == 2:
			PELLET_X = 1600
			PELLET_Y = SCREEN_HEIGHT // 2
		else:
			PELLET_X = random.randrange(700, 1700 + 1, 200)
			PELLET_Y = random.randrange(100, 900 + 1, 100)

		# Carrega os objetos da cena.
		self.LoadSprites()
		
		# Criando o background. 
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((100, 100, 100))

		# Variaveis auxiliares.
		self.gen = 0 # Geração atual.
		self.turn = 0 # Turno atual.

		# Conjunto de indivíduos mortos e vencedores.
		self.dead_organisms = {}
		self.winner_organisms = {}

		# Desenha background.
		self.screen.blit(self.background, (0, 0))

		# Reseta os indivíduos para o estado inicial.
		for s in self.organism_sprites.sprites():
			s.reset()

		# Game loop.
		while True:
			# Para sair.
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

			# Desenha background.
			if not SHOW_TRAIL:
				self.screen.blit(self.background, (0, 0))
			
			# Se a geração atual acabou.
			if self.end_of_generation():
				# Desenha background.
				self.screen.blit(self.background, (0, 0))

				# Reseta os turnos e incrementa a geração.
				self.turn = 0
				self.gen += 1

				# Realiza a seleção da Elite.
				self.select()

				# Imprime informações no terminal.
				self.print_terminal()

				# Realiza a geração da população.
				self.generate()

				# Reseta os indivíduos para o estado inicial.
				for s in self.organism_sprites.sprites():
					s.reset()

			# Realiza os movimentos dos indivíduos.
			for s in self.organism_sprites.sprites():
				s.move(self.turn)

			# Detectando colisões.
			self.collide()

			# Desenhando na tela.
			self.draw()

			# Incrementando o turno atual.
			self.turn += 1

	# Realiza impressões auxiliares no terminal.
	def print_terminal(self):
		# Imprime a geração atual e um rank com os 10 melhores fitness.
		print("Generation: %d" % self.gen)

		for i in range (0, 10):
			print("\t%d) Fitness = %.2f" % (i + 1, self.organism_list[i].fitness))

	# Verifica se a geração acabou.
	def end_of_generation(self):
		return self.turn == MAX_TURNS or len(self.dead_organisms) + len(self.winner_organisms) == POPULATION_SIZE

	# Realiza a geração de uma população.
	def generate(self):
		# Gera toda a população usando apenas a elite.
		for i in range(ELITE_SIZE, POPULATION_SIZE):
			# Aleatoriza dois indivíduos da elite (podem ser o mesmo).
			p1 = random.randint(0, ELITE_SIZE - 1)
			p2 = random.randint(0, ELITE_SIZE - 1)

			# Substituindo a Plebe com os filhos da Elite
			self.organism_list[i].make_child(self.organism_list[p1], self.organism_list[p2])

	# Realiza a seleção (ordenação por fitness e promoção da Plebe)
	def select(self):
		# Calcula o fitness de cada indivíduo.
		for i in self.organism_list:
			i.update_fitness()

		# Ordena decrescente pelo fitness.
		self.organism_list.sort(key=lambda x: x.fitness, reverse=True)

		# Troca 2 da Elite por 2 da Plebe.
		for i in range(5, ELITE_SIZE):
			p = random.randint(ELITE_SIZE, CANDIDATES)
			self.organism_list[i], self.organism_list[p] = self.organism_list[p], self.organism_list[i]


	# Desenha um frame na tela.
	def draw(self):
		# Desenha os sprites.
		self.pellet_sprites.draw(self.screen)
		self.organism_sprites.draw(self.screen)

		# Pintando a Plebe.
		for i in range(ELITE_SIZE, POPULATION_SIZE):
			org = self.organism_list[i]
			pygame.draw.polygon(org.original_image, org.color, [(0, 0), (0, org.height), (org.width, org.height // 2)])

		# Pintando a Elite.
		for i in range(ELITE_SIZE):
			org = self.organism_list[i]
			pygame.draw.polygon(org.original_image, (0, 215, 255), [(0, 0), (0, org.height), (org.width, org.height // 2)])

		# Desenhando as paredes.
		self.wall_sprites.draw(self.screen)

		# Imprimindo texto na tela.
		font = pygame.font.SysFont("Arial", 36)
		text = font.render("Generation: %d" % (self.gen), True, (0, 180, 0))
		self.screen.blit(text, (10, 10))
		text = font.render("Fitness: %.2f" % (self.organism_list[0].fitness), True, (0, 180, 0))
		self.screen.blit(text, (10, 50))

		# Só pinta o turno se não tiver com o trail ativado.
		if not SHOW_TRAIL:
			text = font.render("Turn: %d" % (self.turn), True, (0, 180, 0))
			self.screen.blit(text, (10, 90))

		# Atualizando a tela.
		pygame.display.flip()

	# Realiza as colisões.
	def collide(self):
		# Verifica colisão com o objetivo.
		self.winner_organisms = pygame.sprite.spritecollide(self.pellet, self.organism_sprites, False)

		# Verifica colisão com as paredes.
		self.dead_organisms = pygame.sprite.groupcollide(self.organism_sprites, self.wall_sprites, False, False)

		# Parando a movimentaçao dos indivíduos mortos.
		for dead in self.dead_organisms:
			dead.state = DEAD

		# Parando a movimentaçao dos indivíduos vencedores.
		for winner in self.winner_organisms:
			winner.state = WINNER

	# Carrega os desenhos iniciais.
	def LoadSprites(self):
		# Gerando o objetivo.
		self.pellet = Pellet(PELLET_X, PELLET_Y, PELLET_RADIUS)

		# Adiciona o objetivo ao conjunto de sprites.
		self.pellet_sprites = pygame.sprite.RenderPlain(self.pellet)

		# Cria um grupo de indivíduos.
		self.organism_sprites = pygame.sprite.Group()

		# Lista com os indivíduos.
		self.organism_list = [Organism(random.uniform(MIN_MUTATION, MAX_MUTATION)) for i in range(POPULATION_SIZE)]

		# Adicionando os indivíduos ao conjunto de sprites.
		for i in self.organism_list:
			self.organism_sprites.add(i)

		# Desenhando as bordas.
		self.wall_sprites = pygame.sprite.Group()

		# Upper border.
		self.wall_sprites.add(Wall(0, 0, 0, SCREEN_WIDTH, BORDER_WIDTH, BLACK))

		# Lower border.
		self.wall_sprites.add(Wall(0, SCREEN_HEIGHT - BORDER_WIDTH, 0, SCREEN_WIDTH, BORDER_WIDTH, BLACK))

		# Left border.
		self.wall_sprites.add(Wall(0, 0, 0, BORDER_WIDTH, SCREEN_HEIGHT, BLACK))

		# Right border.
		self.wall_sprites.add(Wall(SCREEN_WIDTH - BORDER_WIDTH, 0, 0, BORDER_WIDTH, SCREEN_HEIGHT, BLACK))

		# Gerando o mapa.
		if MAP == RANDOM_MAP:
			self.randomize_map()
		elif MAP == 1:
			self.map1()
		elif MAP == 2:
			self.map2()
		else:
			print("No such map")
			sys.exit()

	# Mapa de teste com máximos locais.
	def map1(self):
		self.wall_sprites.add(Wall(500, 0, 0, 50, 400))
		self.wall_sprites.add(Wall(500, SCREEN_HEIGHT - 400, 0, 50, 400))

		self.wall_sprites.add(Wall(700, 100, 0, 50, SCREEN_HEIGHT - 200))

		self.wall_sprites.add(Wall(900, 0, 0, 50, 400))
		self.wall_sprites.add(Wall(900, SCREEN_HEIGHT - 400, 0, 50, 400))

		self.wall_sprites.add(Wall(1100, 100, 0, 50, SCREEN_HEIGHT - 200))

	# Mapa com o objetivo quase trancado.
	def map2(self):
		# Caminho
		self.wall_sprites.add(Wall(300, 0, 0, 50, 450))
		self.wall_sprites.add(Wall(300, SCREEN_HEIGHT - 450, 0, 50, 450))

		self.wall_sprites.add(Wall(300, 400, 0, 300, 50))
		self.wall_sprites.add(Wall(300, SCREEN_HEIGHT - 450, 0, 450, 50))

		self.wall_sprites.add(Wall(550, 0, 0, 50, 450))
		self.wall_sprites.add(Wall(700, 100, 0, 50, 450))

		self.wall_sprites.add(Wall(850, 0, 0, 50, 450))

		self.wall_sprites.add(Wall(700, SCREEN_HEIGHT - 450, 0, 950, 50))
		self.wall_sprites.add(Wall(850, 400, 0, 800, 50))
	
		# Gaiola
		self.wall_sprites.add(Wall(1650, 400, 0, 50, 200))

		self.wall_sprites.add(Wall(1500, 400, 0, 50, 80))
		self.wall_sprites.add(Wall(1500, 520, 0, 50, 80))

	# Aleatoriza um mapa.
	def randomize_map(self):
		pos_x = [i for i in range(200, SCREEN_WIDTH + 1, 200)]
		pos_y = [i for i in range(0, SCREEN_HEIGHT - 200 + 1, 200)]

		for i in pos_x:
			k = 0

			for j in pos_y:
				if random.random() < 0.5 and k < len(pos_y) - 1:
					k += 1
					self.wall_sprites.add(Wall(i, j, 0, 50, 200))

# Classe do indivíduo (triangulo)
class Organism(pygame.sprite.Sprite):
	# Construtor
	def __init__(self, mutation):
		# Construtor do pai.
		super().__init__()

		# Atributos do indivíduo.
		self.x = INITIAL_X
		self.y = INITIAL_Y
		self.angle = random.uniform(-math.pi, math.pi)
		self.width = 32
		self.height = 16
		self.mutation = mutation
		self.state = ALIVE
		self.genome = [random.uniform(-MAX_TURN, MAX_TURN) for i in range(MAX_TURNS)]
		self.fitness = 0

		# Calculo da cor de acordo com a mutação
		self.color = get_color(mutation) 		

		# Desenhando o indivíduo.
		self.original_image = pygame.Surface([self.width, self.height])
		self.original_image.fill(WHITE)
		self.original_image.set_colorkey(WHITE)
		pygame.draw.polygon(self.original_image, self.color, [(0, 0), (0, self.height), (self.width, self.height // 2)])
		
		# Retângulo com as mesmas dimensões da imagem.
		self.rect = self.original_image.get_rect()
		self.image = self.original_image # Original image é usado para as transformações

		# Movendo para a posição inicial.
		self.rect.move_ip(self.x, self.y)

		# Diminuindo tamanho da collision box.
		self.rect.inflate_ip(-5, -5)

	# Funçao de movimento do indivíduo.
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

			# Calculo do x, y
			xMove = STEP * math.cos(self.angle)
			yMove = STEP * math.sin(self.angle)

			# Realiza movimento e a rotação do objeto..
			self.rect.move_ip(xMove, yMove)
			self.image = pygame.transform.rotate(self.original_image, -math.degrees(self.angle))

	# Função que calcula o fitness de cada indivíduo
	def update_fitness(self):
		# O fitness inicial é a distância inicial.
		self.fitness = distance((INITIAL_X, INITIAL_Y), (PELLET_X, PELLET_Y))

		# Bônus caso tenha alcançado o objetivo
		if self.state == WINNER:
			self.fitness *= (3 - self.time_to_min_dist / MAX_TURNS)
		else:
			# Leva em consideração:
			# 	- A distância final ao objetivo
			# 	- A distância mínima ao objetivo
			# 	- A distância final ao ponto de partida
			# 	- O tempo até a morte (ou até chegar ao objetivo)
			self.fitness -= 0.4 * self.dist
			self.fitness -= 0.2 * self.min_dist
			self.fitness += 0.4 * self.time_to_dist * (self.dist_initial / distance((INITIAL_X, INITIAL_Y), (PELLET_X, PELLET_Y)))
			self.fitness += 0.25 * self.dist_initial

			if self.state == ALIVE:
				self.fitness *= 0.5

	# Volta o indivíduo para a posição original, estado e ângulo.
	def reset(self):
		self.rect.move_ip(self.x - self.rect.x, self.y - self.rect.y);
		self.state = ALIVE
		self.angle = 0
		self.dist = self.min_dist = distance((self.rect.x, self.rect.y), (PELLET_X, PELLET_Y))
		self.dist_initial = 0
		self.time_to_dist = self.time_to_min_dist = -1

	# Realiza o cruzamento entre dois indivíduos e salva no atual
	def make_child(self, mom, dad):
		if random.random() < (1 + self.mutation) * CHANCE_TO_RESET_GENOME: # Reset total do genoma.
			self.genome = [random.uniform(-MAX_TURN, MAX_TURN) for i in range(MAX_TURNS)]
		else:
			# 50% de chance de um genome[i] vir da mãe e 50% de chance de vir do pai.
			self.genome = [dad.genome[i] if random.random() < 0.5 else mom.genome[i] for i in range(MAX_TURNS)]

			# Chance de ser um seguidor da Elite.
			if random.random() < CHANCE_TO_MUTATE_AT_DEATH:
				# Se for um seguidor, ele deve começar a mutação pouco antes dos seus pais morrerem.
				s = max(0, min(mom.time_to_dist, dad.time_to_dist) - random.randint(MIN_ROLLBACK, MAX_ROLLBACK))
			else:
				s = 0

			# Mutação.
			for i in range(s, MAX_TURNS):
				# Mutação variável com o tempo i.
				if random.random() < self.mutation * (1 + (2 * i / MAX_TURNS)):
					# Chance de apenas inverter o sentido da curva.
					if random.random() < 0.5:
						self.genome[i] = random.uniform(-MAX_TURN, MAX_TURN)
					else:
						self.genome[i] = -self.genome[i]

# Objetivo.
class Pellet(pygame.sprite.Sprite):
	# Construtor.
	def __init__(self, x, y, radius = 32, color = YELLOW):
		# Construtor do pai.
		super().__init__()

		# Atributos do objetivo.
		self.x = x - radius
		self.y = y - radius
		self.radius = radius
		self.color = color
		
		# Desenhando o objetivo.
		self.image = pygame.Surface((2 * self.radius, 2 * self.radius))
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE) 
		pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

		# Retângulo com as mesmas dimensões da imagem.
		self.rect = self.image.get_rect()

		# Diminuindo a hitbox.
		self.rect.inflate_ip(-5, -5)	

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
		
		# Desenhando a parede.
		self.image = pygame.Surface((width, height))
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE)
		pygame.draw.polygon(self.image, color, [(0, 0), (0, height),(width, height), (width, 0)], 0)

		# Retângulo com as mesmas dimensões da imagem.
		self.rect = self.image.get_rect()
		
		# Movendo para a posição inicial.
		self.rect.move_ip(x, y)

# Chamada da main.
if __name__ == "__main__":
	MainWindow = Main()
	MainWindow.MainLoop()
