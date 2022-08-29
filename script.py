import math
import pygame
import random
import os
from PIL import Image
import matplotlib.pyplot as plt

WIDTH = 1000
HEIGHT = 1000
FPS = 60
food_frames = 1 / (FPS / 30)

total_ff_x = []
total_y_x = []
total_y_y = []
amount = 0

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
character_img = pygame.image.load(os.path.join(img_folder, 'bact.png'))
character_c_img = pygame.image.load(os.path.join(img_folder, 'bact_c.png'))
character_ch_img = pygame.image.load(os.path.join(img_folder, 'bact_ch.png'))
character_d_img = pygame.image.load(os.path.join(img_folder, 'bact_d.png'))
character_ds_img = pygame.image.load(os.path.join(img_folder, 'bact_ds.png'))
character_h_img = pygame.image.load(os.path.join(img_folder, 'bact_h.png'))
character_hd_img = pygame.image.load(os.path.join(img_folder, 'bact_hd.png'))
character_s_img = pygame.image.load(os.path.join(img_folder, 'bact_s.png'))
character_sc_img = pygame.image.load(os.path.join(img_folder, 'bact_sc.png'))
food_img = pygame.image.load(os.path.join(img_folder, 'food.png'))

with Image.open(os.path.join(img_folder, 'clue.png')) as file:
    file.show()

back = (255, 255, 220)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Food(pygame.sprite.Sprite):
    taste = 50
    size = 10
    image = food_img

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Player(pygame.sprite.Sprite):
    x = WIDTH / 2
    y = HEIGHT / 2
    speed = 5
    prev_pos = (0, 0)
    prev_prev_pos = (0, 0)
    size = 9
    vel = None
    parameters = (0, 0)
    food = 120
    destination = ()
    food_cup = 80
    collision_list = {}
    split = 0
    damage = 2.5
    cook = 1

    def __init__(self, x, y, px, py):
        pygame.sprite.Sprite.__init__(self)
        self.image = character_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.parameters = (px, py)
        self.speed += px
        self.food_cup -= px * 10
        self.cook += self.cook * py / 5
        self.damage -= py
        if self.parameters == (0, 0):
            self.image = character_img
        elif self.parameters[0] > 1:
            if self.parameters[1] > 1:
                self.image = character_sc_img
            elif self.parameters[1] < 1:
                self.image = character_ds_img
            else:
                self.image = character_s_img
        elif self.parameters[0] < 1:
            if self.parameters[1] > 1:
                self.image = character_ch_img
            elif self.parameters[1] < 1:
                self.image = character_hd_img
            else:
                self.image = character_h_img
        elif self.parameters[1] > 1:
            self.image = character_c_img
        else:
            self.image = character_d_img

    def update(self):
        self.food -= 0.3 / (FPS / 30)
        self.split += 1 / (FPS / 30)
        if self.food >= self.food_cup:
            self.food = self.food_cup
        if self.split >= 250 - self.speed * 3 and self.food >= 25:
            self.split = 0
            random.random()
            x = self.parameters[0]
            y = self.parameters[1]
            if random.randrange(1, 7, 1) == 1:
                x = random.randrange(self.parameters[0] - 5, self.parameters[0] + 5)
                y = random.randrange(self.parameters[1] - 5, self.parameters[1] + 5)
                if x > 10:
                    x = 10
                elif x < -10:
                    x = -10
                if y > 10:
                    y = 10
                elif y < -10:
                    y = -10
            a = Player(self.x + self.size * 2, self.y + self.size * 2, x, y)
            all_sprites.add(a)
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]
        dist_list = []
        for i in all_sprites:
            dist_list.append(i)
        dist_list.remove(self)
        for i in dist_list:
            dx = self.rect.center[0] - i.rect.center[0]
            dy = self.rect.center[1] - i.rect.center[1]
            distance = math.hypot(dx, dy)
            if distance < self.size + i.size:
                if isinstance(i, Player):
                    i.rect.clamp(self)
                    self.destination = ()
                    i.food -= self.damage if i.damage >= 6 else self.damage / 4
                    if self.parameters[1] > 1:
                        self.food -= math.fabs(self.damage)
                    if i.food <= 0:
                        self.food += i.food_cup
                        self.split += 10 + self.damage
                else:
                    self.food += i.taste * self.cook
                    self.split += i.taste * self.cook
                    all_sprites.remove(i)
                    del (i)
        if self.destination == ():
            random.random()
            self.destination = (
                random.randrange(self.x - 200, self.x + 200, 1), random.randrange(self.y - 200, self.y + 200, 1))
            self.vel = get_path((self.x, self.y), self.destination)
        if math.hypot(self.x - self.destination[0], self.y - self.destination[1]) - self.size >= self.speed:
            self.x -= self.vel[0] * self.speed / (FPS / 30)
            self.y -= self.vel[1] * self.speed / (FPS / 30)
        else:
            self.destination = ()
        if self.prev_prev_pos[0] == self.x or self.prev_prev_pos[1] == self.y:
            self.destination = ()
        self.prev_pos = pygame.math.Vector2(self.x, self.y)
        self.prev_prev_pos = self.prev_pos
        self.rect.center = (self.x, self.y)
        self.rect.clamp_ip(screen.get_rect())


def collide(p1, p2):
    p2.rect.clamp(p1)
    p1.rect.clamp(p2)


def get_path(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    vel = pygame.math.Vector2(dx, dy)
    try:
        vel = vel.normalize()
    except:
        ValueError
    return vel


fig, ax = plt.subplots()

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evolution game")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

for i in range(21):
    x = Player(random.randrange(1, WIDTH), random.randrange(1, HEIGHT), 0, 0)
    all_sprites.add(x)

counter = 0
counter2 = 0
running = True
while running:
    clock.tick(FPS)
    counter += 1
    counter2 += 1
    new_amount = 0
    y_x = 0
    y_y = 0
    if counter >= food_frames / (FPS / 30):
        a = Food(random.randrange(1, int(WIDTH)), random.randrange(1, int(HEIGHT)))
        all_sprites.add(a)
        counter = 0
        food_frames += 0.1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    all_sprites.update()
    for p1 in all_sprites:
        for p2 in all_sprites:
            if p1 != p2:
                collide(p1, p2)
        if isinstance(p1, Player):
            new_amount += 1
            if counter2 == 100:
                y_x += p1.parameters[0]
                y_y += p1.parameters[1]
            if p1.food < 1:
                all_sprites.remove(p1)
                del p1
    screen.fill(back)
    all_sprites.draw(screen)
    pygame.display.flip()
    amount = new_amount
    if counter2 == 100:
        # print(total_y_x)
        # print(total_y_y)
        # print(total_ff_x)
        if len(total_y_x) >= 25 and len(total_y_y) >= 25:
            total_y_x.pop(0)
            total_y_y.pop(0)
        if len(total_ff_x) >= 25:
            total_ff_x.pop(0)
        total_y_x.append(y_x / amount if y_x != 0 else 0)
        total_y_y.append(y_y / amount if y_y != 0 else 0)
        total_ff_x.append(FPS / food_frames)
        ax.plot(total_ff_x, total_y_y, color='red')
        ax.plot(total_ff_x, total_y_x, color='blue')
        fig.show()
        ax.cla()
        counter2 = 0

pygame.quit()
