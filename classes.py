import math

class Board:
	def __init__(self, dim, gridL=50):
		# Since x=y, tuple contains x0 and x1 (or, y0 and y1)
		self.dim = self.gameDimensions(dim[0])
		# Is this correct grid implementation?
		self.grid = [[None] * gridL for i in range(gridL)]
		self.player = Player((dim[0] / 2, (4 * dim[1]) / 5))
		self.cores = self.initCores()
		self.obstacles = set()
		# Entities that can be destroyed
		self.enemies = set()
	
	def gameDimensions(self, l):
		margin = l / 10
		return (margin, l - margin)
	
	def determineGrid(self):
		pass

	def initCores(self):
		return set()

	def gameWon(self):
		return (len(self.cores) == 0)

class Player:
	imgPath = "assets/player.png"

	def __init__(self, pos):
		self.pos = pos
		self.rot = 0
		self.health = 3
		self.projs = set()
		self.timeDelay = 0

	def move(self, x1, y1):
		x0, y0 = self.pos[0], self.pos[1]
		self.pos = (x0 + x1, y0 + y1)
		# Returns original position in case movement must be undone
		return (x0, y0)
	
	def rotate(self, d1):
		self.rot = (self.rot + d1) % 360
		if(self.rot < 0):
			self.rot = 360 + self.rot

	def createProjectile(self, l):
		if(self.timeDelay > 0):
			return

		# Modifies angle starting position to reflect typical unit circle
		rot = (90 + self.rot) % 360
		# Uses Law of Sines to calculate vector components
		vx = math.sin(math.radians(90 - rot)) * l
		vy = math.sin(math.radians(rot)) * l
		# Slope of projectile vector, represented as rise-run tuple
		# vy is negative since canvas y-direction is inverted from standard Cartesian plane
		m = (-vy, vx) 

		# Determines position of origin (should be player tip)
		pos = self.pos # placeholder value for debug
		proj = PlayerProjectile(pos, m, self.rot)
		self.projs.add(proj)
		# timerFired() delay before projectile can be created
		self.timeDelay = 2

	def deductHealth(self):
		self.health -= 1
		return (self.health > 0)

	def area():
		# top triangle: 0.7/1.0
		# bottom triangle: 0.3/1.0
		pass

	def detectCollision(self, pos):
		pass

class Projectile:
	def __init__(self, pos, m, rot):
		self.pos = pos
		self.m = m
		self.rot = rot
		self.lifespan = 10

	def move(self):
		x0, y0 = self.pos[0], self.pos[1]
		self.pos = (x0 + self.m[1], y0 + self.m[0])

class PlayerProjectile(Projectile):
	imgPath = "assets/playerProjectile.png"

	def __init__(self, pos, m, rot):
		super().__init__(pos, m, rot)

class OrangeProjectile(Projectile):
	imgPath = "assets/oProjectile.png"

	def __init__(self, pos, m, rot):
		super().__init__(pos, m, rot)
		self.health = 1

class PurpleProjectile(Projectile):
	imgPath = "assets/pProjectile.png"

	def __init__(self, pos, m, rot):
		super().__init__(pos, m, rot)

class Core:
	imgPath = "assets/core.png"

	def __init__(self, pos):
		self.pos = pos
		self.health = 5
	
	def evade(self, pos=None):
		if(not pos):
			pos = self.pos
		# recursive function finding furthest single legal move away from block
		# runs each "turn" until is safely set distance apart
		pass

class ShieldedCore(Core):
	imgPath = "assets/sCore.png"

	def __init__(self, pos):
		super().__init__(pos)
		self.shield = True

	def destroyShield(self):
		self.shield = False
		imgPath = super().imgPath

class Block:
	imgPath = "assets/block.png"

	def __init__(self):
		pass

class DestructableBlock(Block):
	imgPath = "assets/dBlock.png"

	def __init__(self):
		super().__init__()
		self.health = 5 # arbitrary number

class EnemyBlock(Block):
	imgPath = "assets/eBlock.png"

class Enemy:
	imgPath = "assets/enemy.png"

	def __init__(self, pos):
		self.pos = pos
		self.rot = 0
		# Is a variable necessary? They are defeated after a single projectile collision.
		self.health = 1
		self.projs = set()

	# Enemy should always face player
	def orientation(self, pos):
		x0, y0 = self.pos[0], self.pos[1] # Enemy
		x1, y1 = pos[0], pos[1] # Player
		# Determine rotation angle from line drawn between enemy and player position
		a = x1 - x0
		b = y0 - y1 # y0 and y1 swapped since downwards is positive
		c = math.sqrt(a**2 + b**2)
		# Prevents division by zero
		if(a == 0):
			self.rot = 180 if (b < 0) else 0
			return
		# Law of Cosines angle calculation
		rot = math.degrees(math.acos((a**2 + c**2 - b**2) / (2 * a * c)))
		self.rot = ((-1 * (rot + 90)) if (b < 0) else (rot - 90)) % 360