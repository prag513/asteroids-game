import pygame
import math
import random
import os
import sys

#highscore saving
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.expanduser("~")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH = os.path.join(BASE_DIR, ".asteroids_highscore.txt")

try:
    with open(SAVE_PATH, "r") as file:
        high_score = int(file.read())
except:
    high_score = 0

#initialize
pygame.init()

#screen
screen = pygame.display.set_mode((800,600))

#title
pygame.display.set_caption("Asteroids")

#GLOBAL VARIABLES
turning_angle = 3
p_accelerate = 2
bullet_cooldown_time = 600
last_action_time = 0
last_asteroid_time = 0
asteroid_cooldown_time = 200
max_p_speed = 5.5
bullet_speed = 8
asteroid_speed = 3
passive_point_time = 3000
last_passive_point_time = 0
small_asteroid_point = 5
big_asteroid_point = 10
points = 0
smallpoint_font = pygame.font.Font(None, 25)

class Player:
    def __init__(self, centre):
        self.centre = centre
        self.x = self.centre[0]
        self.y = self.centre[1]
        self.angle = 0
        self.velocity = [0,0]
        
        #relative position to centre
        self.shape = [
            (0, -20),
            (-12,10),
            (12,10)
        ]

        self.outline_shape = [
            (0,-16),
            (-9,8),
            (9,8)
        ]
    
    def draw(self, surface):
        self.coords = []
        self.outline_coords = []

        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        
        for x, y in self.shape:
            rotx = x*cos_a - y*sin_a
            roty = x*sin_a + y*cos_a
            realx = rotx + self.x
            realy = roty + self.y
            self.coords.append((realx, realy))
        
        for x, y in self.outline_shape:
            rotx = x*cos_a - y*sin_a
            roty = x*sin_a + y*cos_a
            real_outline_x = rotx + self.x
            real_outline_y = roty + self.y
            self.outline_coords.append((real_outline_x, real_outline_y))
        
        pygame.draw.polygon(surface, 'dark blue', self.coords)
        pygame.draw.polygon(surface, 'blue', self.outline_coords)

    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        #friction
        friction = 0.005
        self.velocity[0] *= (1-friction)
        self.velocity[1] *= (1-friction)

    def rotate(self, da):
        self.angle += da

    def accelerate(self, speed):
        factor = 0.08
        self.normalised_x_acc = factor * (speed * math.sin(self.angle))
        self.normalised_y_acc = factor * (-speed * math.cos(self.angle))

        if math.sqrt((self.velocity[0]+self.normalised_x_acc)**2 + (self.velocity[1]+self.normalised_y_acc)**2) < max_p_speed:
            self.velocity[0] += self.normalised_x_acc
            self.velocity[1] += self.normalised_y_acc

    def shoot(self):
        pygame.draw.circle(screen, 'white', self.coords[0], 5)

class Bullet:
    def __init__(self, player):
        self.x = player.coords[0][0]
        self.y = player.coords[0][1]
        self.base_xvelocity = player.velocity[0]
        self.base_yvelocity = player.velocity[1]
        self.angle = player.angle
        self.radius = 4
        self.color = 'white'
        self.speed = bullet_speed
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.speed * math.sin(self.angle) + self.base_xvelocity
        self.y += -self.speed * math.cos(self.angle) + self.base_yvelocity

class Asteroid:
    def __init__(self):
        self.speed = asteroid_speed
        self.velocity = [0,0]
        self.rot_angle = 0
        self.rot_speed = random.uniform(-0.03, 0.03)

        xrange1 = range(-100, -50)
        xrange2 = range(850, 900)
        yrange1 = range(-100, -50)
        yrange2 = range(650, 700)
        xcombined = list(xrange1) + list(xrange2)
        ycombined = list(yrange1) + list(yrange2)
        self.x = random.choice(xcombined)
        self.y = random.choice(ycombined)

        angle = random.uniform(0, math.tau)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.size = random.randint(0,1)

        self.bigshape = [
            (0, -42),
            (18, -38),
            (32, -20),
            (28, 5),
            (38, 18),
            (20, 35),
            (0, 28),
            (-18, 40),
            (-35, 22),
            (-30, 0),
            (-40, -18),
            (-25, -35)
                ]
        self.smallshape = [
                (0, -21),
                (9, -19),
                (16, -10),
                (14, 2.5),
                (19, 9),
                (10, 17.5),
                (0, 14),
                (-9, 20),
                (-17.5, 11),
                (-15, 0),
                (-20, -9),
                (-12.5, -17.5)
            ]
        self.coords = []
        if self.size == 1:
            self.shape = self.bigshape
        else:
            self.shape = self.smallshape

        for x,y in self.shape:
            self.coords.append((self.x+x, self.y+y))

    def draw(self):
        pygame.draw.polygon(screen, 'dark green', self.coords)

    def move(self):
        self.x += self.dx
        self.y += self.dy

        self.rot_angle += self.rot_speed
        cos_a = math.cos(self.rot_angle)
        sin_a = math.sin(self.rot_angle)
        self.coords = []
        for x,y in self.shape:
            rotx = x*cos_a - y*sin_a
            roty = x*sin_a + y*cos_a
            realx = rotx + self.x
            realy = roty + self.y
            self.coords.append((realx,realy))

