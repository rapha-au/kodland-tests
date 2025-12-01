import pgzrun
import pygame.rect
import random
import pgzero.loaders

TITLE = "Coin Catcher"
WIDTH = 800
HEIGHT = 600

class GameState:
    MainMenu=0
    Playing = 1
    GameOver = 2

t = 0
game_state = GameState.MainMenu
muted=False
changed = False
prev_mouse = False

my_sounds = {
    "song": sounds.song
}


class Enemy:
    def __init__(self, x, y, direction):
        self.actor = Actor("saw_a", center=(x, y))
        self.direction = direction#STRING= RIGHT, LEFT

    def update(self, t):
        anim = t % 20
        if anim < 10:
            self.actor.image = "saw_a"
        else:
            self.actor.image = "saw_b"

class Player:
    def __init__(self):
        self.actor = Actor("character_green_idle", center=(100, 100))
        self.on_ground = True
        self.vx = 0
        self.vy = 0
        self.gravity = 0.4     # gravity strength
        self.jump_power = -12   # jump impulse
        self.facing = "FRONT"
        self.coins = 0
        self.hearts = 3
        self.invincibility_timer = 0  # Invincibility

    def keyspace(self):
        # Jump only if touching the ground
        if self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
            sounds.jump.play()

    def keyright(self):
        if self.actor.x < WIDTH:
            self.actor.x += 5
            self.facing = "RIGHT"

    def keyleft(self):
        if self.actor.x > 0:
            self.actor.x -= 5
            self.facing = "LEFT"

    
    def update(self, t, p_manager):
        global game_state
        anim = t % 20

        if self.facing == "RIGHT":
            if anim < 10:
                self.actor.image = "character_green_walk_a"
            else:
                self.actor.image = "character_green_walk_b"
        elif self.facing == "LEFT":
            if anim < 10:
                self.actor.image = "character_green_walk_a_left"
            else:
                self.actor.image = "character_green_walk_b_left"
        elif self.facing == "FRONT":
            self.actor.image = "character_green_idle"
        


        # Horizontal Movement
        self.actor.x += self.vx

        for p in p_manager.platform_list:
            block = p.block
            if self.actor.colliderect(block):

                if self.actor.bottom > block.top and self.actor.top < block.bottom:

                    if self.vx > 0:       # moving right
                        self.actor.right = block.left
                    elif self.vx < 0:     # moving left
                        self.actor.left = block.right

        # Vertical Movement
        self.vy += self.gravity
        self.actor.y += self.vy

        self.on_ground = False

        for p in p_manager.platform_list:
            block = p.block
            
            if self.actor.colliderect(block):
                
                previous_bottom = self.actor.bottom - self.vy

                horizontal_overlap = (
                    self.actor.right > block.left + 2 and 
                    self.actor.left < block.right - 2
                )

                if not horizontal_overlap:
                    continue 

                if self.vy > 0 and previous_bottom <= block.top:
                    self.actor.bottom = block.top
                    self.vy = 0
                    self.on_ground = True

                elif self.vy < 0 and self.actor.top >= block.bottom:
                    self.actor.top = block.bottom
                    self.vy = 0

        # Ground Collision
        if self.actor.colliderect(p_manager.ground):
            self.actor.bottom = p_manager.ground.top
            self.vy = 0
            self.on_ground = True

        # Reset horizontal velocity after all movement
        self.vx = 0

        # Coin Pickup
        for p in p_manager.platform_list:
            if p.coin.actor and self.actor.colliderect(p.coin.actor):
                p.coin.actor = None
                self.coins += 1

        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # ENEMY COLLISION
        for e in p_manager.enemy_list:
            
            # Smaller hitbox
            hitbox = self.actor.inflate(-40, -20)
            
            if e.actor.colliderect(hitbox):
                
                if self.invincibility_timer == 0:
                    self.hearts -= 1
                    sounds.hit.play()
                    self.invincibility_timer = 60

        if self.hearts <= 0:
            game_state = GameState.GameOver
            

player = Player()

class Coin:
    def __init__(self, x, y):
        self.actor = Actor("coin_gold", center=(x, y))

class Platform:
    def __init__(self, x, y, w, h, coin):
        self.actor = Actor("terrain_grass_block")
        self.block = pygame.Rect(x, y, w, h)

        self.actor.center = self.block.center

        self.time_remaining = 3*60
        self.coin = coin


