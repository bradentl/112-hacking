class Board:
	def __init__(self, dim):
		self.dim = dim
		self.player = Player((dim[0] / 2, dim[1] / 2))
		self.cores = set()
		self.blocks = set()

class Player:
	imgPath = "assets/player.png"

	def __init__(self, pos):
		self.pos = pos
		self.rot = 0
		self.health = 3
		self.projectiles = set()

	def move(self, x1, y1):
		x0, y0 = self.pos[0], self.pos[1]
		self.pos = (x0 + x1, y0 + y1)
		print(self.pos)
	
	def rotate(self, d1):
		self.rot = (self.rot + d1) % 360
		if(self.rot < 0):
			self.rot = 360 + self.rot

	def area():
		# top triangle: 0.7/1.0
		# bottom triangle: 0.3/1.0
		pass

	def detectCollision(self, pos):
		pass

	def deductHealth(self):
		self.health -= 1
		return (self.health > 0)

class Projectile:
	def __init__(self, pos, vel):
		pass

class PlayerProjectile(Projectile):
	imgPath = ""

	def __init__(self, pos, vel):
		pass

class OrangeProjectile(Projectile):
	imgPath = ""

	def __init__(self):
		self.health = 1

class BlackProjectile(Projectile):
	pass

class EnemyCore:
	imgPath = ""

	def __init__(self, shield):
		self.health = 5
		self.shield = shield

class Block:
	imgPath = ""

	def __init__(self):
		pass

class DestructableBlock(Block):
	imgPath = ""

	def __init__(self):
		super().__init__()
		self.health = 5 # arbitrary number

class EnemyBlock(Block):
	imgPath = ""