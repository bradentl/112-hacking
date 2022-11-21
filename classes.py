import math
import random

class Board:
	def __init__(self, dim, sCoreDim, gridL=50):
		# Since x=y, tuple contains x0 and x1 (or, y0 and y1)
		self.dim = self.gameDimensions(dim[0])
		# Is this correct grid implementation?
		self.grid = [[None] * gridL for i in range(gridL)]
		self.player = Player((dim[0] / 2, (4 * dim[1]) / 5))
		self.cores = self.initCores(sCoreDim)
		self.obstacles = set()
		# Entities that can be destroyed
		self.enemies = self.initEnemies()
	
	def gameDimensions(self, l):
		margin = l / 10
		return (margin, l - margin)
	
	def determineGrid(self):
		pass

	def initCores(self, dim):
		x = self.dim[0] + (dim / 2)
		core = ShieldedCore((x, x))
		return {core}
	
	def initEnemies(self):
		return set()

	def isLegalMove(self, pos, dim=0):
		if(pos[0] < (self.dim[0] + (dim[0] / 2)) or pos[1] < (self.dim[0] + (dim[1] / 2)) or 
		   pos[0] > (self.dim[1] - (dim[0] / 2)) or pos[1] > (self.dim[1] - (dim[1] / 2))):
			return False
		return True

	def gameWon(self):
		return (len(self.cores) == 0)

class Player:
	imgPath = "assets/player.png"

	def __init__(self, pos):
		self.pos = pos
		self.rot = 0
		self.health = 3
		self.projs = set()
		self.firingDelay = 0
		# Implement targeting system
		self.target = None

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
		if(self.firingDelay > 0):
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
		self.firingDelay = 2

	def deductHealth(self):
		self.health -= 1
		return (self.health > 0)

	def determineTarget(self, enemies=set(), cores=set()):
		targets = list(cores if (len(enemies) == 0) else enemies)
		# Toggles targeting
		if(self.target or len(targets) == 0):
			self.target = None
			return

		def distance(x1, y1):
			return math.sqrt((self.pos[0] - x1)**2 + (self.pos[1] - y1)**2)
		enemyDistance = [distance(e.pos[0], e.pos[1]) for e in targets]

		self.target = targets[enemyDistance.index(min(enemyDistance))]
	
	def autoOrient(self):
		x0, y0 = self.pos[0], self.pos[1]
		x1, y1 = self.target.pos[0], self.target.pos[1]
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

	def area():
		# top triangle: 0.7/1.0
		# bottom triangle: 0.3/1.0
		pass

	def detectCollision(self, pos):
		pass

class Projectile:
	def __init__(self, pos, m, rot=0):
		self.pos = pos
		self.m = m
		self.rot = rot
		self.lifespan = 15

	def move(self):
		x0, y0 = self.pos[0], self.pos[1]
		self.pos = (x0 + self.m[1], y0 + self.m[0])

class PlayerProjectile(Projectile):
	imgPath = "assets/playerProjectile.png"

	def __init__(self, pos, m, rot):
		super().__init__(pos, m, rot)

class OrangeProjectile(Projectile):
	imgPath = "assets/oProjectile.png"

	def __init__(self, pos, m):
		super().__init__(pos, m)
		self.health = 1
		self.lifespan = self.lifespan * 2

class PurpleProjectile(Projectile):
	imgPath = "assets/pProjectile.png"

	def __init__(self, pos, m):
		super().__init__(pos, m)
		self.lifespan = self.lifespan * 2