class PlatformManager:
    def __init__(self):
        self.time = 0
        self.ground = pygame.Rect(0, 500, 800, 20)
        self.platform_list = []
        self.enemy_list = []
        clock.schedule_interval(self.add_enemy, 10.0)
        clock.schedule_interval(self.add, 5.0)

    def reset(self):
        self.time = 0
        self.ground = pygame.Rect(0, 500, 800, 20)
        self.platform_list = []
        self.enemy_list = []

        clock.unschedule(self.add_enemy)
        clock.schedule_interval(self.add_enemy, 10.0)

        clock.unschedule(self.add)
        clock.schedule_interval(self.add, 5.0)
        
    def add(self):
        # Create an Hypothetical Platform

        x = random.randint(0, 750)
        y = random.randint(0, 550)
        w = 32
        coin = Coin((x+10),(y-15))

        r = Platform(
            x,
            y,
            w,
            50,
            coin
        )

        #Test if it collides with anything else
        for platform in self.platform_list:
            if r.block.colliderect(platform.block):
                #Collided, return false
                return False
        
        # Passed the test, add it to the list of platforms
        self.platform_list.append(r)

        return True
    
    def add_enemy(self):
        d = random.randint(0,1)
        direction = ""
        dx = 0

        if d == 0:
            direction = "RIGHT"
            dx = 0
        else:
            direction = "LEFT"
            dx = 800

        self.enemy_list.append(Enemy(
            dx,
            400,
            direction
        ))

    
    def update(self):
        self.time+=1

        for enemy in self.enemy_list:
            if enemy.direction == "RIGHT":
                enemy.actor.x+=2
            elif enemy.direction == "LEFT":
                enemy.actor.x-=2
            enemy.update(self.time)

        
        
        new_list = []
        for i in range(0, len(self.platform_list)):
            if i > 0:
                self.platform_list[i].time_remaining-=1

            if self.platform_list[i].time_remaining > 0:
                new_list.append(self.platform_list[i])

        self.platform_list = new_list
            
                
    def draw(self):
        #Draw Ground
        for i in range(0,15):
            screen.blit("terrain_grass_block",(64*i, 500))


        for r in self.platform_list:
            #Draw platforms
            r.actor.draw()

            #Draw Coins
            if r.coin.actor != None:
                r.coin.actor.draw()
        #Draw Enemies
        for enemy in self.enemy_list:
            enemy.actor.draw()
    

p_manager = PlatformManager()


def on_key_up(key):
    if key == keys.RIGHT or key == keys.LEFT:
        player.facing = "FRONT"


def set_all_volume(vol):
    music.set_volume(vol)

    for snd in my_sounds.values():
       snd.set_volume(vol)

def toggle_mute_unmute():
    global muted, changed
    muted = not muted
    
    if changed == False:
        if muted:
            set_all_volume(0.0)
        else:
            set_all_volume(7.0)

    changed = True


def update():
    global t, game_state, changed, prev_mouse
    t+=1

    current = pygame.mouse.get_pressed()[0]

    if game_state == GameState.MainMenu:
        mx, my = pygame.mouse.get_pos()

        if prev_mouse and not current:
            if mx > 100 and mx < 200 and my>400 and my<430:
                print("NEW GAME CLICKED")
                game_state = GameState.Playing
            elif mx > 100 and mx < 200 and my>450 and my<480:
                print("MUTE/UNMUTE")
                toggle_mute_unmute()
                changed=False
            elif mx > 100 and mx < 200 and my>500 and my<530:
                print("EXIT")
                exit()

    prev_mouse = current

    if game_state == GameState.Playing:
        if keyboard.space:
            player.keyspace()
    
        if keyboard.right:
            player.keyright()
    
        if keyboard.left:
            player.keyleft()

        p_manager.update()
        player.update(t, p_manager)

    if game_state == GameState.GameOver:
        if keyboard.RETURN:
            player.coins = 0
            player.hearts = 3
            game_state = GameState.Playing
            p_manager.reset()

def draw():
    screen.clear()

    if game_state == GameState.MainMenu:
        sounds.song.play()

        screen.blit('forest', (0, 0))
        screen.draw.text("Coin Catcher", (100, 200), fontsize=62, color=(25,25,25))

        screen.draw.text("New Game", (100, 400), fontsize=24)
        screen.draw.text("Sound ON/OFF", (100, 450), fontsize=24)
        screen.draw.text("Exit", (100, 500), fontsize=24)

    elif game_state == GameState.Playing:
        sounds.song.play()
        screen.blit('forest', (0, 0))
        player.actor.draw()
        p_manager.draw()

    elif game_state == GameState.GameOver:
        sounds.song.stop()
        screen.draw.text("Game Over", (100, 200), fontsize=64)
        screen.draw.text(f"You got {player.coins} coins!", (100, 250), fontsize=64)
        screen.draw.text("Press enter to play again!", (100, 300), fontsize=64)
        



pgzrun.go()