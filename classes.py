import math
import time
import random
import numpy as np

class Board:
	def __init__(self, app, difficulty=5):
		# Since x=y, tuple contains x0 and x1 (or, y0 and y1)
		self.dim = self.gameDimensions(app.width)
		self.player = self.initPlayer(app)
		self.cores = self.initCores(app)
		self.blocks = {"block": set(), "dBlock": set(),"eBlock": set()}
		self.enemies = set()
		self.populateBoard(app)
		# Time limit set to arbitrary number for debugging
		self.time = time.time() + 60
	
	def gameDimensions(self, l):
		margin = l / 10
		return (margin, l - margin)
	
	def populateBoard(self, app):
		# Scaling calculations ensure block dimensions are 25x25
		l = int((self.dim[1] - self.dim[0]) / 25)
		# https://numpy.org/doc/stable/user/absolute_beginners.html
		randBoard = np.random.randint(0, 100, size=(l, l))
		print(randBoard)

		ratio = {"empty":80, "block":19, "enemy":1}
		# Transforms the majority of squares to empty
		prev = (0, 0)
		for division in ratio:
			print(prev[1] + ratio[division])
			randBoard[(prev[1] <= randBoard) & (randBoard < (prev[1] + ratio[division]))] = prev[0]
			prev = (prev[0] + 1, prev[1] + ratio[division])
		print(randBoard)

		def adjacentSquares(index, testedIndices=set()):
			foundIndices = set()
			testedIndices.add(index)
			
			bound = lambda i : max(0, min(i, l - 1))
			# Orthogonal adjacent squares
			orthAdjs = {(index[0], bound(index[1] - 1)),
						(index[0], bound(index[1] + 1)),
						(bound(index[0] - 1), index[1]),
						(bound(index[0] + 1), index[1])
			}

			row, col = index[0], index[1]
			for square in orthAdjs:
				if(square in testedIndices or square in foundIndices):
					continue

				if(randBoard[row][col] == randBoard[square[0]][square[1]]):
					foundIndices.add(index)
					foundIndices.add(square)
					result = adjacentSquares(square, testedIndices)
					if(result):
						# https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
						foundIndices = foundIndices | result
			if(len(foundIndices) == 0):
				return False
			else:
				return foundIndices

		def entityAssignment(indices):
			if(len(indices) == 0):
				return []
			else:
				row, col = indices[0][0], indices[0][1]
				x, y = 0.5 * ((50 * col) + 25), 0.5 * ((50 * row) + 25)
				pos = (x + self.dim[0], y + self.dim[0])
				print(indices[1:])
				return [pos] + entityAssignment((indices[1:]))

		# First array represents the row indices; second array represents column indices.
		# https://numpy.org/doc/stable/reference/generated/numpy.nonzero.html
		blockIndices = np.nonzero(randBoard == 1)
		for i in range(len(blockIndices[0])):
			adjacents = adjacentSquares((blockIndices[0][i], blockIndices[1][i]))
			if(not adjacents):
				continue
			print(list(adjacents))
			for pos in entityAssignment(list(adjacents)):
				self.blocks["block"].add(Block(pos, (app.blockImg.width, app.blockImg.height)))

		enemyIndices = np.nonzero(randBoard == 2)
		for i in range(len(enemyIndices[0])):
			enemyIndices = [(enemyIndices[0][i], enemyIndices[1][i]) for i in range(len(enemyIndices[0]))]
			enemyCoords = entityAssignment(enemyIndices)
			for pos in enemyCoords:
				self.enemies.add(Enemy(pos, (app.enemyImg.width, app.enemyImg.height)))

		def determinePosition(preference=None):
			pass
	
	def initPlayer(self, app):
		# Player always spawns in same position
		pos = (app.width / 2, (4 * app.height) / 5)
		dim = (app.playerImg.width, app.playerImg.height)
		return Player(pos, dim)

	def initCores(self, app):
		bDim = (app.width, app.height)
		dim = (app.coreImg.width, app.coreImg.height)
		core = ShieldedCore(bDim, dim)
		return {core}

	def isLegalMove(self, entity):
		x, y = entity.pos[0], entity.pos[1]
		# Ensure object is within board dimensions
		if(x < (self.dim[0] + (entity.dim[0] / 2)) or y < (self.dim[0] + (entity.dim[1] / 2)) or 
		   x > (self.dim[1] - (entity.dim[0] / 2)) or y > (self.dim[1] - (entity.dim[1] / 2))):
			return False
		return True
	
	# After entity moves, method is called to test for collisions.
	# Method gathers all neccesary elements to test for collision and passes them to detectCollision()
	def collisionManager(self, collider, exclusions=set()):
		# Following the separation axis theorem, determine possible dividing axes
		# dividingAxes = collider.collisionAxes()
		# print(dividingAxes)

		for core in self.cores:
			if(self.detectCollision(collider, core)):
				# print("core: collision")
				collider.collisionBehavior(core)
				core.collisionBehavior(collider)
			for proj in core.projs:
				if(self.detectCollision(collider, proj)):
					# print("core proj: collision")
					collider.collisionBehavior(proj)
					proj.collisionBehavior(collider)

		for enemy in self.enemies:
			if(self.detectCollision(collider, enemy)):
				# print("enemy: collision")
				collider.collisionBehavior(enemy)
				enemy.collisionBehavior(collider)
			for proj in enemy.projs:
				if(self.detectCollision(collider, proj)):
					# print("enemy proj: collision")
					collider.collisionBehavior(proj)
					proj.collisionBehavior(collider)

	# Using the Separating Axis theorem...
	#	- Two convex objects do not overlap if there exists an axis onto which the two objects' projections do not overlap.
	#	- Such an axis only exists if one of the sides of one of the polygons forms such a line.
	def detectCollision(self, collider, testEntity):
		# If every axis intersects, both objects intersect.
		x, y = collider.pos[0], collider.pos[1]
		dim = (testEntity.pos[0] - (testEntity.dim[0] / 2), testEntity.pos[0] + (testEntity.dim[0] / 2),
			   testEntity.pos[1] - (testEntity.dim[1] / 2), testEntity.pos[1] + (testEntity.dim[1] / 2))
		
		if(x > dim[0] and x < dim[1] and y > dim[2] and y < dim[3]):
			return True
		return False

	def gameWon(self):
		return (len(self.cores) == 0)

