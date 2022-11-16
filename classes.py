import math

class Board:
	def __init__(self, dim):
		self.dim = dim[0] / 10
		self.player = Player((dim[0] / 2, (4 * dim[1]) / 5))
		self.cores = set()
		self.blocks = set()

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
		print(self.pos)
	
	def rotate(self, d1):
		self.rot = (self.rot + d1) % 360
		if(self.rot < 0):
			self.rot = 360 + self.rot

	def createProjectile(self, l):
		if(self.timeDelay > 0):
			return

		if(self.rot % 180 == 0):
			m = (-l, 0) if (self.rot == 0) else (l, 0)
		else:
			# Modifies angle starting position to reflect typical unit circle
			rot = (90 + self.rot) % 360
			# Uses Law of Sines to calculate vector components
			vx = math.sin(math.radians(90 - rot)) * l
			vy = math.sin(math.radians(rot)) * l
			# Determine positive/negative direction depending on quadrant
			pass
			# Slope of projectile vector, represented as rise-run tuple
			# vy is negative since canvas y-direction is inverted from standard Cartesian plane
			m = (-vy, vx) 
		pos = self.pos # placeholder value for debug
		proj = PlayerProjectile(pos, m, self.rot)
		self.projs.add(proj)
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

	def __init__(self, shield):
		self.health = 5
		self.shield = shield

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