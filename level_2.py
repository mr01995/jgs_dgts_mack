import os
import random
import math
import pygame
import sys
from os import listdir
from os.path import isfile, join
from button import *
from pause import draw_pause_menu

pygame.init()

pygame.display.set_caption("Heatwaves")

WIDTH, HEIGHT = 1280, 720
FPS = 60
PLAYER_VEL = 15
global pause
global countdown


window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.life = 10
        self.invencivel = False
        self.invencibilidade_tempo = 500
        self.tempo_dano = 0
        self.jump_sound = pygame.mixer.Sound('assets/Audio/jump.wav')
        self.jump_sound.set_volume(0.5)
        self.hit_sound = pygame.mixer.Sound('assets/Audio/hit.wav')

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.jump_sound.play()
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def tomar_dano(self):
        if not self.invencivel:
            self.life -= 1
            self.hit_sound.play()
            self.invencivel = True
            self.tempo_dano = pygame.time.get_ticks()

    def tempo_invencibilidade(self):
        if self.invencivel:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.tempo_dano >= self.invencibilidade_tempo:
                self.invencivel = False

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x,  offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x,  offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_bathtub_size(size):
    path = join("assets", "House", "bathtub.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, 720, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Bathtub(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        bathtub = get_bathtub_size(size)
        self.image.blit(bathtub, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_closet_size(size):
    path = join("assets", "House", "closet.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, 720, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Closet(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        closet = get_closet_size(size)
        self.image.blit(closet, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_sink_size(size):
    path = join("assets", "House", "sink.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, 720, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Sink(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        sink = get_sink_size(size)
        self.image.blit(sink, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
def get_stove_size(size):
    path = join("assets", "House", "stove.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, 720, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Stove(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        stove = get_stove_size(size)
        self.image.blit(stove, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

def get_toilet_size(size):
    path = join("assets", "House", "toilet.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, 720, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Toilet(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        toilet = get_toilet_size(size)
        self.image.blit(toilet, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    image = pygame.image.load(join("assets", "city", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x,  offset_y):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x,  offset_y)

    player.draw(window, offset_x,  offset_y)

    x = 30
    y = 30
    spacing = 20
    life_width = 60
    life_height = 20
    life_color = (0, 255, 0)  # cor das vidas restantes
    lost_life_color = (0, 0, 0)  # cor das vidas perdidas
    for i in range(player.life):
        pygame.draw.rect(window, life_color, (x, y, life_width, life_height))
        x += spacing

    for i in range(player.life, 10):
        pygame.draw.rect(window, lost_life_color,
                         (x, y, life_width, life_height))
        x += spacing

    pygame.display.update()


def draw_countdown(countdown):

    text = get_font(75).render(str(int(countdown)), True,
                               (255, 255, 255))  # Renderiza o número como texto
    text_rect = text.get_rect(center=(640, 100))  # Centraliza o texto na tela
    window.blit(text, text_rect)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    from main import morte

    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
            player.tomar_dano()
            player.tempo_invencibilidade()
            if player.life <= 0:
                morte()


def main(window):
    from main import morte

    clock = pygame.time.Clock()
    background, bg_image = get_background("bg_nivel_2.png")
    pause = False
    block_size = 96
    countdown = 300

    bathtub_size = 62
    bathtub = Bathtub(100, HEIGHT - bathtub_size * 2 - 58, 720)
    closet_size = 110
    closet = Closet(400, HEIGHT - closet_size * 2 - 58, 720)
    sink_size = 80
    sink = Sink(700, HEIGHT - sink_size * 2 - 58, 720)
    stove_size = 80
    stove = Stove(1200, HEIGHT - stove_size * 2 - 58, 720)
    toilet_size = 80
    toilet = Toilet(1600, HEIGHT - toilet_size * 2 - 58, 720)

    player = Player(100, 100, 50, 50)
    fire = Fire(block_size * 14, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    # esse for de cima vai colocar mais blocos no chão
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 5) // block_size)]

    # um desses aqui coloca blocos na tela
    objects = [*floor,
               #    distancia X altura
               bathtub,
               closet,
               sink,
               stove,
               toilet,
               Block(block_size * 10, HEIGHT - block_size * 3, block_size),
               Block(block_size * 10, HEIGHT - block_size * 4, block_size),
               Block(block_size * 10, HEIGHT - block_size * 5, block_size),
               Block(block_size * 10, HEIGHT - block_size * 6, block_size),
               Block(block_size * 10, HEIGHT - block_size * 7, block_size),
               Block(block_size * 10, HEIGHT - block_size * 8, block_size),
               Block(block_size * 10, HEIGHT - block_size * 9, block_size),
               Block(block_size * 10, HEIGHT - block_size * 10, block_size),
               Block(block_size * 11, HEIGHT - block_size * 10, block_size),
               Block(block_size * 11, HEIGHT - block_size * 11, block_size),
               Block(block_size * 12, HEIGHT - block_size * 11, block_size),
               Block(block_size * 12, HEIGHT - block_size * 12, block_size),
               Block(block_size * 13, HEIGHT - block_size * 12, block_size),
               Block(block_size * 25, HEIGHT - block_size * 3, block_size),
               Block(block_size * 25, HEIGHT - block_size * 4, block_size),
               Block(block_size * 25, HEIGHT - block_size * 5, block_size),
               Block(block_size * 25, HEIGHT - block_size * 6, block_size),
               Block(block_size * 25, HEIGHT - block_size * 7, block_size),
               Block(block_size * 25, HEIGHT - block_size * 8, block_size),
               Block(block_size * 25, HEIGHT - block_size * 9, block_size),
               Block(block_size * 25, HEIGHT - block_size * 10, block_size),
               Block(block_size * 24, HEIGHT - block_size * 10, block_size),
               Block(block_size * 24, HEIGHT - block_size * 11, block_size),
               Block(block_size * 23, HEIGHT - block_size * 11, block_size),
               Block(block_size * 23, HEIGHT - block_size * 12, block_size),
               Block(block_size * 22, HEIGHT - block_size * 12, block_size),
               Block(block_size * 21, HEIGHT - block_size * 12, block_size),
               Block(block_size * 20, HEIGHT - block_size * 12, block_size),
               Block(block_size * 19, HEIGHT - block_size * 12, block_size),
               Block(block_size * 18, HEIGHT - block_size * 12, block_size),
               Block(block_size * 17, HEIGHT - block_size * 12, block_size),
               Block(block_size * 16, HEIGHT - block_size * 12, block_size),
               Block(block_size * 15, HEIGHT - block_size * 12, block_size),
               Block(block_size * 14, HEIGHT - block_size * 12, block_size),
               Block(block_size * 11, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 11.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 12, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 12.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 13, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 13.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 14, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 14.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 15, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 15.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 16, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 16.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 17, HEIGHT - \
                     block_size * 4, block_size/2), fire,
               Block(block_size * 17.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 18, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 18.5, HEIGHT - \
                     block_size * 2.5, block_size/2),
               Block(block_size * 19, HEIGHT - block_size * 3, block_size/2),
               Block(block_size * 19.5, HEIGHT - \
                     block_size * 3.5, block_size/2),
               Block(block_size * 20, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 20.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 21, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 21.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 22, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 22.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 23, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 23.5, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 24, HEIGHT - block_size * 4, block_size/2),
               Block(block_size * 24.5, HEIGHT - block_size * 4, block_size/2),

               Block(block_size * 11, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 11.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 12, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 12.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 13, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 13.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 14, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 14.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 15, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 15.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 16, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 16.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 17, HEIGHT - \
                     block_size * 7, block_size/2), fire,
               Block(block_size * 17.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 18, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 18.5, HEIGHT - \
                     block_size * 6.5, block_size/2),
               Block(block_size * 19, HEIGHT - block_size * 6, block_size/2),
               Block(block_size * 19.5, HEIGHT - \
                     block_size * 5.5, block_size/2),
               Block(block_size * 20, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 20.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 21, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 21.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 22, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 22.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 23, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 23.5, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 24, HEIGHT - block_size * 7, block_size/2),
               Block(block_size * 24.5, HEIGHT - block_size * 7, block_size/2),


               ]

    offset_x = 0
    offset_y = 0
    scroll_area_width = 200
    scroll_area_height = 75

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    pause = not pause

        player.loop(FPS)

        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x,  offset_y)
        draw_countdown(countdown)

        # if pause:
        #     draw_pause_menu(window)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        if ((player.rect.bottom - offset_y >= HEIGHT - scroll_area_height) and player.y_vel > 0) or (
                (player.rect.top - offset_y <= (scroll_area_height + 100)) and player.y_vel < 0):
            offset_y += player.y_vel
        countdown -= clock.tick(60) / 1000

        if countdown <= 0:
            morte()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