class Player:
	imgPath = "assets/player.png"

	def __init__(self, pos, dim):
		self.pos = pos
		self.dim = dim
		self.rot = 0
		self.health = 3
		self.projs = set()
		self.firingDelay = 0
		self.target = None
		self.action = None
	
	def collisionBehavior(self, collider):
		match collider:
			case OrangeProjectile(): self.health -= 1
			case PurpleProjectile(): self.health -= 1
			case _: self.action = "undo"

	def move(self, x1, y1):
		x0, y0 = self.pos[0], self.pos[1]
		self.pos = (x0 + x1, y0 + y1)
		# Returns original position in case movement must be undone
		return (x0, y0)
	
	def rotate(self, d1):
		self.rot = (self.rot + d1) % 360
		if(self.rot < 0):
			self.rot = 360 + self.rot

	def createProjectile(self, dim):
		if(self.firingDelay > 0):
			return

		# Modifies angle starting position to reflect typical unit circle
		rot = (90 + self.rot) % 360
		# Uses Law of Sines to calculate vector components
		vx = math.sin(math.radians(90 - rot)) * self.dim[1]
		vy = math.sin(math.radians(rot)) * self.dim[1]
		# Slope of projectile vector, represented as rise-run tuple
		# vy is negative since canvas y-direction is inverted from standard Cartesian plane
		m = (-vy, vx) 

		# Determines position of origin (should be player tip)
		pos = self.pos # placeholder value for debug
		proj = PlayerProjectile(pos, dim, m, self.rot)
		self.projs.add(proj)
		# Delay before another projectile can be created
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


class Projectile:
	def __init__(self, pos, dim, m, rot=0):
		self.pos = pos
		self.dim = dim
		self.m = m
		self.rot = rot
		self.lifespan = 15
		self.action = None

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

	def __init__(self, pos, dim, m, rot):
		super().__init__(pos, dim, m, rot)
	
	def collisionBehavior(self, collider):
		match collider:
			case OrangeProjectile(): return
			case Enemy(): return
			case _: self.action = "despawn"
	
	# Rectangle should have two possible dividing axes.
	def collisionAxes(self):
		# Angle deviation calculations
		c = math.sqrt((self.dim[0] / 2)**2 + (self.dim[1] / 2)**2)
		A = math.degrees(math.asin(self.dim[0] / (2 * c)))
		# Vertices coordinate calculations
		def coordCalculator(angle):
			r = math.sqrt(self.dim[0]**2 + self.dim[1]**2) / 2
			x = self.pos[0] + (r * math.cos(math.radians(-angle)))
			y = self.pos[1] + (r * math.sin(math.radians(-angle)))
			return (x, y)
		
		vertices = [coordCalculator(self.rot + 90 + A), # Top Left
					coordCalculator(self.rot + 90 - A), # Top Right
					coordCalculator(self.rot - 90 + A), # Bottom Right
					coordCalculator(self.rot - 90 - A)  # Botom Left
		]

		axes = set()
		# Determine axes from vertices
		pass

