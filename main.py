import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()



#vlerat
WIDTH = 750
HEIGHT = 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pew Pew")

PLAYER_WIDTH = 130
PLAYER_HEIGHT = 110


#Mi marr karakterat
RED_SPACE_SHIP = pygame.image.load("enemyred.png")
RED_SPACE_SHIP = pygame.transform.scale(RED_SPACE_SHIP, (PLAYER_WIDTH, PLAYER_HEIGHT))

GREEN_SPACE_SHIP = pygame.image.load("enemygreen.png")
GREEN_SPACE_SHIP = pygame.transform.scale(GREEN_SPACE_SHIP, (PLAYER_WIDTH, PLAYER_HEIGHT))

BLUE_SPACE_SHIP = pygame.image.load("enemyblue.png")
BLUE_SPACE_SHIP = pygame.transform.scale(BLUE_SPACE_SHIP, (PLAYER_WIDTH, PLAYER_HEIGHT))

#lojtari
YELLOW_SPACE_SHIP = pygame.image.load("player.png")
YELLOW_SPACE_SHIP = pygame.transform.scale(YELLOW_SPACE_SHIP, (PLAYER_WIDTH, PLAYER_HEIGHT))

#plumat
RED_LASER = pygame.image.load("pixel_laser_red.png")
GREEN_LASER = pygame.image.load("pixel_laser_green.png")
BLUE_LASER = pygame.image.load("pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load("pixel_laser_yellow.png")

#background
BG = pygame.image.load("Background_space.png")
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))

MUSIC = pygame.mixer.Sound("music.mp3")
MUSIC.set_volume(0.05)

SHOOT = pygame.mixer.Sound("shoot.mp3")
SHOOT.set_volume(0.006)

HIT = pygame.mixer.Sound("hit.mp3")
HIT.set_volume(0.06)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 72

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        WIN.blit(self.ship_img, (self.x, self.y))    
        for laser in self.lasers:
            laser.draw(window)


    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            pygame.mixer.Channel(1).play(pygame.mixer.Sound(SHOOT))

    def get_width(self):
        return self.ship_img.get_width()
        
    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        pygame.mixer.Channel(0).play(pygame.mixer.Sound(HIT))



class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER), 
                "blue" : (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("cosmicsans", 50)
    lost_font = pygame.font.SysFont("impact", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 2

    player_vel = 6
    laser_vel = 7

    player = Player(300, 650)

    lost = False
    lost_count = 0

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG, (0, 0))
        #me shkrujt tekstin
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))



        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        MUSIC.play()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue




        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > -20: # n'tmajt
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() - 20 < WIDTH: # n'tdjatht
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > -20: # nalt
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() - 20 < HEIGHT: # posht
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
        
main()
