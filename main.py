from classes import *
from cmu_112_graphics import *

import random

############
res = (500, 500)

# This function hardcodes for simpler debugging
def debug(app):
	app.board = Board((app.width, app.height), app.sCoreImg.width)

def createEnemy(app):
	pos = (random.randint(app.board.dim[0], app.board.dim[1]),
		   random.randint(app.board.dim[0], app.board.dim[1]))
	enemy = Enemy(pos)
	app.board.enemies.add(enemy)
############

def appStarted(app):
	app.board = None
	app.gameOver = False
	initSprites(app)
	debug(app) # Remember to remove in final product

def initSprites(app, scale=1/3):
	app.playerImg = app.scaleImage(app.loadImage("assets/player.png"), scale)
	app.projImg = app.scaleImage(app.loadImage("assets/playerProjectile.png"), scale)
	app.coreImg = app.scaleImage(app.loadImage("assets/core.png"), scale)
	app.sCoreImg = app.scaleImage(app.loadImage("assets/sCore.png"), scale)
	app.enemyImg = app.scaleImage(app.loadImage("assets/enemy.png"), scale)
	app.oProjImg = app.scaleImage(app.loadImage("assets/oProjectile.png"), scale)
	app.pProjImg = app.scaleImage(app.loadImage("assets/pProjectile.png"), scale)

def timerFired(app):
	if(not app.board):
		return

	if(app.board.player.firingDelay > 0):
		app.board.player.firingDelay -= 1

	if(app.board.player.target):
		app.board.player.autoOrient()
	
	for core in app.board.cores:
		if(core.firingDelay > 0):
			core.firingDelay -= 1
		
		core.firingPattern(3, app.coreImg.height, app.board.player.pos)

		for proj in core.projs.copy():
			if(proj.lifespan <= 0):
				core.projs.remove(proj)
			else:
				proj.move()
				proj.lifespan -= 1

	for enemy in app.board.enemies:
		if(enemy.firingDelay > 0):
			enemy.firingDelay -= 1

		pos = enemy.follow(app.board.player.pos, app.enemyImg.height)
		if(not app.board.isLegalMove(enemy.pos, (app.enemyImg.width, app.enemyImg.height))):
			enemy.pos = pos
		enemy.autoFire()

		for proj in enemy.projs.copy():
			if(proj.lifespan <= 0):
				enemy.projs.remove(proj)
			else:
				proj.move()
				proj.lifespan -= 1

	# Iterates over a copied set to allow removal of elements
	for proj in app.board.player.projs.copy():
		if(proj.lifespan <= 0):
			# Is a __hash__ method necessary?
			app.board.player.projs.remove(proj)
		else:
			proj.move()
			proj.lifespan -= 1

def keyPressed(app, event):
	# If board is inactive, skip board-related commands
	if(not app.board):
		return
	
	match event.key:
		case "r": 		app.board.player.rotate(-10)
		case "e": 		app.board.player.rotate(+10)
		case "Space":	app.board.player.createProjectile(app.playerImg.height)
		case "t":		app.board.player.determineTarget(app.board.enemies, app.board.cores)
		# Debug keys
		case "k":		createEnemy(app)

	# Keys that require legality checks
	def playerMovement():
		match event.key:
			case 'Up':		return app.board.player.move(0, -5)
			case 'Down': 	return app.board.player.move(0, +5)
			case "Left":	return app.board.player.move(-5, 0)
			case "Right":	return app.board.player.move(+5, 0)
	
	pos = playerMovement()
	if(not app.board.isLegalMove(app.board.player.pos, (app.playerImg.width, app.playerImg.height))):
		app.board.player.pos = pos

def redrawAll(app, canvas):
	# Drawing background
	canvas.create_rectangle(0, 0, app.width, app.height, fill="gray")
	if(app.board):
		# Drawing board
		canvas.create_rectangle(app.board.dim[0], app.board.dim[0], app.board.dim[1], app.board.dim[1],
								fill="#c4bea6", outline="#c4bea6")
		# Drawing player
		canvas.create_image(app.board.player.pos[0], app.board.player.pos[1],
							image=ImageTk.PhotoImage(app.playerImg.rotate(app.board.player.rot)))
		if(app.board.player.target):
			canvas.create_line(app.board.player.pos[0], app.board.player.pos[1],
							   app.board.player.target.pos[0], app.board.player.target.pos[1], fill="blue", dash=(5,1))

		# Drawing projectiles
		for proj in app.board.player.projs:
			canvas.create_image(proj.pos[0], proj.pos[1],
							image=ImageTk.PhotoImage(app.projImg.rotate(proj.rot)))
		
		# Drawing cores
		for core in app.board.cores:
			canvas.create_image(core.pos[0], core.pos[1],
								image=ImageTk.PhotoImage(app.sCoreImg if core.shield else app.coreImg))
			
			for proj in core.projs:
				canvas.create_image(proj.pos[0], proj.pos[1],
									image=ImageTk.PhotoImage(app.oProjImg if (type(proj) == OrangeProjectile) else app.pProjImg))

		# Drawing enemies
		for enemy in app.board.enemies:
			canvas.create_image(enemy.pos[0], enemy.pos[1],
								image=ImageTk.PhotoImage(app.enemyImg.rotate(enemy.rot)))
			for proj in enemy.projs:
				canvas.create_image(proj.pos[0], proj.pos[1],
									image=ImageTk.PhotoImage(app.oProjImg if (type(proj) == OrangeProjectile) else app.pProjImg))

		# Debug visualizations
		# canvas.create_line(app.width / 2, 0, app.width / 2, app.height, fill="red")
		# canvas.create_line(0, app.height / 2, app.width, app.height / 2, fill="red")
		cx, cy = app.board.player.pos[0], app.board.player.pos[1]
		# canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="red")
		x1, y1 = app.board.player.pos[0] - (app.playerImg.width / 2), app.board.player.pos[1] + (app.playerImg.height / 2)
		x2, y2 = app.board.player.pos[0] + (app.playerImg.width / 2), app.board.player.pos[1] - (app.playerImg.height / 2)
		# canvas.create_rectangle(x1, y1, x2, y2, outline="black")
		cx, cy = app.board.player.pos[0], app.board.player.pos[1]
		r = app.playerImg.height / 2
		# canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="black")
		cx, cy = cx - (app.playerImg.width / 2), cy + (app.playerImg.height / 2)
		# canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="red")
		# for enemy in app.board.enemies:
		# 	canvas.create_line(enemy.pos[0], enemy.pos[1], app.board.player.pos[0], app.board.player.pos[1], fill="blue")
		# 	canvas.create_line(enemy.pos[0], enemy.pos[1], enemy.pos[0], app.board.player.pos[1], fill="blue", dash=(5,1))
		# 	canvas.create_line(enemy.pos[0], app.board.player.pos[1], app.board.player.pos[0], app.board.player.pos[1], fill="blue", dash=(5,1))
		# 	canvas.create_text(enemy.pos[0] + app.enemyImg.width * 2, enemy.pos[1] + app.enemyImg.height / 2,
		# 					   text=enemy.rot, font="Arial 10 bold", fill="black")

def playGame():
	runApp(width=res[0], height=res[1])

playGame()