import pygame
from intro_screen import IntroScreen
from game import Game

def main():
    pygame.init()
    width, height = 800, 600

    intro = IntroScreen(width, height)
    intro.run()

    game = Game(width, height)
    game.run()

if __name__ == "__main__":
    main()
