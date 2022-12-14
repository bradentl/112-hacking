from classes import *
from cmu_112_graphics import *

##########################################
# Menu Mode
def menu_changeMode(app, mode):
	app.board = Board(app)
	app.timeConstant = 0
	app.menuSfx.active = False
	app.mode = mode

# Maintains constant app size
def menu_sizeChanged(app):
	app.setSize(res[0], res[1])

def menu_redrawAll(app, canvas):
	canvas.create_rectangle(0, 0, app.width, app.height, fill="gray")
	canvas.create_text((app.width / 2) - 25, app.height / 8, anchor="e", text="Hacking",
					   font="Arial 26 bold", fill="black")
	canvas.create_text((app.width / 2) + 25, app.height / 8, anchor="w", text="112",
					   font="Arial 26 bold", fill="black")
	canvas.create_text(app.width / 2, (9 * app.height) / 10, text="Click anywhere to begin.",
					   font="Arial 26 italic", fill="black")
	canvas.create_image(app.menuPlayer.pos[0], app.menuPlayer.pos[1],
								image=ImageTk.PhotoImage(app.playerImg.rotate(app.menuPlayer.rot, expand=True)))

def menu_keyPressed(app, event):
	match event.key:
		case "Up":		app.menuPlayer.movements["Up"] = -1
		case "Down": 	app.menuPlayer.movements["Down"] = +1
		case "Left":	app.menuPlayer.movements["Left"] = -1
		case "Right":	app.menuPlayer.movements["Right"] = +1
		case "r": 		app.menuPlayer.spin = 1
		case "f": 		app.menuPlayer.spin = -1

def menu_keyReleased(app, event):
	match event.key:
		case "Up":		app.menuPlayer.movements["Up"] = 0
		case "Down": 	app.menuPlayer.movements["Down"] = 0
		case "Left":	app.menuPlayer.movements["Left"] = 0
		case "Right":	app.menuPlayer.movements["Right"] = 0
		case "r": 		app.menuPlayer.spin = False
		case "f": 		app.menuPlayer.spin = False

def menu_mousePressed(app, event):
	menu_changeMode(app, "game")

def menu_timerFired(app):
	app.menuPlayer.move()
	
	if(app.menuPlayer.spin):
		app.menuPlayer.autoRotate()
##########################################

##########################################
# Game Mode
def game_changeMode(app, mode):
	# Closes active audio threads
	app.board.bgm.active = False
	for sfx in app.board.sfx:
		sfx.active = False
	app.mode = mode

# Maintains constant app size
def game_sizeChanged(app):
	app.setSize(res[0], res[1])

def game_keyPressed(app, event):
	match event.key:
		# Even if player.spin is an integer, value will change to boolean
		# i.e. not -1 = False, not 1 = False
		case "s":		app.board.player.spin = not app.board.player.spin
		# Controls the direction of spin by replacing with integer value.
		# i.e. False * -1 = 0; True * -1 = -1; -1 * -1 = 1
		case "v":		app.board.player.spin = app.board.player.spin * -1
		case "r": 		app.board.player.spin = 1
		case "f": 		app.board.player.spin = -1
		# Defined angles
		case "q":		app.board.player.rot = 45
		case "w":		app.board.player.rot = 0
		case "e":		app.board.player.rot = -45
		case "a":		app.board.player.rot = 90
		case "d":		app.board.player.rot = -90
		case "z":		app.board.player.rot = 135
		case "x":		app.board.player.rot = 180
		case "c":		app.board.player.rot = -135
		case "Space":	app.board.player.fire = True
		case "l":		app.board.player.fire = not app.board.player.fire
		case "t":		app.board.player.toggleTarget(app.board.enemies, app.board.cores)
		case "p":		app.pause = not app.pause
		case "Up":		app.board.player.movements["Up"] = -1
		case "Down": 	app.board.player.movements["Down"] = +1
		case "Left":	app.board.player.movements["Left"] = -1
		case "Right":	app.board.player.movements["Right"] = +1

# Using keyReleased in tandem with keyPressed allows for smoother movement and
# multiple key actions activated simultaneously.
def game_keyReleased(app, event):
	match event.key:
		case "Space":	app.board.player.fire = False
		case "Up":		app.board.player.movements["Up"] = 0
		case "Down": 	app.board.player.movements["Down"] = 0
		case "Left":	app.board.player.movements["Left"] = 0
		case "Right":	app.board.player.movements["Right"] = 0
		case "r": 		app.board.player.spin = False
		case "f": 		app.board.player.spin = False

