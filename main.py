from classes import *
from cmu_112_graphics import *

import classes as c

res = (500, 500)

############
# This function hardcodes for simpler debugging
def debug(app):
	margin = app.width / 10
	app.board = c.Board((app.width - margin, app.width - margin))
############

def appStarted(app):
	# app.gameActive = False
	debug(app) # Remember to remove in final product
	app.image = app.loadImage(app.board.player.imgPath)

def timerFired(app):
    pass

def keyPressed(app, event):
	if(not app.board): # board is active (FIX LATER)
		return

	match event.key:
		case 'Up':		app.board.player.move(0, -5)
		case 'Down':	app.board.player.move(0, +5)
		case "Left":	app.board.player.move(-5, 0)
		case "Right":	app.board.player.move(+5, 0)
		case "r": 		app.board.player.rotate(10)
		case "Space":
			# fire projectiles
			pass

def redrawAll(app, canvas):
	canvas.create_rectangle(0, 0, app.width, app.height, fill="gray")
	canvas.create_image(app.board.player.pos[0], app.board.player.pos[1],
						image=ImageTk.PhotoImage(app.scaleImage(app.image.rotate(app.board.player.rot), 1/3)))

def playGame():
	runApp(width=res[0], height=res[1])

playGame()

# app.gameActive = app.player.deductHealth()