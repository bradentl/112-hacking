import time
import math
import random

class Board:
	def __init__(self, dim, gridL=50):
		# Since x=y, tuple contains x0 and x1 (or, y0 and y1)
		self.dim = self.gameDimensions(dim[0])
		self.player = Player((dim[0] / 2, (4 * dim[1]) / 5))
		self.cores = self.initCores(dim)
		self.blocks = {"block": set(), "dBlock": set(),"eBlock": set()}
		self.enemies = self.initEnemies()
		# 1 minute time limit
		self.time = time.time() + 60
	
	def gameDimensions(self, l):
		margin = l / 10
		return (margin, l - margin)

	def initCores(self, dim):
		core = ShieldedCore(dim)
		return {core}
	
	def initEnemies(self):
		return set()

	def isLegalMove(self, pos, dim=(0,0)):
		# Ensure object is within board dimensions
		if(pos[0] < (self.dim[0] + (dim[0] / 2)) or pos[1] < (self.dim[0] + (dim[1] / 2)) or 
		   pos[0] > (self.dim[1] - (dim[0] / 2)) or pos[1] > (self.dim[1] - (dim[1] / 2))):
			return False
		return True
	
	# After projectile moves, method is called to test for collisions.
	# Method gathers all neccesary elements to test for collision and passes them to detectCollision()
	def collisionManager(self, collider, exclusions=None):
		# Following the separation axis theorem, determine possible dividing axes
		dividingAxes = collider.collisionAxes()

		for enemy in self.enemies:
			self.detectCollision(enemy.projs)

	def polygonIntersection(self):
		pass

	def circleIntersection(self, axes):
		# If every axis intersects, both objects intersect.
		if(len(axes) == 0):
			return True
		else:
			pass

	# Using the Separating Axis theorem...
	#  - If two convex polygons are not intersecting, there exists a line that passes between them.
	#  - Such a line only exists if one of the sides of one of the polygons forms such a line.
	def detectCollision(self, collider, testEntities):
		if(len(testEntities) == 0):
			return False
		else:
			pass

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
		# Returns boolean indicating whether player has lost
		return (self.health > 0)
	
	def toggleTarget(self, enemies=set(), cores=set()):
		if(self.target):
			self.target = None
			return
		self.determineTarget(enemies, cores)

	def determineTarget(self, enemies=set(), cores=set()):
		# Only targets cores if there are no enemies to target
		targets = list(cores if (len(enemies) == 0) else enemies)

		# If there's nothing to target, reset target value and return.
		# (Technically there would always be something to target otherwise the game would end,
		# but its best to err on the side of caution and prevent crashes.)
		if(len(targets) == 0):
			self.target = None
			return

		def distance(x1, y1):
			return math.sqrt((self.pos[0] - x1)**2 + (self.pos[1] - y1)**2)
		# Creates a list of the distance between player and each possible target
		enemyDistance = [distance(e.pos[0], e.pos[1]) for e in targets]
		# Since enemyDistance has same order as targets, determine shortest length and use
		# the index to determine the appropriate element.
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

	# Behavior if collides with projectile
	def collisionBehavior(self):
		self.health -= 1


class Projectile:
	def __init__(self, pos, m, rot=0):
		self.pos = pos
		self.m = m
		self.rot = rot
		self.lifespan = 15

	def move(self):
		x0, y0 = self.pos[0], self.pos[1]
		self.pos = (x0 + self.m[1], y0 + self.m[0])
		# Unlike Player.move(), there is no return since projectiles can leave the board.
		# Additionally, when they hit obstacles they simply despawn.
	
	def isOffscreen(self, sDim):
		if(self.pos[0] < 0 or self.pos[1] < 0 or 
		   self.pos[0] > sDim[0] or self.pos[1] > sDim[1]):
			return True
		return False

class PlayerProjectile(Projectile):
	imgPath = "assets/playerProjectile.png"

	def __init__(self, pos, m, rot):
		super().__init__(pos, m, rot)
	
	# Rectangle should have two possible dividing axes.
	def collisionAxes(self):
		rot = (-self.rot % 90)
		axes = set()
		if(rot == 0):
			# Values formatted in tuple as ((rise, run), b)
			# Provides all necessary constants for y = mx + b
			pass