def game_timerFired(app):
	if(app.pause):
		return

	# Runs every three seconds to preserve efficiency
	if(app.board.player.target and app.timeConstant % 3 == 0):
		# Re-establishes closest target in case closer enemy appears
		app.board.player.determineTarget(app.board.enemies, app.board.cores)
		app.board.player.autoOrient()
	
	pos = app.board.player.move()
	if(not app.board.isLegalMove(app.board.player)):
		app.board.player.pos = pos
	else:
		app.board.collisionManager(app.board.player)
		if("hurt" in app.board.player.action):
			app.board.sfx.add(Audio("sfx/pHit.wav"))
			# Reset action
			app.board.player.action.remove("hurt")
		if("undo" in app.board.player.action):
			app.board.player.pos = pos
			app.board.player.action.remove("undo")
	
	# Logic works even though player.spin can hold integer values since
	# 0 acts like a False boolean value (not 0 = True)
	if(app.board.player.spin):
		app.board.player.autoRotate()
	if(app.board.player.fire):
		if(app.board.player.autoFire((app.projImg.width, app.projImg.height))):
			app.board.sfx.add(Audio("sfx/pShoot.wav"))
	
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
			app.board.collisionManager(proj, {app.board.player})
			proj.lifespan -= 1

	for block in app.board.blocks.copy():
		# Only DestructibleBlock need testing
		if(type(block) != DestructibleBlock):
			continue
		if(block.health <= 0):
				app.board.blocks.remove(block)

	# Slight delay to enemy functions for QoL
	if(app.timeConstant > 0):
		for core in app.board.cores.copy():
			if(core.health <= 0):
				app.board.cores.remove(core)

			if(app.board.gameWon()):
				game_changeMode(app, "win")
				# Deliberately excluded from sfx set such that audio continues after scene change.
				Audio("sfx/cExplode.wav")
				return

			if(core.firingDelay > 0):
				core.firingDelay -= 1

			if(core.shield and len(app.board.enemies) == 0):
				core.shield = False
				if(app.timeConstant > 1):
					app.board.sfx.add(Audio("sfx/shieldBreak.wav"))
			
			# If core is within specified distance of player, begin evasive action.
			d = math.sqrt((app.board.player.pos[0] - core.pos[0])**2 + (app.board.player.pos[1] - core.pos[1])**2)
			if(d < 200 and app.timeConstant % 3 == 0):
				core.evade(app)
		
			# Shouldn't matter whether oProjImg or pProjImg since both have identical dimensions
			core.firingPattern(app.board.player.pos, (app.oProjImg.width, app.oProjImg.height))

			for proj in core.projs.copy():
				if(proj.lifespan <= 0 or proj.action == "despawn"):
					core.projs.remove(proj)
				else:
					proj.move()
					app.board.collisionManager(proj, app.board.cores | app.board.enemies | app.board.projs)
					# Performs removal foremost to prevent unnecessary operations
					if(proj.isOffscreen((app.width, app.height))):
						core.projs.remove(proj)
						continue
					proj.lifespan -= 1

		for enemy in app.board.enemies.copy():
			if(enemy.action == "despawn"):
				app.board.enemies.remove(enemy)
				app.board.projs = app.board.projs | enemy.projs
				continue

			if(enemy.firingDelay > 0):
				enemy.firingDelay -= 1

			pos = enemy.follow(app.board.player.pos)
			if(not app.board.isLegalMove(enemy)):
				enemy.pos = pos
			else:
				app.board.collisionManager(enemy, app.board.projs)
				if(enemy.action == "undo"):
					enemy.pos = pos
					enemy.action = None
			enemy.autoFire((app.oProjImg.width, app.oProjImg.height))

			for proj in enemy.projs.copy():
				if(proj.lifespan <= 0 or proj.action == "despawn"):
					enemy.projs.remove(proj)
				else:
					proj.move()
					app.board.collisionManager(proj, app.board.enemies | app.board.cores | app.board.projs)
					if(proj.isOffscreen((app.width, app.height))):
						enemy.projs.remove(proj)
						continue
					proj.lifespan -= 1
		
		for proj in app.board.projs.copy():
			if(proj.lifespan <= 0 or proj.action == "despawn"):
				app.board.projs.remove(proj)
			else:
				proj.move()
				if(proj.isOffscreen((app.width, app.height))):
					app.board.projs.remove(proj)
					continue
				proj.lifespan -= 1
	
	if(app.board.time - time.time() <= 0 or app.board.player.health <= 0):
		game_changeMode(app, "lose")
		# Deliberately excluded from sfx set such that audio continues after scene change.
		Audio("sfx/pExplode.wav")
		return
	
	# Useful for activating code at intervals of time constant
	app.timeConstant += 1

