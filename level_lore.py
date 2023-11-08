import pygame
import sys
from button import *
import level_1 as lv1
import level_2 as lv2
import level_3 as lv3


pygame.init()

WIDTH = 1280
HEIGHT = 720

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lore of the characters")

menu_bg = pygame.image.load("assets/Background/Background.gif").convert()
menu_bg = pygame.transform.scale(menu_bg, (1280, 720))


def get_font_title(size):
    return pygame.font.Font("assets/Font/Humanistic.ttf", size)


def level_1():
    from main import level_select
    while True:
        level_mouse_pos = pygame.mouse.get_pos()

        window.fill("white")
        level_selector_bg = pygame.image.load(
            "assets/Background/level_selector_bg.png").convert()
        level_selector_bg = pygame.transform.scale(
            level_selector_bg, (1280, 720))
        window.blit(level_selector_bg, (0, 0))

        title_text = get_font(100).render("ENCHENTE", True, (130, 200, 150))
        title_rect = title_text.get_rect(center=(640, 100))
        window.blit(title_text, title_rect)

        play_button = Button(image=pygame.image.load("assets/ButtonStyle/Play Rect.png"), pos=(640, 400),
                             text_input="Começar", font=get_font(35), base_color="White", hovering_color="Green")
        return_button = Button(image=pygame.image.load("assets/ButtonStyle/return.png"), pos=(100, 650),
                               text_input="<", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        return_button.changeColor(level_mouse_pos)
        return_button.update(window)
        play_button.changeColor(level_mouse_pos)
        play_button.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(level_mouse_pos):
                    lv1.main(window)
                if return_button.checkForInput(level_mouse_pos):
                    level_select()

        pygame.display.update()


def level_2():
    from main import level_select
    while True:
        level_mouse_pos = pygame.mouse.get_pos()

        window.fill("white")
        level_selector_bg = pygame.image.load(
            "assets/Background/level_selector_bg.png").convert()
        level_selector_bg = pygame.transform.scale(
            level_selector_bg, (1280, 720))
        window.blit(level_selector_bg, (0, 0))

        title_text = get_font(100).render(
            "ONDA DE CALOR", True, (130, 200, 150))
        title_rect = title_text.get_rect(center=(640, 100))
        window.blit(title_text, title_rect)

        play_button = Button(image=pygame.image.load("assets/ButtonStyle/Play Rect.png"), pos=(640, 400),
                             text_input="Começar", font=get_font(35), base_color="White", hovering_color="Green")
        return_button = Button(image=pygame.image.load("assets/ButtonStyle/return.png"), pos=(100, 650),
                               text_input="<", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        return_button.changeColor(level_mouse_pos)
        return_button.update(window)
        play_button.changeColor(level_mouse_pos)
        play_button.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(level_mouse_pos):
                    lv2.main(window)
                if return_button.checkForInput(level_mouse_pos):
                    level_select()

        pygame.display.update()


# Nível 3 ainda está em Construção e o código abaixo é placeholder

def level_3():
    from main import level_select
    while True:
        level_mouse_pos = pygame.mouse.get_pos()

        window.fill("white")
        level_selector_bg = pygame.image.load(
            "assets/Background/level_selector_bg.png").convert()
        level_selector_bg = pygame.transform.scale(
            level_selector_bg, (1280, 720))
        window.blit(level_selector_bg, (0, 0))

        title_text = get_font(100).render("Avalanche", True, (130, 200, 150))
        title_rect = title_text.get_rect(center=(640, 100))
        window.blit(title_text, title_rect)

        play_button = Button(image=pygame.image.load("assets/ButtonStyle/Play Rect.png"), pos=(640, 400),
                             text_input="Começar", font=get_font(35), base_color="White", hovering_color="Green")
        return_button = Button(image=pygame.image.load("assets/ButtonStyle/return.png"), pos=(100, 650),
                               text_input="<", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        return_button.changeColor(level_mouse_pos)
        return_button.update(window)
        play_button.changeColor(level_mouse_pos)
        play_button.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(level_mouse_pos):
                    lv3.main(window)
                if return_button.checkForInput(level_mouse_pos):
                    level_select()

        pygame.display.update()