class OrangeProjectile(Projectile):
	imgPath = "assets/oProjectile.png"

	def __init__(self, pos, m):
		super().__init__(pos, m)
		self.health = 1
		# Longer lifespan since they move slower
		self.lifespan = self.lifespan * 2

class PurpleProjectile(Projectile):
	imgPath = "assets/pProjectile.png"

	def __init__(self, pos, m):
		super().__init__(pos, m)
		self.lifespan = self.lifespan * 2

class Core:
	imgPath = "assets/core.png"

	def __init__(self, bDim):
		self.pattern = random.randint(0,2)
		self.pos = self.posFromPattern(bDim)
		self.health = 5
		self.projs = set()
		# Angle of projectile fire
		self.deg = 0
		self.pType = True
		self.firingDelay = 0
	
	def posFromPattern(self, bDim):
		match self.pattern:
			case _: return (bDim[0] / 2, bDim[1] / 2)
	
	def evade(self, pPos, pos=None):
		if(not pos):
			pos = self.pos
		# Backtracking function determining furthest single legal move away from block
		# runs each "turn" until is safely set distance apart
		d = math.sqrt((pos[0] - pPos[0])**2 + (pos[1] - pPos[1])**2)
		safeDistance = 0 # safe distance should change depending on scale
		if(d > safeDistance):
			# Continue typical movement pattern
			# return functionForTypicalMovement()
			pass
		else:
			# recursive backtracking
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
		m = (self.m[0] / 3, self.m[1] / 3)
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
			return 180 if (b < 0) else 0
		# Law of Cosines angle calculation
		rot = math.degrees(math.acos((a**2 + c**2 - b**2) / (2 * a * c)))
		rot = ((-1 * (rot + 90)) if (b < 0) else (rot - 90)) % 360
		return rot

	def firingPattern(self, l, pPos):
		if(self.firingDelay > 0):
			return
		
		pType = self.pType

		# Various firing patterns for variety
		match self.pattern:
			case 1:
				for deg in range(self.deg, self.deg + 360, 60):
					self.createProjectile(deg, l, pType)
					pType = not pType
				self.pType = not pType
				self.deg += 10
				self.firingDelay = 7
			case 2:
				deg = self.angleToPlayer(pPos)
				for adj in range(-20, 21, 20):
					self.pType = not self.pType
					self.createProjectile(deg + adj, l, self.pType)
				self.firingDelay = 8
			case _:
				for deg in range(0, 360, 45):
					self.createProjectile(deg, l, pType)
					pType = not pType
				self.pType = not self.pType
				self.firingDelay = 10
	
	def collisionBehavior(self):
		pass

class ShieldedCore(Core):
	imgPath = "assets/sCore.png"

	def __init__(self, pos):
		super().__init__(pos)
		self.shield = True

	def destroyShield(self):
		self.shield = False
	
	def collisionBehavior(self):
		if(not self.shield):
			return super().collisionBehavior()
		pass	

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
		# Determines which direction to turn
		neg = -1 if (self.rot - rot > 0) else 1
		# Corrects 180˚-360˚ angles
		neg = neg * (-1 if (abs(self.rot - rot) > 180) else 1)
		# If degree of difference in angle is reasonably small, turn at a smaller interval.
		# This prevents shakiness and stabilizes visuals.
		turn = 4 if (abs(self.rot - rot) > 2) else 1
		self.rot = (self.rot + (neg * turn)) % 360
	
	def createProjectile(self):
		# Values here are reduced by factor to slow projectiles down from standard speed
		m = (self.m[0] / 3, self.m[1] / 3)
		# Determines which type of projectile to add
		proj = OrangeProjectile(self.pos, m)
		self.projs.add(proj)
		self.firingDelay = 15
	
	def autoFire(self):
		if(self.firingDelay > 0):
			return
		self.createProjectile()