def reset_game():
    global player, bullets, asteroids, points, paused
    global last_action_time, last_asteroid_time, last_passive_point_time

    player = Player([400, 300])

    bullets = []
    asteroids = []

    points = 0

    last_action_time = 0
    last_asteroid_time = 0
    last_passive_point_time = pygame.time.get_ticks()

    paused = False

#Spaceship
player = Player([400, 300])

#store bullets
bullets = []

#store asteroids
asteroids = []

clock = pygame.time.Clock()

#game loop
running = True
paused = False
while running:
    #bg
    screen.fill((0,0,0))
    #time
    current_time = pygame.time.get_ticks()
    
    #EVENTS
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and not paused:
                    if current_time - last_action_time > bullet_cooldown_time:
                        bullets.append(Bullet(player))
                        last_action_time = current_time
                if event.key == pygame.K_r and paused:
                    reset_game()

    player.draw(screen)

    for bullet in bullets:
        bullet.draw()

    for asteroid in asteroids:
        asteroid.draw()

    if paused:
        gover_font = pygame.font.Font(None, 74)
        point_font = pygame.font.Font(None, 50)
        restart_font = pygame.font.Font(None, 20)
        gover_text = gover_font.render("GAME OVER", True, "white")
        point_text = point_font.render(f"Points: {points}", True, "white")
        restart_text = restart_font.render("Press R to restart", True, "white")
        screen.blit(gover_text, (250, 250))
        screen.blit(point_text, (325, 320))
        screen.blit(restart_text, (345, 360))

        highscore_font = pygame.font.Font(None, 25)
        highscore_gameover = highscore_font.render(f"High Score: {high_score}", True, "white")
        screen.blit(highscore_gameover, (340, 380))


    if not paused:
        #draw ship
        player.move()

        #bullet
        for bullet in bullets[:]:
            #maintain bullet
            bullet.move()
            
            #delete offscreen bullets
            if (bullet.x < 0 or bullet.x > 800 or bullet.y < 0 or bullet.y > 600):
                bullets.remove(bullet)
        #points
        smallpoint_text = smallpoint_font.render(f"Points: {points}", True, "white")
        screen.blit(smallpoint_text, (700, 20))
        #asteroids
        if current_time - last_asteroid_time > asteroid_cooldown_time:
            asteroids.append(Asteroid())
            last_asteroid_time = current_time
        
        for asteroid in asteroids[:]:
            asteroid.move()

            if (asteroid.x < -200 or asteroid.x > 1000 or asteroid.y < -200 or asteroid.y > 800):
                asteroids.remove(asteroid)

            #asteroid-bullet collision
            for bullet in bullets[:]:
                buldx = asteroid.x - bullet.x
                buldy = asteroid.y - bullet.y
                buldistance = math.sqrt(buldx*buldx + buldy*buldy)
                if asteroid.size == 1:
                    if buldistance < 40:  # asteroid radius approximation
                        asteroids.remove(asteroid)
                        bullets.remove(bullet)
                        points+= big_asteroid_point
                        break
                else:
                    if buldistance < 20:  # asteroid radius approximation
                        asteroids.remove(asteroid)
                        bullets.remove(bullet)
                        points+= small_asteroid_point
                        break
            #asteroid-player collision
            playerdx = player.x - asteroid.x
            playerdy = player.y - asteroid.y
            playerdistance = math.sqrt(playerdx**2 + playerdy**2)
            if asteroid.size == 1:
                if playerdistance < 55:
                    paused = True

                    if points > high_score:
                        high_score = points
                        with open(SAVE_PATH, "w") as file:
                            file.write(str(high_score))
            else:
                if playerdistance < 30:
                    paused = True
                    if points > high_score:
                        high_score = points
                        with open(SAVE_PATH, "w") as file:
                            file.write(str(high_score))
        #player teleport
        if player.x < 0:
            player.x = 800
        if player.x > 800:
            player.x = 0
        if player.y < 0:
            player.y = 600
        if player.y > 600:
            player.y = 0
        
        #movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rotate(math.radians(-turning_angle))
        if keys[pygame.K_RIGHT]:
            player.rotate(math.radians(turning_angle))
        if keys[pygame.K_UP]:
            player.accelerate(p_accelerate)
        if keys[pygame.K_DOWN]:
            player.accelerate(-p_accelerate)
        
        #passive point gain
        if current_time - last_passive_point_time > passive_point_time:
            points += 1
            last_passive_point_time = current_time

    pygame.display.update()
    clock.tick(60)
