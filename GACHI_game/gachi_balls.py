import pygame as pg
import numpy as np
import math
from random import randint

SCREEN_SIZE = (800, 800)  # минимальная ширина - 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 220, 0)
ORANGE = (255, 150, 0)
MAROON = (128, 0, 0)
OLIVE = (0, 128, 128)
NAVY_BLUE = (0, 0, 128)
TARGET_COLORS = [RED, YELLOW, ORANGE]
DARK_YELLOW = (80, 60, 0)
EYES = (80, 0, 0)
FPS = 30
FONT_SIZE = 50

pg.mixer.pre_init(22050, -16, 2, 2048)
pg.init()
pg.mixer.init()

sound0 = pg.mixer.Sound("start.wav")
sound1 = pg.mixer.Sound("woo.wav")
sound2 = pg.mixer.Sound("hit.ogg")  # .ogg быстрее обрабатывается
sound4 = pg.mixer.Sound("yeah.wav")
sound5 = pg.mixer.Sound("end.wav")
sound6 = pg.mixer.Sound("300.ogg")
screen = pg.display.set_mode(SCREEN_SIZE)
SCREEN_SIZE = (SCREEN_SIZE[0], SCREEN_SIZE[1] - 100)
pg.display.set_caption("GACHI BALLS")
clock = pg.time.Clock()
screen.fill(BLACK)

font = pg.font.Font(None, FONT_SIZE)
g = 10  # ускорение свободного падения
(g_min, g_max) = (0, 50)
k = 0.8  # коэффициент замедления при ударении со стенками
number_of_targets = 5
counter = 0  # переменная для времени
score = 0  # счет
s = -1
counter0 = -1


class Ball:
    def __init__(self, coord, vel, t0):
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.coord = coord
        self.vel = vel
        self.rad = 15
        self.is_alive = True
        self.time = t0  # время когда заспавнили шарик

    def draw(self):
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def check_walls(self, v):
        if self.coord[0] < self.rad:
            self.coord[0] = self.rad
            self.vel[0] = (-k) * v[0]
        elif self.coord[0] > SCREEN_SIZE[0] - self.rad:
            self.coord[0] = SCREEN_SIZE[0] - self.rad
            self.vel[0] = (-k) * v[0]

    def move(self, t):
        self.vel = list(self.vel)
        self.coord = list(self.coord)
        vel_y = self.vel[1] + g * (t - self.time) / FPS
        self.coord[0] = self.coord[0] + int(self.vel[0])
        self.coord[1] = self.coord[1] + int(vel_y)
        self.check_walls((self.vel[0], vel_y))
        if self.coord[1] > (SCREEN_SIZE[1] + 2 * self.rad):  # улетел вниз
            self.is_alive = False
        if g == 0 and self.coord[1] < (-2) * self.rad:  # улетел вверх и g=0
            self.is_alive = False
        if g == 0 and (t - self.time) / FPS > 5:  # если строго горизонтально
            self.is_alive = False


