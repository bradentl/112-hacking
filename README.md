# 112 Hacking
An implementation of the NieR:Automata hacking minigames using 112-graphics. Players must navigate an obstacle-ridden board and defeat enemies with projectiles to clear the game.  

Entry Point: `main.py`  
Required Libraries: numpy, PIL, PyAudio  
Source Files: All necessary resources should be included and properly arranged.  

### Game Description:  
*Objective: Destroy the enemy core within the time limit.*  
While enemies are present on the board, the core will be protected from attacks.  
Fire bullets at enemies and the core to destroy them.  
Orange bullets can be destroyed with player bullets; purple bullets are indestructible.  
Orange blocks will damage the player; black blocks may be destroyed.  

### Controls:  
`Up`, `Down`, `Left`, `Right`: Movement controls  
`Space`: Fires player bullets. (Use `l` to toggle auto-fire.)  
`r`: Counterclockwise rotation  
`f`: Clockwise rotation  
`s`: Toggles continuous rotation. (Use `v` to alternate direction of turn.)  
`t`: Toggles enemy targeting.

Pre-defined player angles:  
↖ ↑ ↗   `q`  `w`  `e`  
← · → = `a`   ·    `d`  
↙ ↓ ↘   `z`  `x`  `c`  