class Core:
	imgPath = "assets/core.png"

	def __init__(self, pos):
		self.pos = pos
		self.health = 5
		self.projs = set()
		self.firingDelay = 0
	
	def evade(self, pos=None):
		if(not pos):
			pos = self.pos
		# backtracking function finding furthest single legal move away from block
		# runs each "turn" until is safely set distance apart
		pass

	def createProjectile(self, deg, l, pType=True):
		# Define slope from angle
		rot = (90 + deg) % 360
		vx = math.sin(math.radians(90 - rot)) * l
		vy = math.sin(math.radians(rot)) * l
		# Slope of projectile vector, represented as rise-run tuple
		# vy is negative since canvas y-direction is inverted from standard Cartesian plane
		self.m = (-vy, vx)
		# Values here are reduced by factor to slow projectiles down from standard speed
		m = (self.m[0] / 2.5, self.m[1] / 2.5)
		# Determines which type of projectile to add
		proj = OrangeProjectile(self.pos, m) if pType else PurpleProjectile(self.pos, m)
		self.projs.add(proj)
	
	def angleToPlayer(self, pPos):
		x0, y0 = self.pos[0], self.pos[1] # Enemy
		x1, y1 = pPos[0], pPos[1] # Player
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
		rot = ((-1 * (rot + 90)) if (b < 0) else (rot - 90)) % 360
		return rot

	def firingPattern(self, pattern, l, pPos=None, pType=True):
		if(self.firingDelay > 0):
			return

		match pattern:
			case 1:
				pass
			case 2:
				deg = self.angleToPlayer(pPos)
				self.createProjectile(deg - 20, l)
				self.createProjectile(deg, l)
				self.createProjectile(deg + 20, l)
				self.firingDelay = 3
			case _:
				for deg in range(0, 360, 45):
					self.createProjectile(deg, l, pType)
					pType = not pType
				self.firingDelay = 10

class ShieldedCore(Core):
	imgPath = "assets/sCore.png"

	def __init__(self, pos):
		super().__init__(pos)
		self.shield = True

	def destroyShield(self):
		self.shield = False

class Block:
	imgPath = "assets/block.png"

	def __init__(self, pos):
		self.pos = pos

class DestructableBlock(Block):
	imgPath = "assets/dBlock.png"

	def __init__(self, pos):
		super().__init__(pos)
		self.health = 5 # arbitrary number

class EnemyBlock(Block):
	imgPath = "assets/eBlock.png"

	def __init__(self, pos):
		super().__init__(pos)

class Enemy:
	imgPath = "assets/enemy.png"

	def __init__(self, pos):
		self.pos = pos
		self.rot = 180
		# Is a variable necessary? They are defeated after a single projectile collision.
		self.health = 1
		self.m = (0, 0)
		self.projs = set()
		self.firingDelay = 0
	
	# Slowly move forwards according to orientation
	def follow(self, pPos, l):
		self.orient(pPos)
		# Modifies angle starting position to reflect typical unit circle
		rot = (90 + self.rot) % 360
		# Uses Law of Sines to calculate vector components
		vx = math.sin(math.radians(90 - rot)) * l
		vy = math.sin(math.radians(rot)) * l
		# Slope of projectile vector, represented as rise-run tuple
		# vy is negative since canvas y-direction is inverted from standard Cartesian plane
		self.m = (-vy, vx)
		pos = self.pos
		self.pos = (pos[0] + (self.m[1] / 20), pos[1] + (self.m[0] / 20))
		return pos

	# Enemy should slowly turn to face player
	def orient(self, pos):
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
		rot = ((-1 * (rot + 90)) if (b < 0) else (rot - 90)) % 360
		print(self.rot - rot)
		if((self.rot - rot) < 0):
			self.rot += 5
		else:
			self.rot -= 5
	
	def createProjectile(self):
		# Values here are reduced by factor to slow projectiles down from standard speed
		m = (self.m[0] / 2.5, self.m[1] / 2.5)
		# Determines which type of projectile to add
		proj = OrangeProjectile(self.pos, m)
		self.projs.add(proj)
		self.firingDelay = 15
	
	def autoFire(self):
		if(self.firingDelay > 0):
			return
		self.createProjectile()
	
	def firingPattern(self, patternType):
		pass