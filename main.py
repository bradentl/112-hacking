from classes import *
from cmu_112_graphics import *

import classes as c

############
res = (500, 500)

# This function hardcodes for simpler debugging
def debug(app):
	scale = 1/3
	app.board = c.Board((app.width, app.height))
	app.playerImg = app.scaleImage(app.loadImage(app.board.player.imgPath), scale)
	app.projImg = app.scaleImage(app.loadImage("assets/playerProjectile.png"), scale)
############

def appStarted(app):
	app.board = None
	debug(app) # Remember to remove in final product

def timerFired(app):
	if(not app.board):
		return

	if(app.board.player.timeDelay > 0):
		app.board.player.timeDelay -= 1

	# Iterates over a copied set to allow removal of elements
	for proj in app.board.player.projs.copy():
		if(proj.lifespan <= 0):
			# Is a __hash__ method necessary?
			app.board.player.projs.remove(proj)
		else:
			print(f'{len(app.board.player.projs)}: {proj}')
			proj.move()
			proj.lifespan -= 1

def keyPressed(app, event):
	# If board is inactive, skip board-related commands
	if(not app.board):
		return

	match event.key:
		case 'Up':		app.board.player.move(0, -5)
		case 'Down':	app.board.player.move(0, +5)
		case "Left":	app.board.player.move(-5, 0)
		case "Right":	app.board.player.move(+5, 0)
		case "r": 		app.board.player.rotate(-10)
		case "e": 		app.board.player.rotate(+10)
		case "Space":	app.board.player.createProjectile(app.playerImg.height)

def redrawAll(app, canvas):
	# Drawing background
	canvas.create_rectangle(0, 0, app.width, app.height, fill="gray")
	if(app.board):
		# Drawing board
		canvas.create_rectangle(app.board.dim, app.board.dim, app.width - app.board.dim, app.height - app.board.dim,
								fill="#c4bea6", outline="#c4bea6")
		# Drawing player
		canvas.create_image(app.board.player.pos[0], app.board.player.pos[1],
							image=ImageTk.PhotoImage(app.playerImg.rotate(app.board.player.rot)))
		
		# Drawing projectiles
		for proj in app.board.player.projs:
			canvas.create_image(proj.pos[0], proj.pos[1],
							image=ImageTk.PhotoImage(app.projImg.rotate(proj.rot)))

		# Debug visualizations
		canvas.create_line(app.width / 2, 0, app.width / 2, app.height, fill="red")
		canvas.create_line(0, app.height / 2, app.width, app.height / 2, fill="red")
		cx, cy = app.board.player.pos[0], app.board.player.pos[1]
		canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="red")
		x1, y1 = app.board.player.pos[0] - (app.playerImg.width / 2), app.board.player.pos[1] + (app.playerImg.height / 2)
		x2, y2 = app.board.player.pos[0] + (app.playerImg.width / 2), app.board.player.pos[1] - (app.playerImg.height / 2)
		canvas.create_rectangle(x1, y1, x2, y2, outline="black")
		cx, cy = app.board.player.pos[0], app.board.player.pos[1]
		r = app.playerImg.height / 2
		canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="black")
		cx, cy = cx - (app.playerImg.width / 2), cy + (app.playerImg.height / 2)
		canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="red")

def playGame():
	runApp(width=res[0], height=res[1])

playGame()

# app.gameActive = app.player.deductHealth()