from classes import *
from cmu_112_graphics import *

import random

############
res = (500, 500)

# This function hardcodes for simpler debugging
def debug(app):
	app.board = Board(app, 3)

def createEnemy(app):
	pos = (random.randint(app.board.dim[0] + app.enemyImg.width, app.board.dim[1] - app.enemyImg.width),
		   random.randint(app.board.dim[0] + app.enemyImg.height, app.board.dim[1] - app.enemyImg.height))
	dim = (app.enemyImg.width, app.enemyImg.height)
	enemy = Enemy(pos, dim)
	app.board.enemies.add(enemy)

def createBlock(app):
	pos = (random.randint(app.board.dim[0] + app.blockImg.width, app.board.dim[1] - app.blockImg.width),
		   random.randint(app.board.dim[0] + app.blockImg.height, app.board.dim[1] - app.blockImg.height))
	dim = (app.blockImg.width, app.blockImg.height)
	# This seems pretty inefficient, but allowed since only for debugging
	blockObject = {1:Block(pos, dim),2:DestructableBlock(pos, dim),3:EnemyBlock(pos, dim)}
	block = blockObject[random.randint(1,3)]
	blockType = {Block:"block",DestructableBlock:"dBlock",EnemyBlock:"eBlock"}
	app.board.blocks[blockType[type(block)]].add(block)
############

def appStarted(app):
	app.board = None
	app.state = "Active"
	app.pause = False
	app.timeConstant = 0
	initSprites(app)
	debug(app) # Remember to remove in final product

def initSprites(app):
	# Ensures that block dimensions are 25px
	scale = 25 / app.loadImage("assets/block.png").height
	app.playerImg = app.scaleImage(app.loadImage("assets/player.png"), scale)
	app.projImg = app.scaleImage(app.loadImage("assets/playerProjectile.png"), scale)
	app.coreImg = app.scaleImage(app.loadImage("assets/core.png"), scale)
	app.sCoreImg = app.scaleImage(app.loadImage("assets/sCore.png"), scale)
	app.enemyImg = app.scaleImage(app.loadImage("assets/enemy.png"), scale)
	app.oProjImg = app.scaleImage(app.loadImage("assets/oProjectile.png"), scale)
	app.pProjImg = app.scaleImage(app.loadImage("assets/pProjectile.png"), scale)
	app.blockImg = app.scaleImage(app.loadImage("assets/block.png"), scale)
	app.dBlockImg = app.scaleImage(app.loadImage("assets/dBlock.png"), scale)
	app.eBlockImg = app.scaleImage(app.loadImage("assets/eBlock.png"), scale)

# Maintains constant app size
def sizeChanged(app):
	app.setSize(res[0], res[1])

def timerFired(app):
	if(app.pause):
		return
	# Useful for activating code at intervals of time constant
	app.timeConstant += 1

	if(not app.board):
		return

	# Runs every three seconds to preserve efficiency
	if(app.board.player.target and app.timeConstant % 3 == 0):
		# Re-establishes closest target in case closer enemy appears
		app.board.player.determineTarget(app.board.enemies, app.board.cores)
		app.board.player.autoOrient()
	
	if(app.board.player.firingDelay > 0):
		app.board.player.firingDelay -= 1
	# Iterates over a copied set to allow removal of elements
	for proj in app.board.player.projs.copy():
		if(proj.lifespan <= 0 or proj.action == "despawn"):
			# Is a __hash__ method necessary?
			app.board.player.projs.remove(proj)
		else:
			proj.move()
			# Prevents unneccesary offscreen projectile tracking
			if(proj.isOffscreen((app.width, app.height))):
				app.board.player.projs.remove(proj)
				continue
			app.board.collisionManager(proj)
			proj.lifespan -= 1

	for core in app.board.cores.copy():
		if(core.health <= 0):
			app.board.cores.remove(core)

		if(len(app.board.cores) == 0):
			app.state = "Win"
			app.board = None
			return

		if(core.firingDelay > 0):
			core.firingDelay -= 1
		
		core.evade(app.board.player.pos)

		if(len(app.board.enemies) == 0):
			core.destroyShield()
		
		# Shouldn't matter whether oProjImg or pProjImg since both have identical dimensions
		core.firingPattern(app.board.player.pos, (app.oProjImg.width, app.oProjImg.height))

		for proj in core.projs.copy():
			if(proj.lifespan <= 0 or proj.action == "despawn"):
				core.projs.remove(proj)
			else:
				proj.move()
				# Performs removal foremost to prevent unnecessary operations
				if(proj.isOffscreen((app.width, app.height))):
					core.projs.remove(proj)
					continue
				proj.lifespan -= 1

	for enemy in app.board.enemies.copy():
		if(enemy.action == "despawn"):
			app.board.enemies.remove(enemy)
			continue

		if(enemy.firingDelay > 0):
			enemy.firingDelay -= 1

		pos = enemy.follow(app.board.player.pos)
		if(not app.board.isLegalMove(enemy)):
			enemy.pos = pos
		enemy.autoFire((app.oProjImg.width, app.oProjImg.height))

		for proj in enemy.projs.copy():
			if(proj.lifespan <= 0 or proj.action == "despawn"):
				print("despawning")
				enemy.projs.remove(proj)
			else:
				proj.move()
				if(proj.isOffscreen((app.width, app.height))):
					enemy.projs.remove(proj)
					continue
				proj.lifespan -= 1
	
	if(app.board.time - time.time() <= 0 or app.board.player.health <= 0):
		app.state = "Lose"
		app.board = None