def game_redrawAll(app, canvas):
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
		if(app.board.player.hurt):
			# Damage animation
			canvas.create_image(app.board.player.pos[0], app.board.player.pos[1],
								image=ImageTk.PhotoImage(app.hurtPlayerImg.rotate(app.board.player.rot, expand=True)))
			app.board.player.hurt = (app.board.player.hurt + 1) % 10
		else:
			canvas.create_image(app.board.player.pos[0], app.board.player.pos[1],
								image=ImageTk.PhotoImage(app.playerImg.rotate(app.board.player.rot, expand=True)))

		# Drawing target lines
		if(app.board.player.target):
			canvas.create_line(app.board.player.pos[0], app.board.player.pos[1],
							   app.board.player.target.pos[0], app.board.player.target.pos[1], fill="blue", dash=(5,1))
		
		# Drawing cores
		for core in app.board.cores:
			for proj in core.projs:
				canvas.create_image(proj.pos[0], proj.pos[1],
									image=ImageTk.PhotoImage(app.oProjImg if (type(proj) == OrangeProjectile) else app.pProjImg))
			if(core.hurt):
				canvas.create_image(core.pos[0], core.pos[1], image=ImageTk.PhotoImage(app.hurtCoreImg))
				core.hurt = (core.hurt + 1) % 2
			else:
				canvas.create_image(core.pos[0], core.pos[1], image=ImageTk.PhotoImage(app.sCoreImg if core.shield else app.coreImg))
			

		# Drawing enemies
		for enemy in app.board.enemies:
			for proj in enemy.projs:
				canvas.create_image(proj.pos[0], proj.pos[1],
									image=ImageTk.PhotoImage(app.oProjImg if (type(proj) == OrangeProjectile) else app.pProjImg))
			canvas.create_image(enemy.pos[0], enemy.pos[1], image=ImageTk.PhotoImage(app.enemyImg.rotate(enemy.rot, expand=True)))
		
		for proj in app.board.projs:
			canvas.create_image(proj.pos[0], proj.pos[1],
								image=ImageTk.PhotoImage(app.oProjImg if (type(proj) == OrangeProjectile) else app.pProjImg))
		
		# Drawing blocks
		for block in app.board.blocks:
			# Only DestructibleBlocks have the attribute hurt
			if(hasattr(block, "hurt") and block.hurt):
				canvas.create_image(block.pos[0], block.pos[1], image=ImageTk.PhotoImage(app.hurtDBlockImg))
				block.hurt = (block.hurt + 1) % 2
				continue

			def blockImg(blockType):
				match blockType:
					case DestructibleBlock(): return app.dBlockImg
					case EnemyBlock(): return app.eBlockImg
					case Block(): return app.blockImg
			
			canvas.create_image(block.pos[0], block.pos[1], image=ImageTk.PhotoImage(blockImg(block)))
		
		# Drawing timer
		canvas.create_text(app.board.player.pos[0] + app.playerImg.width, app.board.player.pos[1] - (app.playerImg.height / 2),
						   text="%.2f"%(app.board.time - time.time()), font="Arial 10 bold", fill="black")
##########################################

##########################################
# Win Mode
def win_changeMode(app, mode):
	app.menuSfx = Audio("sfx/menuOpen.wav")
	app.mode = mode

# Maintains constant app size
def win_sizeChanged(app):
	app.setSize(res[0], res[1])

def win_redrawAll(app, canvas):
	canvas.create_rectangle(0, 0, app.width, app.height, fill="gray")
	canvas.create_text(app.width / 2, app.height / 2,
					   text="Hacking Complete", font="Courier 30", fill="black")

def win_mousePressed(app, event):
	win_changeMode(app, "menu")
##########################################

##########################################
# Lose Mode
def lose_changeMode(app, mode):
	app.menuSfx = Audio("sfx/menuOpen.wav")
	app.mode = mode

# Maintains constant app size
def lose_sizeChanged(app):
	app.setSize(res[0], res[1])

def lose_redrawAll(app, canvas):
	canvas.create_rectangle(0, 0, app.width, app.height, fill="gray")
	canvas.create_text(app.width / 2, app.height / 2,
					   text="Hacking Failed", font="Courier 30", fill="black")

def lose_mousePressed(app, event):
	lose_changeMode(app, "menu")
##########################################

def appStarted(app):
	initSprites(app)
	app.board = None
	app.pause = False
	app.mode = "menu"
	app.menuPlayer = Player((app.width / 2, app.height / 8), (app.playerImg.width, app.playerImg.height))
	app.menuSfx = Audio("sfx/menuOpen.wav")

def initSprites(app):
	# Ensures that block dimensions are 25px
	scale = 25 / app.loadImage("assets/block.png").height
	app.playerImg = app.scaleImage(app.loadImage("assets/player.png"), scale)
	app.hurtPlayerImg = app.scaleImage(app.loadImage("assets/player_hurt.png"), scale)
	app.projImg = app.scaleImage(app.loadImage("assets/playerProjectile.png"), scale)
	app.coreImg = app.scaleImage(app.loadImage("assets/core.png"), scale)
	app.hurtCoreImg = app.scaleImage(app.loadImage("assets/core_hurt.png"), scale)
	app.sCoreImg = app.scaleImage(app.loadImage("assets/sCore.png"), scale)
	app.enemyImg = app.scaleImage(app.loadImage("assets/enemy.png"), scale)
	app.oProjImg = app.scaleImage(app.loadImage("assets/oProjectile.png"), scale)
	app.pProjImg = app.scaleImage(app.loadImage("assets/pProjectile.png"), scale)
	app.blockImg = app.scaleImage(app.loadImage("assets/block.png"), scale)
	app.dBlockImg = app.scaleImage(app.loadImage("assets/dBlock.png"), scale)
	app.hurtDBlockImg = app.scaleImage(app.loadImage("assets/dBlock_hurt.png"), scale)
	app.eBlockImg = app.scaleImage(app.loadImage("assets/eBlock.png"), scale)

res = (500, 500)
def playGame():
	runApp(width=res[0], height=res[1])
playGame()