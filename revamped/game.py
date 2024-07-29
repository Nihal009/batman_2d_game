import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from graphics import load_texture, draw_quad, load_maze

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("2D Maze Game")
        self.init_opengl()
        self.character_texture = load_texture('assets/images/imgbin_pixel-art-batman-png.png')
        self.item_texture = load_texture('assets/images/toppng.com-batman-logo-png-batman-symbol-black-and-white-2400x1303.png')
        self.obstacle_texture = load_texture('assets/images/—Pngtree—tips obstacle warning_1034699.png')
        self.background_texture = load_texture('assets/images/Gotham City Backgrounds - Wallpaper Cave.jpeg')
        self.joker_texture = load_texture('assets/images/imgbin_pixel-art-batman-png.png')
        self.character_pos = [50, 50]
        self.character_size = 50
        self.maze, self.items, self.joker_pos = self.load_maze('assets/images/maze.png')
        self.score = 0
        self.lives = 5
        self.running = True

    def init_opengl(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)

    def load_maze(self, image_path):
        maze, items, joker_pos = load_maze(image_path)
        return maze, items, joker_pos

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.move_character(0, 5)
            if keys[pygame.K_DOWN]:
                self.move_character(0, -5)
            if keys[pygame.K_LEFT]:
                self.move_character(-5, 0)
            if keys[pygame.K_RIGHT]:
                self.move_character(5, 0)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.draw_maze()
            draw_quad(self.character_texture, self.character_pos[0], self.character_pos[1], self.character_size, self.character_size)
            self.draw_items()
            self.draw_joker()
            self.draw_text(f'Score: {self.score}', 10, self.height - 30)
            self.draw_text(f'Lives: {self.lives}', self.width - 150, self.height - 30)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        print(f"Game Over! Your score: {self.score}")

    def draw_maze(self):
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == '#':
                    draw_quad(self.obstacle_texture, x * 50, y * 50, 50, 50)

    def draw_items(self):
        for item in self.items:
            draw_quad(self.item_texture, item[0], item[1], 30, 30)
            if self.character_pos[0] < item[0] + 30 and self.character_pos[0] + self.character_size > item[0] and \
               self.character_pos[1] < item[1] + 30 and self.character_pos[1] + self.character_size > item[1]:
                self.items.remove(item)
                self.score += 1

    def draw_joker(self):
        draw_quad(self.joker_texture, self.joker_pos[0], self.joker_pos[1], 50, 50)
        if self.character_pos[0] < self.joker_pos[0] + 50 and self.character_pos[0] + self.character_size > self.joker_pos[0] and \
           self.character_pos[1] < self.joker_pos[1] + 50 and self.character_pos[1] + self.character_size > self.joker_pos[1]:
            self.running = False
            print("You reached the Joker!")

    def move_character(self, dx, dy):
        new_pos = [self.character_pos[0] + dx, self.character_pos[1] + dy]
        cell_x = new_pos[0] // 50
        cell_y = new_pos[1] // 50
        if self.maze[cell_y][cell_x] == ' ':
            self.character_pos = new_pos

    def draw_text(self, text, x, y):
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render(text, True, (255, 255, 255))
        self.window.blit(text_surface, (x, y))