def keyPressed(app, event):
	# If board is inactive, skip board-related commands
	if(not app.board):
		return
	
	match event.key:
		case "r": 		app.board.player.rotate(-10)
		case "e": 		app.board.player.rotate(+10)
		case "Space":	app.board.player.createProjectile((app.projImg.width, app.projImg.height))
		case "t":		app.board.player.toggleTarget(app.board.enemies, app.board.cores)
		case "p":		app.pause = not app.pause
		# Debug keys
		case "k":		createEnemy(app)
		case "l":		createBlock(app)

	# Keys that require legality checks
	def playerMovement():
		match event.key:
			case 'Up':		return app.board.player.move(0, -5)
			case 'Down': 	return app.board.player.move(0, +5)
			case "Left":	return app.board.player.move(-5, 0)
			case "Right":	return app.board.player.move(+5, 0)
	
	pos = playerMovement()
	if(not app.board.isLegalMove(app.board.player)):
		app.board.player.pos = pos
	else:
		app.board.collisionManager(app.board.player)
		if(app.board.player.action == "undo"):
			app.board.player.pos = pos
			# Reset waitng action
			app.board.player.action = None

def redrawAll(app, canvas):
	# Drawing background
	canvas.create_rectangle(0, 0, app.width, app.height, fill="gray")

	if(app.board):
		# Drawing board
		canvas.create_rectangle(app.board.dim[0], app.board.dim[0], app.board.dim[1], app.board.dim[1],
								fill="#c4bea6", outline="#c4bea6")
		# Drawing projectiles
		# Projectiles are drawn first so they appear underneath player
		for proj in app.board.player.projs:
			canvas.create_image(proj.pos[0], proj.pos[1],
							image=ImageTk.PhotoImage(app.projImg.rotate(proj.rot, expand=True)))

		# Drawing player
		canvas.create_image(app.board.player.pos[0], app.board.player.pos[1],
							image=ImageTk.PhotoImage(app.playerImg.rotate(app.board.player.rot, expand=True)))
		if(app.board.player.target):
			canvas.create_line(app.board.player.pos[0], app.board.player.pos[1],
							   app.board.player.target.pos[0], app.board.player.target.pos[1], fill="blue", dash=(5,1))
		
		# Drawing cores
		for core in app.board.cores:
			for proj in core.projs:
				canvas.create_image(proj.pos[0], proj.pos[1],
									image=ImageTk.PhotoImage(app.oProjImg if (type(proj) == OrangeProjectile) else app.pProjImg))
			canvas.create_image(core.pos[0], core.pos[1], image=ImageTk.PhotoImage(app.sCoreImg if core.shield else app.coreImg))

		# Drawing enemies
		for enemy in app.board.enemies:
			for proj in enemy.projs:
				canvas.create_image(proj.pos[0], proj.pos[1],
									image=ImageTk.PhotoImage(app.oProjImg if (type(proj) == OrangeProjectile) else app.pProjImg))
			canvas.create_image(enemy.pos[0], enemy.pos[1], image=ImageTk.PhotoImage(app.enemyImg.rotate(enemy.rot, expand=True)))
		
		# Drawing blocks
		for blockType in app.board.blocks:
			# Saves time by immediately exiting empty sets
			if(len(app.board.blocks[blockType]) == 0):
				continue

			def blockImg(blockType):
				match blockType:
					case "block": return app.blockImg
					case "dBlock": return app.dBlockImg
					case "eBlock": return app.eBlockImg
			img = blockImg(blockType)

			for block in app.board.blocks[blockType]:
							canvas.create_image(block.pos[0], block.pos[1], image=ImageTk.PhotoImage(img))
		
		# Drawing timer
		canvas.create_text(app.board.player.pos[0] + app.playerImg.width, app.board.player.pos[1] - (app.playerImg.height / 2),
						   text='%.2f'%(app.board.time - time.time()), font="Arial 10 bold", fill="black")
	
	if(app.state == "Lose"):
		canvas.create_text(app.width / 2, app.height / 2,
						   text="GAME OVER", font="Arial 30 bold", fill="black")
	elif(app.state == "Win"):
		canvas.create_text(app.width / 2, app.height / 2,
						   text="YOU WIN", font="Arial 30 bold", fill="black")

def playGame():
	runApp(width=res[0], height=res[1])

playGame()