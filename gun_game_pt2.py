import pygame as pg
import numpy as np
from random import randint

SCREEN_SIZE = (1000, 800)  # минимальная ширина - 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 220, 0)
ORANGE = (255, 150, 0)
MAROON = (128, 0, 0)
OLIVE = (0, 128, 128)
NAVY_BLUE = (0, 0, 128)
TARGET_COLORS = [RED, ORANGE]
DARK_YELLOW = (80, 60, 0)
EYES = (80, 0, 0)
FPS = 30
FONT_SIZE = 50

pg.init()

screen = pg.display.set_mode(SCREEN_SIZE)
SCREEN_SIZE = (SCREEN_SIZE[0], SCREEN_SIZE[1] - 100)
pg.display.set_caption("The gun of Khiryanov")
clock = pg.time.Clock()
screen.fill(BLACK)

font = pg.font.Font(None, FONT_SIZE)
g = 10  # ускорение свободного падения
(g_min, g_max) = (0, 50)
k = 0.8  # коэффициент замедления при ударении со стенками
number_of_targets = 3
counter = 0  # переменная для времени
score = 0  # счет


class Ball:
    def __init__(self, coord, vel):
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.coord = coord
        self.vel = vel
        self.rad = 12
        self.is_alive = True
        self.age = 0  # возраст шарика

    def draw(self):
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def check_walls(self, v):
        if self.coord[0] < self.rad:
            self.coord[0] = self.rad
            self.vel[0] = (-k) * v[0]
        elif self.coord[0] > SCREEN_SIZE[0] - self.rad:
            self.coord[0] = SCREEN_SIZE[0] - self.rad
            self.vel[0] = (-k) * v[0]

    def move(self):
        self.age += 1
        self.vel = list(self.vel)
        self.coord = list(self.coord)
        vel_y = self.vel[1] + g * self.age / FPS
        self.coord[0] = self.coord[0] + int(self.vel[0])
        self.coord[1] = self.coord[1] + int(vel_y)
        self.check_walls((self.vel[0], vel_y))
        if self.coord[1] > (SCREEN_SIZE[1] + 2 * self.rad):  # улетел вниз
            self.is_alive = False
        if g == 0 and self.coord[1] < (-2) * self.rad:  # улетел вверх и g=0
            self.is_alive = False
        if g == 0 and self.age / FPS > 5:  # если строго горизонтально
            self.is_alive = False


class Laser:
    def __init__(self, coord, vel, angle):
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.start_pos = coord
        self.vel = vel
        self.vel = list(self.vel)
        self.angle = angle
        self.rad = 8
        self.length = 60
        self.coord = coord
        self.coord = list(self.coord)
        self.is_alive = True

    def draw(self):
        pg.draw.line(screen, self.color, self.start_pos, self.coord, self.rad)

    def check_walls(self):
        if self.coord[0] < -self.length or self.coord[0] > SCREEN_SIZE[0] + self.length or \
                self.coord[1] < -self.length or self.coord[1] > SCREEN_SIZE[1] + self.length:
            self.is_alive = False

    def move(self):
        self.coord[0] += int(2*self.vel[0])
        self.coord[1] += int(2*self.vel[1])
        self.check_walls()


class Cannon:
    def __init__(self):
        self.coord = [SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2]
        self.size = 25
        self.rad = self.size // 2
        self.angle = 0
        self.min_pow = 0
        self.max_pow = 40
        self.power = randint(self.min_pow + 20, self.max_pow)
        self.active = False
        self.vel = [0, 0]

    def draw(self):
        end_pos = (int(self.coord[0] + self.power * 2 * np.cos(self.angle)),
                   int(self.coord[1] + self.power * 2 * np.sin(self.angle)))
        wheel_coord1 = (self.coord[0] - 2 * self.size + self.rad,
                        self.coord[1] + self.size + self.rad)
        wheel_coord2 = (self.coord[0] + 2 * self.size - self.rad,
                        self.coord[1] + self.size + self.rad)
        pg.draw.line(screen, WHITE, self.coord, end_pos, 5)
        pg.draw.rect(screen, WHITE,
                     [self.coord[0] - 2 * self.size, self.coord[1],
                      4 * self.size, self.size])
        pg.draw.circle(screen, WHITE, wheel_coord1, self.rad)
        pg.draw.circle(screen, WHITE, wheel_coord2, self.rad)
        return end_pos

    def strike(self):
        vel = (int(self.power * np.cos(self.angle)),
               int(self.power * np.sin(self.angle)))
        self.active = False
        return vel

    def set_angle(self, mouse_pos):
        self.angle = np.arctan2(mouse_pos[1] - self.coord[1],
                                mouse_pos[0] - self.coord[0])

    def move(self):
        self.coord[0] += 10 * self.vel[0]
        self.coord[1] += 10 * self.vel[1]


