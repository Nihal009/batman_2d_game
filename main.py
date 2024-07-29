import pygame
from pygame.locals import *
from game import IntroScreen, Game

def main():
    pygame.init()
    width, height = 800, 600
    intro = IntroScreen(width, height)
    intro.run()

    game = Game(width, height)
    game.run()

if __name__ == "__main__":
    main()
