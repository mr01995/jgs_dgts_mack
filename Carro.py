# class Carro(Object):
#     def __init__(self, x, y, width, height):
#         super().__init__(x, y, width, height, "carro")
#         self.carro = load_sprite_sheets("cars", "Jeep_1", width, height)
#         # self.image = self.carro["Brake"][0]
#         self.mask = pygame.mask.from_surface(self.image)
#         # self.animation_name = "Brake"

# def draw(window, background, bg_image, player, carro, objects, offset_x):
#     for tile in background:
#         window.blit(bg_image, tile)

#     for obj in objects:
#         obj.draw(window, offset_x)

#     player.draw(window, offset_x)
#     carro.draw(window, offset_x)

#     #BLOCK
#     #    Carro(1000, 100, 200, 200),

# carro = Carro(1000, 100, 200, 200)
# # WHILE
#         draw(window, background, bg_image, player, carro, objects, offset_x)

# def get_car(size):
#     path = join("assets", "Cars", "Jeep_1", "Brake.png")
#     image = pygame.image.load(path).convert_alpha()
#     surface = pygame.Surface((size, size), pygame.SRCALPHA, 16)
#     rect = pygame.Rect(200, 200, size, size)
#     surface.blit(image, (0, 0), rect)
#     return pygame.transform.scale2x(surface)


# class Car(Object):
#     def __init__(self, x, y, size):
#         super().__init__(x, y, size, size)
#         block = get_car(size)
#         self.image.blit(block, (0, 0))
#         self.mask = pygame.mask.from_surface(self.image)