class Cannon:
    def __init__(self):
        self.coord = (0, SCREEN_SIZE[1] // 2)
        self.angle = 0
        self.min_pow = 0
        self.max_pow = 40
        self.power = randint(self.min_pow + 20, self.max_pow)
        self.active = False

    def draw(self):
        end_pos = (int(self.coord[0] + self.power * 2 * np.cos(self.angle)),
                   int(self.coord[1] + self.power * 2 * np.sin(self.angle)))
        pg.draw.line(screen, WHITE, self.coord, end_pos, 5)
        return end_pos

    def strike(self):
        vel = (int(self.power * np.cos(self.angle)),
               int(self.power * np.sin(self.angle)))
        self.active = False
        return vel

    def set_angle(self, mouse_pos):
        self.angle = np.arctan2(mouse_pos[1] - self.coord[1],
                                mouse_pos[0] - self.coord[0])


class Target:
    def __init__(self):
        self.coords = list((randint(50, SCREEN_SIZE[0] - 50),
                            randint(50, SCREEN_SIZE[1] - 50)))
        self.radius = 30
        self.vel = list((randint(0, 7), randint(0, 7)))
        self.color = TARGET_COLORS[randint(0, 2)]

    def draw(self):
        pg.draw.circle(screen, self.color, self.coords, self.radius)
        pg.draw.circle(screen, WHITE, self.coords, self.radius - 10)
        pg.draw.circle(screen, self.color, self.coords, self.radius - 20)

    def hit_check(self, xy, ball_radius, score0):
        (ball_x, ball_y) = xy
        (x, y) = self.coords
        distance = math.sqrt((ball_x - x) ** 2 + (ball_y - y) ** 2)
        if distance <= (self.radius + ball_radius):
            sound2.play()
            self.coords = list((randint(50, SCREEN_SIZE[0] - 50),
                                randint(50, SCREEN_SIZE[1] - 50)))
            self.vel = list((randint(0, 5), randint(0, 5)))
            self.color = TARGET_COLORS[randint(0, 2)]
            if score0 % 50 == 49:
                if score0 % 300 == 299:
                    sound6.play()
                else:
                    sound4.play()
            return 1
        else:
            return 0

    def check_walls(self):
        for i in (0, 1):
            if self.coords[i] < self.radius:
                self.coords[i] = self.radius
                self.vel[i] = (-1) * self.vel[i]
            elif self.coords[i] > SCREEN_SIZE[i] - self.radius:
                self.coords[i] = SCREEN_SIZE[i] - self.radius
                self.vel[i] = (-1) * self.vel[i]

    def move(self):
        for i in (0, 1):
            self.coords[i] = self.coords[i] + self.vel[i]
        self.check_walls()


def clock_and_score_renewal(time0, score0):
    time_passed = int(time0 / FPS)
    if time_passed < 60:
        str_format_time = "Time: " + str(time_passed) + "s"
    else:
        str_format_time = "Time: " + str(time_passed // 60) + "m " + \
                          str(time_passed % 60) + "s"
    text2 = font.render(str_format_time, True, OLIVE)
    str_format_score = "Score: " + str(score0)
    text3 = font.render(str_format_score, True, MAROON)
    pg.draw.rect(screen, WHITE, (0, SCREEN_SIZE[1], SCREEN_SIZE[0], 100))
    screen.blit(text2, (SCREEN_SIZE[0] * 6 // 23, SCREEN_SIZE[1] + 35))
    screen.blit(text3, (10, SCREEN_SIZE[1] + 35))


def draw_background(color):
    a = 400
    screen.fill(BLACK)
    scr = pg.Surface((a, a), pg.SRCALPHA)
    pg.draw.circle(scr, DARK_YELLOW, (200, 200), 100)
    pg.draw.circle(scr, BLACK, (200, 200), 101, 1)
    pg.draw.rect(scr, BLACK, (150, 250, 100, 20))
    pg.draw.circle(scr, color, (150, 180), 20)
    pg.draw.circle(scr, BLACK, (150, 180), 10)
    pg.draw.circle(scr, BLACK, (150, 180), 21, 1)
    pg.draw.circle(scr, color, (250, 180), 15)
    pg.draw.circle(scr, BLACK, (250, 180), 7)
    pg.draw.circle(scr, BLACK, (250, 180), 16, 1)
    pg.draw.polygon(scr, BLACK,
                    [(220, 166), (298, 136), (301, 144), (224, 173)])
    pg.draw.polygon(scr, BLACK,
                    [(182, 166), (178, 173), (99, 125), (104, 117)])
    screen.blit(scr, (0, 0))
    screen.blit(scr, (SCREEN_SIZE[0] - a, 0))
    screen.blit(scr, (0, SCREEN_SIZE[1] - a))
    screen.blit(scr, (SCREEN_SIZE[0] - a, SCREEN_SIZE[1] - a))


target_list = list(Target() for q in range(number_of_targets))
gun = Cannon()
pg.display.update()
finished = False
ball_list = []
ball_new_list = []


def g_and_cannon_power_renewal():
    font1 = pg.font.Font(None, FONT_SIZE * 4 // 5)
    str_format_g = "g: " + str(g) + " (left&right)"
    str_format_power = "power: " + str(gun.power) + " (up&down)"
    text4 = font1.render(str_format_g, True, NAVY_BLUE)
    text5 = font1.render(str_format_power, True, NAVY_BLUE)
    screen.blit(text4, (SCREEN_SIZE[0] * 12 // 20, SCREEN_SIZE[1] + 20))
    screen.blit(text5, (SCREEN_SIZE[0] * 12 // 20, SCREEN_SIZE[1] + 55))


while not finished:
    clock.tick(FPS)
    counter += 1
    if counter == 1:
        sound0.play()
    if counter == counter0 + s*3*FPS:
        finished = True
    if counter % FPS == 0:
        EYES = (randint(0, 100), randint(0, 100), randint(0, 100))
    draw_background(EYES)
    for target in target_list:
        target.move()
        target.draw()
    gun_end = gun.draw()
    ball_new_list = []
    for ball in ball_list:
        ball.move(counter)
        for target in target_list:
            score += target.hit_check(ball.coord, ball.rad, score)
        if ball.is_alive:
            ball.draw()
            ball_new_list.append(ball)  # отсеивает мёртвые шары
    ball_list = ball_new_list
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sound5.play()
            s = 1
            counter0 = counter
        elif event.type == pg.MOUSEMOTION:
            gun.set_angle(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN:
            ball_list.append(Ball(gun_end, gun.strike(), counter))
            sound1.play()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT and g != g_max:
                g += 1
            if event.key == pg.K_LEFT and g != g_min:
                g -= 1
            if event.key == pg.K_UP and gun.power != gun.max_pow:
                gun.power += 1
            if event.key == pg.K_DOWN and gun.power != gun.min_pow:
                gun.power -= 1
    clock_and_score_renewal(counter, score)
    g_and_cannon_power_renewal()
    pg.display.update()

pg.quit()
