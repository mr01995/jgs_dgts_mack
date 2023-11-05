import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 900, 600
FPS = 60
PLAYER_VEL = 5

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

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
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

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# Função que retorna imagem do bloco


def get_block(size):
    # Pega o caminho da imagem
    path = join("assets", "Terrain", "Terrain.png")
    # Pega a imagem e converte para transprente
    image = pygame.image.load(path).convert_alpha()
    # Cria uma superfície
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    # Cria o retangulo pegando a imagem e o tamanho de uma imagem grande
    rect = pygame.Rect(96, 0, size, size)
    # Desenha a imagem na superfície
    surface.blit(image, (0, 0), rect)
    # Retorna a superfície
    return pygame.transform.scale2x(surface)

# Objeto bloco que herda da classe Object


class Block(Object):
    # Construtor
    def __init__(self, x, y, size):
        # Chama o construtor da classe pai
        super().__init__(x, y, size, size)
        # Carrega as imagens do bloco
        block = get_block(size)
        # Desenha o bloco
        self.image.blit(block, (0, 0))
        # Cria uma mascara para o objeto
        self.mask = pygame.mask.from_surface(self.image)

# Objeto carro que herda da classe Object


# def get_block(size):
#     # Pega o caminho da imagem
#     path = join("assets", "Terrain", "Terrain.png")
#     # Pega a imagem e converte para transprente
#     image = pygame.image.load(path).convert_alpha()
#     # Cria uma superfície
#     surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
#     # Cria o retangulo pegando a imagem e o tamanho de uma imagem grande
#     rect = pygame.Rect(200, 200, size, size)
#     # Desenha a imagem na superfície
#     surface.blit(image, (0, 0), rect)
#     # Retorna a superfície
#     return pygame.transform.scale2x(surface)


class Car(Object):
    # Construtor
    def __init__(self, x, y, width, height):
        # Chama o construtor da classe pai
        super().__init__(x, y, width, height, "Brake")
        # Carrega as imagens
        self.car = load_sprite_sheets("Cars", "Jeep_1", width, height)
        self.image = self.car["Brake"][0]
        # Seleciona a imagem
        # self.image.blit(car, (0, 0))
        # Cria uma mascara para o objeto
        self.mask = pygame.mask.from_surface(self.image)
# preciso rever o video e como ele faz para reconhoecer o carro como um objeto assim como um bloco
# Pega as imagne


def get_background(name):
    # Vasculha os arquivos filtrando pelo nome
    image = pygame.image.load(join("assets", "Background", name))
    # Pega os tamanos
    _, _, width, height = image.get_rect()
    # Matriz de ladrilhos
    tiles = []

    # Vasculha os ladrilhos e preenche a matriz
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    # Retorna as imagens e a matriz de ladrilhos
    return tiles, image

# Desenha os objetos que foram passados nos parametros


def draw(window, background, bg_image, player, objects, offset_x):

    # pega os ladrilhos e desenha cada um
    for tile in background:
        window.blit(bg_image, tile)

    # Percorre a lista de objetos e desenha cada um
    for obj in objects:
        obj.draw(window, offset_x)

    # Desenha o jogador
    player.draw(window, offset_x)

    # atualiza atela
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
    # Pega as teclas
    keys = pygame.key.get_pressed()
    # Velocidade
    player.x_vel = 0
    # Colisão na esquerda
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    # Colisão na direita
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    # Verifica as teclas
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    # Verifica as colisões
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    # Verifica as colisões
    to_check = [collide_left, collide_right, *vertical_collide]

    # Verifica as colisões
    for obj in to_check:
        if obj and obj.name == "Brake":
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()

    # Fundo e imagem de fundo
    background, bg_image = get_background("Blue.png")

    # Tamanho do bloco
    block_size = 96

    # Jogador
    player = Player(100, 100, 50, 50)
    # Car
    car = Car(1020, 120, 200, 200)

    # Plataformas
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 5) // block_size)]

    # Objetos que serão renderizados e colididos
    objects = [*floor,
               # Criando blocos que ficam flutuando na tela e pelo ar
               Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 3, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size),
               Block(block_size * 4, HEIGHT - block_size * 4, block_size),
               Block(block_size * 5, HEIGHT - block_size * 4, block_size),
               Block(block_size * 6, HEIGHT - block_size * 4, block_size),
               Block(block_size * 6, HEIGHT - block_size * 2, block_size),
               Block(block_size * 11, HEIGHT - block_size * 4, block_size),
               Block(block_size * 8, HEIGHT - block_size * 2, block_size),
               car,
               ]

    offset_x = 0
    # Area de rolagem para alinhamento com o jogador
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)
        # Eventos
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

        # Loop do jogador
        player.loop(FPS)

        # Manegador de movimentos veridica colisões
        handle_move(player, objects)

        # Desenha os elementos passados nos parametros
        draw(window, background, bg_image, player, objects, offset_x)

        #   Alinha a tela com o jogador
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
