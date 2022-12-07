import re
import os
import math
import time
import wave
import random
import pyaudio
import threading
import numpy as np

p = pyaudio.PyAudio()

class Audio:
	def __init__(self, path):
		self.active = True
		# https://people.csail.mit.edu/hubert/pyaudio/docs/
		self.wf = wave.open(path, 'rb')
		self.stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
							 channels=self.wf.getnchannels(),
							 rate=self.wf.getframerate(),
							 output=True)
		self.play()

	def play(self):
		# Creates separate threads for each audio effect
		concurrentAudio = threading.Thread(target=self.audioThread)
		concurrentAudio.start()

	def stop(self):
		self.stream.stop_stream()
		self.stream.close()

	# https://people.csail.mit.edu/hubert/pyaudio/docs/
	def audioThread(self):
		CHUNK = 1024
		data = self.wf.readframes(CHUNK)
		# Since boards only last a minute, unncessary to loop track.
		while len(data):
			# Terminates audio stream
			if(not self.active):
				self.stop()
				return
			self.stream.write(data)
			data = self.wf.readframes(CHUNK)

class Board:
	def __init__(self, app, difficulty=5):
		# Since x=y, tuple contains x0 and x1 (or, y0 and y1)
		self.dim = self.gameDimensions(app.width)
		self.player = None
		self.cores = set()
		self.blocks = set()
		self.enemies = set()
		# Orphaned projectiles remaining after entity defeated
		self.projs = set()
		self.populateBoard(app)
		self.bgm = self.initBgm()
		self.sfx = set()
		self.time = time.time() + 60
	
	def gameDimensions(self, l):
		margin = l / 10
		return (margin, l - margin)
	
	def populateBoard(self, app):
		# initSprites() scaling calculations ensure block dimensions are 25x25
		# Represents both length and width of grid since is square
		l = int((self.dim[1] - self.dim[0]) / app.blockImg.height)
		randGrid = np.random.randint(0, 100, size=(l, l))

		# Establishes the ratio of element frequency
		ratio = {"empty": 80, "block": 19, "enemy": 1}

		# Records previous iteration data
		prev = (0, 0)
		# Translates random grid values into element representations according to ratio
		for freq in ratio:
			randGrid[(prev[1] <= randGrid) & (randGrid < (prev[1] + ratio[freq]))] = prev[0]
			prev = (prev[0] + 1, prev[1] + ratio[freq])
		print(f'Current Board:\n{randGrid}')

		def emptyAdjacents(index, testedIndices=set()):
			foundIndices = set()
			testedIndices.add(index)
			
			bound = lambda i : max(0, min(i, l - 1))
			# Only tests orthogonally adjacent squares
			orthAdjs = {(index[0], bound(index[1] - 1)),
						(index[0], bound(index[1] + 1)),
						(bound(index[0] - 1), index[1]),
						(bound(index[0] + 1), index[1])
			}

			row, col = index[0], index[1]
			for square in orthAdjs:
				if(square in testedIndices or square in foundIndices):
					continue

				if(randGrid[row][col] == randGrid[square[0]][square[1]]):
					foundIndices.add(index)
					foundIndices.add(square)
					result = emptyAdjacents(square, testedIndices)
					if(result):
						# https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
						foundIndices = foundIndices | result
			if(len(foundIndices) == 0):
				return False
			else:
				return foundIndices

		# Additional grid variable neccesary since final board layout differs from randGrid,
		# either by exception or addition of elements.
		grid = np.zeros(shape=(l,l))

		def indexToCoord(index):
			row, col = index[0], index[1]
			# numbers?
			x, y = 0.5 * ((50 * col) + 25), 0.5 * ((50 * row) + 25)
			return (x + self.dim[0], y + self.dim[0])

		def entityAssignment(indices):
			if(len(indices) == 0):
				return []
			else:
				pos = indexToCoord((indices[0][0], indices[0][1]))
				return [pos] + entityAssignment((indices[1:]))

		# First array represents the row indices; second array represents column indices.
		# https://numpy.org/doc/stable/reference/generated/numpy.nonzero.html
		blockIndices = np.nonzero(randGrid == 1)
		for i in range(len(blockIndices[0])):
			adjacents = emptyAdjacents((blockIndices[0][i], blockIndices[1][i]))
			if(not adjacents):
				continue
			# 1:3 probability of EnemyBlock
			blockType = random.randint(0, 3)
			for pos in entityAssignment(list(adjacents)):
				if(blockType == 0):
					self.blocks.add(EnemyBlock(pos, (app.blockImg.width, app.blockImg.height)))
				else:
					self.blocks.add(Block(pos, (app.blockImg.width, app.blockImg.height)))
				# grid[blockIndices[0][i]][blockIndices[1][i]] = 1

		enemyIndices = np.nonzero(randGrid == 2)
		for i in range(len(enemyIndices[0])):
			enemyIndices = [(enemyIndices[0][i], enemyIndices[1][i]) for i in range(len(enemyIndices[0]))]
			enemyCoords = entityAssignment(enemyIndices)
			for pos in enemyCoords:
				self.enemies.add(Enemy(pos, (app.enemyImg.width, app.enemyImg.height)))
				# grid[enemyIndices[0][i]][enemyIndices[1][i]] = 1

		def determinePosition(preference=None):
			options = np.nonzero(randGrid == 0)
			# If none provided, selects a random empty square.
			if(not preference):
				i = random.randint(0, len(options[0]))
				return (options[0][i], options[1][i])

		# (l // 2, (4 * l) // 5)

		pos = indexToCoord(determinePosition())
		self.player = Player(pos, (app.playerImg.width, app.playerImg.height))

		pos = indexToCoord(determinePosition())
		self.cores.add(ShieldedCore(pos, (app.coreImg.width, app.coreImg.height)))

	def initBgm(self):
		# Selects a random audio file from the bgm folder.
		# Uses regular expression to select only .wav files
		files = [f for f in os.listdir("./bgm") if re.match('(.+).wav', f)]
		path = f'bgm/{files[random.randint(0, len(files) - 1)]}'
		return Audio(path)

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
				collider.collisionBehavior(core)
				core.collisionBehavior(collider)
			for proj in core.projs:
				if(self.detectCollision(collider, proj)):
					collider.collisionBehavior(proj)
					proj.collisionBehavior(collider)

		for enemy in self.enemies:
			if(self.detectCollision(collider, enemy)):
				collider.collisionBehavior(enemy)
				enemy.collisionBehavior(collider)
			for proj in enemy.projs:
				if(self.detectCollision(collider, proj)):
					collider.collisionBehavior(proj)
					proj.collisionBehavior(collider)

		for proj in self.projs:
			if(self.detectCollision(collider, proj)):
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
		self.hurt = False
		self.projs = set()
		self.firingDelay = 0
		self.target = None
		self.movements = {"Up": 0,
						  "Down": 0,
						  "Left": 0,
						  "Right": 0
		}
		self.spin = False
		self.fire = False
		self.action = None
	
	def collisionBehavior(self, collider):
		match collider:
			case OrangeProjectile(): self.deductHealth()
			case PurpleProjectile(): self.deductHealth()
			case _: self.action = "undo"
	
	def deductHealth(self):
		# Invincible during hurt animation
		if(self.hurt):
			return
		self.health -= 1
		self.hurt = 1
		self.action = "hurt"

	def move(self):
		x0, y0 = self.pos[0], self.pos[1]
		x1 = (self.movements["Left"] + self.movements["Right"]) * 5
		y1 = (self.movements["Up"] + self.movements["Down"]) * 5
		self.pos = (x0 + x1, y0 + y1)
		# Returns original position in case movement must be undone
		return (x0, y0)
	
	def rotate(self, d1):
		self.rot = (self.rot + d1) % 360
		if(self.rot < 0):
			self.rot = 360 + self.rot

	def autoRotate(self, dir=1):
		if(type(self.spin) == int):
			dir = self.spin
		self.rot = (self.rot + (dir * 6)) % 360

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
	
	def autoFire(self, dim):
		if(self.firingDelay > 0):
			return False
		self.createProjectile(dim)
		return True
	
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
		# Since target maintains a calculated rotation, turn off spinning.
		self.spin = False
	
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
		self.lifespan = self.lifespan * 3
	
	def collisionBehavior(self, collider):
		match collider:
			case Block(): self.action = "despawn"
			case Player(): self.action = "despawn"
			case PlayerProjectile(): self.action = "despawn"

class PurpleProjectile(Projectile):
	imgPath = "assets/pProjectile.png"

	def __init__(self, pos, dim, m):
		super().__init__(pos, dim, m)
		self.lifespan = self.lifespan * 3
	
	def collisionBehavior(self, collider):
		match collider:
			case Block(): self.action = "despawn"
			case Player(): self.action = "despawn"

class Core:
	imgPath = "assets/core.png"

	def __init__(self, pos, dim):
		self.pattern = random.randint(0,2)
		self.pos = pos
		self.dim = dim
		self.health = 5
		self.hurt = False
		self.projs = set()
		# Angle of projectile fire
		self.deg = 0
		self.pType = True
		self.firingDelay = 0
		self.action = None
	
	# Behavior if collides with projectile
	def collisionBehavior(self, collider):
		match collider:
			case PlayerProjectile(): self.deductHealth()
	
	def deductHealth(self):
		self.health -= 1
		self.hurt = 1
	
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