class Target1:
    def __init__(self):
        self.coords = list((randint(50, SCREEN_SIZE[0] - 50),
                            randint(50, SCREEN_SIZE[1] - 50)))
        self.radius = 30
        self.vel = list((randint(-7, 7), randint(-7, 7)))
        self.color = TARGET_COLORS[0]

    def draw(self):
        pg.draw.circle(screen, self.color, self.coords, self.radius)
        pg.draw.circle(screen, WHITE, self.coords, self.radius - 10)
        pg.draw.circle(screen, self.color, self.coords, self.radius - 20)

    def hit_check(self, xy, ball_radius):
        (ball_x, ball_y) = xy
        (x, y) = self.coords
        distance = ((ball_x - x) ** 2 + (ball_y - y) ** 2) ** 0.5
        if distance <= (self.radius + ball_radius):
            self.coords = list((randint(50, SCREEN_SIZE[0] - 50),
                                randint(50, SCREEN_SIZE[1] - 50)))
            self.vel = list((randint(-7, 7), randint(-7, 7)))
            self.color = TARGET_COLORS[0]
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


class Target2:
    def __init__(self):
        self.coords = list((randint(50, SCREEN_SIZE[0] - 50),
                            randint(50, SCREEN_SIZE[1] - 50)))
        self.radius = 25
        self.vel = list((randint(-12, 12), randint(-12, 12)))
        self.color = TARGET_COLORS[1]

    def draw(self):
        pg.draw.circle(screen, self.color, self.coords, self.radius)
        pg.draw.circle(screen, WHITE, self.coords, self.radius - 10)
        pg.draw.circle(screen, self.color, self.coords, self.radius - 20)

    def hit_check(self, xy, ball_radius):
        (ball_x, ball_y) = xy
        (x, y) = self.coords
        distance = ((ball_x - x) ** 2 + (ball_y - y) ** 2) ** 0.5
        if distance <= (self.radius + ball_radius):
            self.coords = list((randint(50, SCREEN_SIZE[0] - 50),
                                randint(50, SCREEN_SIZE[1] - 50)))
            self.vel = list((randint(0, 5), randint(0, 5)))
            self.color = TARGET_COLORS[1]
            return 3
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

    def renew_velocity(self):
        self.vel = list((randint(-12, 12), randint(-12, 12)))


class Manager:
    def __init__(self, g):
        self.g = g
        self.targets = list(Target1() for k in range(number_of_targets - 1))
        self.target_2 = Target2()
        self.targets.append(self.target_2)
        self.gun = Cannon()
        self.enemy = Cannon()
        self.balls = []  # balls & lasers actually
        self.balls_new = []
        self.score = 0

    def move_and_draw(self):
        self.gun.move()
        gun_end = self.gun.draw()
        for target in self.targets:
            target.move()
            target.draw()
        ball_new_list = []
        for ball in self.balls:
            ball.move()
            for target in self.targets:
                self.score += target.hit_check(ball.coord, ball.rad)
            if ball.is_alive:
                ball.draw()
                ball_new_list.append(ball)  # отсеивает мёртвые шары
        self.balls = ball_new_list
        return gun_end

    def check_pressed_keys(self):
        self.gun.vel = [0, 0]
        if pg.key.get_pressed():
            if pg.key.get_pressed()[pg.K_w]:
                self.gun.vel[1] -= 1
            if pg.key.get_pressed()[pg.K_s]:
                self.gun.vel[1] += 1
            if pg.key.get_pressed()[pg.K_a]:
                self.gun.vel[0] -= 1
            if pg.key.get_pressed()[pg.K_d]:
                self.gun.vel[0] += 1

    def event_handler(self, events):
        gun_end = self.move_and_draw()
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEMOTION:
                self.gun.set_angle(event.pos)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # левая кнопка мыши
                    self.balls.append(Ball(gun_end, self.gun.strike()))
                if event.button == 3:  # правая кнопка мыши
                    self.balls.append(Laser(gun_end, self.gun.strike(), self.gun.angle))
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT and self.g != g_max:
                    self.g += 1
                if event.key == pg.K_LEFT and self.g != g_min:
                    self.g -= 1
                if event.key == pg.K_UP and self.gun.power != self.gun.max_pow:
                    self.gun.power += 1
                if event.key == pg.K_DOWN and self.gun.power != self.gun.min_pow:
                    self.gun.power -= 1
        return done

    def g_and_cannon_power_renewal(self):
        font1 = pg.font.Font(None, FONT_SIZE * 4 // 5)
        str_format_g = "g: " + str(self.g) + " (left&right)"
        str_format_power = "power: " + str(self.gun.power) + " (up&down)"
        text4 = font1.render(str_format_g, True, NAVY_BLUE)
        text5 = font1.render(str_format_power, True, NAVY_BLUE)
        screen.blit(text4, (SCREEN_SIZE[0] * 12 // 20, SCREEN_SIZE[1] + 20))
        screen.blit(text5, (SCREEN_SIZE[0] * 12 // 20, SCREEN_SIZE[1] + 55))


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


mgr = Manager(g)
pg.display.update()
finished = False

while not finished:
    clock.tick(FPS)
    counter += 1
    if counter % (3*FPS//2) == 0:
        EYES = (randint(0, 100), randint(0, 100), randint(0, 100))
    if counter % randint(1, FPS) == 0:
        mgr.targets[number_of_targets - 1].renew_velocity()
    draw_background(EYES)
    mgr.check_pressed_keys()
    finished = mgr.event_handler(pg.event.get())
    clock_and_score_renewal(counter, mgr.score)
    mgr.g_and_cannon_power_renewal()
    pg.display.update()

pg.quit()