class OrangeProjectile(Projectile):
	imgPath = "assets/oProjectile.png"

	def __init__(self, pos, dim, m):
		super().__init__(pos, dim, m)
		# Longer lifespan since they move slower
		self.lifespan = self.lifespan * 2
	
	def collisionBehavior(self, collider):
		match collider:
			case Block(): self.action = "despawn"
			case Player(): self.action = "despawn"
			case PlayerProjectile(): self.action = "despawn"

class PurpleProjectile(Projectile):
	imgPath = "assets/pProjectile.png"

	def __init__(self, pos, dim, m):
		super().__init__(pos, dim, m)
		self.lifespan = self.lifespan * 2
	
	def collisionBehavior(self, collider):
		match collider:
			case Block(): self.action = "despawn"
			case Player(): self.action = "despawn"

class Core:
	imgPath = "assets/core.png"

	def __init__(self, bDim, dim):
		self.pattern = random.randint(0,2)
		self.pos = self.posFromPattern(bDim)
		self.dim = dim
		self.health = 5
		self.projs = set()
		# Angle of projectile fire
		self.deg = 0
		self.pType = True
		self.firingDelay = 0
		self.action = None
	
	# Behavior if collides with projectile
	def collisionBehavior(self, collider):
		match collider:
			case PlayerProjectile(): self.health -= 1
	
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

	def createProjectile(self, deg, dim, pType=True):
		# Define slope from angle
		rot = (90 + deg) % 360
		vx = math.sin(math.radians(90 - rot)) * self.dim[1]
		vy = math.sin(math.radians(rot)) * self.dim[1]
		# Slope of projectile vector, represented as rise-run tuple
		# vy is negative since canvas y-direction is inverted from standard Cartesian plane
		self.m = (-vy, vx)
		# Values here are reduced by factor to slow projectiles down from standard speed
		m = (self.m[0] / 3, self.m[1] / 3)
		# Determines which type of projectile to add
		proj = OrangeProjectile(self.pos, dim, m) if pType else PurpleProjectile(self.pos, dim, m)
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

	def firingPattern(self, pPos, dim):
		if(self.firingDelay > 0):
			return
		
		pType = self.pType

		# Various firing patterns for variety
		match self.pattern:
			case 1:
				for deg in range(self.deg, self.deg + 360, 60):
					self.createProjectile(deg, dim, pType)
					pType = not pType
				self.pType = not pType
				self.deg += 10
				self.firingDelay = 7
			case 2:
				deg = self.angleToPlayer(pPos)
				for adj in range(-20, 21, 20):
					self.pType = not self.pType
					self.createProjectile(deg + adj, dim, self.pType)
				self.firingDelay = 8
			case _:
				for deg in range(0, 360, 45):
					self.createProjectile(deg, dim, pType)
					pType = not pType
				self.pType = not self.pType
				self.firingDelay = 10

class ShieldedCore(Core):
	imgPath = "assets/sCore.png"

	def __init__(self, pos, dim):
		super().__init__(pos, dim)
		self.shield = True

	def destroyShield(self):
		self.shield = False
	
	def collisionBehavior(self, collider):
		if(not self.shield):
			return super().collisionBehavior(collider)

class Block:
	imgPath = "assets/block.png"

	def __init__(self, pos, dim):
		self.pos = pos
		self.dim = dim

class DestructableBlock(Block):
	imgPath = "assets/dBlock.png"

	def __init__(self, pos, dim):
		super().__init__(pos, dim)
		self.health = 5 # arbitrary number

class EnemyBlock(Block):
	imgPath = "assets/eBlock.png"

	def __init__(self, pos, dim):
		super().__init__(pos, dim)

class Enemy:
	imgPath = "assets/enemy.png"

	def __init__(self, pos, dim):
		self.pos = pos
		self.dim = dim
		self.rot = 180
		# Is a variable necessary? They are defeated after a single projectile collision.
		self.health = 1
		self.m = (0, 0)
		self.projs = set()
		self.firingDelay = 0
		self.action = None

	def collisionBehavior(self, collider):
		match collider:
			case PlayerProjectile(): self.action = "despawn"
	
	# Slowly move forwards according to orientation
	def follow(self, pPos):
		self.orient(pPos)
		# Modifies angle starting position to reflect typical unit circle
		rot = (90 + self.rot) % 360
		# Uses Law of Sines to calculate vector components
		vx = math.sin(math.radians(90 - rot)) * self.dim[1]
		vy = math.sin(math.radians(rot)) * self.dim[1]
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
	
	def createProjectile(self, dim):
		# Values here are reduced by factor to slow projectiles down from standard speed
		m = (self.m[0] / 3, self.m[1] / 3)
		# Determines which type of projectile to add
		proj = OrangeProjectile(self.pos, dim, m)
		self.projs.add(proj)
		self.firingDelay = 15
	
	def autoFire(self, dim):
		if(self.firingDelay > 0):
			return
		self.createProjectile(dim)