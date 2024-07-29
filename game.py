import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random

class IntroScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Batman's Adventure - Intro")
        self.init_opengl()
        self.intro_texture = self.load_texture('assets/images/WhatsApp Image 2024-07-15 at 11.28.57 PM.jpeg')
        self.intro_music = 'assets/music/THE BATMAN Theme Michael Giacchino (Main Trailer Music).mp3'
        self.running = True

    def init_opengl(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)

    def load_texture(self, image_path):
        img = pygame.image.load(image_path)
        img_data = pygame.image.tostring(img, "RGBA", 1)
        width, height = img.get_size()
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        return texture

    def run(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.intro_music)
        pygame.mixer.music.play(-1)

        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.running = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.draw_intro()

            pygame.display.flip()
            clock.tick(60)

        pygame.mixer.music.stop()

    def draw_intro(self):
        glBindTexture(GL_TEXTURE_2D, self.intro_texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(self.width, 0)
        glTexCoord2f(1, 1); glVertex2f(self.width, self.height)
        glTexCoord2f(0, 1); glVertex2f(0, self.height)
        glEnd()

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Batman's Adventure")
        self.init_opengl()
        self.character_texture = self.load_texture('assets/images/imgbin_pixel-art-batman-png.png')
        self.item_texture = self.load_texture('assets/images/toppng.com-batman-logo-png-batman-symbol-black-and-white-2400x1303.png')
        self.obstacle_texture = self.load_texture('assets/images/—Pngtree—tips obstacle warning_1034699.png')
        self.background_texture = self.load_texture('assets/images/Gotham City Backgrounds - Wallpaper Cave.jpeg')
        self.character_pos = [width // 4, height // 2]
        self.character_velocity = [5, 0]  # Batman now runs continuously
        self.gravity = -0.5
        self.jump_power = 10
        self.items = []
        self.obstacles = []
        self.platforms = []
        self.score = 0
        self.distance = 0
        self.lives = 3
        self.running = True
        self.level = 1
        self.difficulty = "Easy"
        self.base_obstacle_speed = 3
        self.base_item_speed = 2
        self.obstacle_speed = self.base_obstacle_speed
        self.item_speed = self.base_item_speed
        self.obstacle_frequency = 120
        self.item_frequency = 90
        self.item_timer = 0
        self.obstacle_timer = 0
        self.ground_level = 100  # Height of the ground from the bottom of the screen

        self.background_music = 'assets/music/The Dark Knight Rises Official Soundtrack Despair Hans Zimmer WaterTower.mp3'

        pygame.mixer.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

        self.init_platforms()

    def init_opengl(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def load_texture(self, image_path):
        img = pygame.image.load(image_path)
        img_data = pygame.image.tostring(img, "RGBA", 1)
        width, height = img.get_size()
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        return texture

    def init_platforms(self):
        platform_width = self.width // 3
        for i in range(3):
            x = i * platform_width
            y = self.ground_level
            self.platforms.append((x, y, platform_width, 10))

    def update_game_state(self):
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and self.on_platform():
            self.character_velocity[1] = self.jump_power

        self.character_velocity[1] += self.gravity
        self.character_pos[1] += self.character_velocity[1]

        # Check platform collisions
        on_platform = False
        for platform in self.platforms:
            if (self.character_pos[0] + 50 > platform[0] and self.character_pos[0] < platform[0] + platform[2] and
                self.character_pos[1] <= platform[1] + platform[3] and self.character_pos[1] + 50 >= platform[1] + platform[3]):
                self.character_pos[1] = platform[1] + platform[3]
                self.character_velocity[1] = 0
                on_platform = True
                break

        if not on_platform:
            self.character_pos[1] = max(self.ground_level, self.character_pos[1])

        self.distance += self.character_velocity[0]
        self.score = self.distance // 100

        self.item_timer += 1
        self.obstacle_timer += 1
        if self.item_timer > self.item_frequency:
            self.item_timer = 0
            self.spawn_item()
        if self.obstacle_timer > self.obstacle_frequency:
            self.obstacle_timer = 0
            self.spawn_obstacle()

        for item in self.items[:]:
            item[0] -= self.item_speed + self.character_velocity[0]
            if item[0] < 0:
                self.items.remove(item)
            elif self.check_collision(self.character_pos, item, [50, 50], [30, 30]):
                self.items.remove(item)
                self.score += 10

        for obstacle in self.obstacles[:]:
            x, y, width, height = obstacle
            x -= self.obstacle_speed + self.character_velocity[0]
            if x < -width:
                self.obstacles.remove(obstacle)
            elif self.check_collision(self.character_pos, [x, y], [50, 50], [width, height]):
                self.lives -= 1
                self.obstacles.remove(obstacle)
                if self.lives <= 0:
                    self.show_game_over()
                    return
            else:
                self.obstacles[self.obstacles.index(obstacle)] = (x, y, width, height)

        for i, platform in enumerate(self.platforms):
            x, y, width, height = platform
            x -= self.character_velocity[0]
            if x + width < 0:
                x = self.width
            self.platforms[i] = (x, y, width, height)

        self.level_up()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_SPACE and self.on_platform():
                    self.character_velocity[1] = self.jump_power

    def on_platform(self):
        for platform in self.platforms:
            if (self.character_pos[0] + 50 > platform[0] and self.character_pos[0] < platform[0] + platform[2] and
                self.character_pos[1] <= platform[1] + platform[3] and self.character_pos[1] + 50 >= platform[1] + platform[3]):
                return True
        return False

    def spawn_item(self):
        platform = random.choice(self.platforms)
        x = platform[0] + platform[2]  # Spawn at the right edge of the platform
        y = platform[1] + platform[3] + random.randint(50, 150)  # Spawn above the platform
        self.items.append([x, y])

    def spawn_obstacle(self):
        platform = random.choice(self.platforms)
        x = platform[0] + platform[2]  # Spawn at the right edge of the platform
        y = platform[1] + platform[3]  # Spawn on top of the platform
        width = random.randint(30, 60)
        height = random.randint(30, 60)
        self.obstacles.append((x, y, width, height))

    def level_up(self):
        if self.score > 0 and self.score % 100 == 0:
            self.level += 1
            self.character_velocity[0] += 0.5
            self.obstacle_speed += 0.5
            self.item_speed += 0.5
            self.obstacle_frequency = max(30, self.obstacle_frequency - 5)
            self.item_frequency = max(20, self.item_frequency - 5)

    def check_collision(self, pos1, pos2, size1, size2):
        return (pos1[0] < pos2[0] + size2[0] and pos1[0] + size1[0] > pos2[0] and
                pos1[1] < pos2[1] + size2[1] and pos1[1] + size1[1] > pos2[1])

    def show_game_over(self):
        # Pause the background music
        pygame.mixer.music.pause()

        game_over_font = pygame.font.Font(None, 74)
        retry_font = pygame.font.Font(None, 36)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Unpause the music when restarting
                        pygame.mixer.music.unpause()
                        self.reset_game()
                        return

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
            retry_text = retry_font.render("Press Enter to Retry", True, (255, 255, 255))
            self.draw_text(game_over_text, self.width // 2 - game_over_text.get_width() // 2, self.height // 2)
            self.draw_text(retry_text, self.width // 2 - retry_text.get_width() // 2, self.height // 2 - 50)

            pygame.display.flip()

    def draw_text(self, text, x, y):
        text_data = pygame.image.tostring(text, "RGBA", 1)
        width, height = text.get_size()
        
        glWindowPos2i(x, y)
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def draw_game(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw scrolling background
        bg_scroll = int(self.distance % self.width)
        glBindTexture(GL_TEXTURE_2D, self.background_texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-bg_scroll, 0)
        glTexCoord2f(1, 0); glVertex2f(self.width - bg_scroll, 0)
        glTexCoord2f(1, 1); glVertex2f(self.width - bg_scroll, self.height)
        glTexCoord2f(0, 1); glVertex2f(-bg_scroll, self.height)
        glEnd()
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(self.width - bg_scroll, 0)
        glTexCoord2f(0, 0); glVertex2f(self.width - bg_scroll, 0)
        glTexCoord2f(1, 0); glVertex2f(2*self.width - bg_scroll, 0)
        glTexCoord2f(1, 1); glVertex2f(2*self.width - bg_scroll, self.height)
        glTexCoord2f(0, 1); glVertex2f(self.width - bg_scroll, self.height)
        glEnd()

        self.draw_character()
        self.draw_items()
        self.draw_obstacles()
        self.draw_platforms()
        self.draw_score()
        self.draw_lives()
        self.draw_level()

    def draw_character(self):
        glBindTexture(GL_TEXTURE_2D, self.character_texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(self.character_pos[0], self.character_pos[1])
        glTexCoord2f(1, 0); glVertex2f(self.character_pos[0] + 50, self.character_pos[1])
        glTexCoord2f(1, 1); glVertex2f(self.character_pos[0] + 50, self.character_pos[1] + 50)
        glTexCoord2f(0, 1); glVertex2f(self.character_pos[0], self.character_pos[1] + 50)
        glEnd()

    def draw_items(self):
        glBindTexture(GL_TEXTURE_2D, self.item_texture)
        for item in self.items:
            x, y = item
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + 30, y)
            glTexCoord2f(1, 1); glVertex2f(x + 30, y + 30)
            glTexCoord2f(0, 1); glVertex2f(x, y + 30)
            glEnd()

    def draw_obstacles(self):
        glBindTexture(GL_TEXTURE_2D, self.obstacle_texture)
        for obstacle in self.obstacles:
            x, y, width, height = obstacle
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + width, y)
            glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
            glTexCoord2f(0, 1); glVertex2f(x, y + height)
            glEnd()

    def draw_platforms(self):
        glBindTexture(GL_TEXTURE_2D, 0)  # No texture, just color
        glColor3f(0.5, 0.5, 0.5)  # Set platform color to gray
        for platform in self.platforms:
            x, y, width, height = platform
            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + width, y)
            glVertex2f(x + width, y + height)
            glVertex2f(x, y + height)
            glEnd()
        glColor3f(1.0, 1.0, 1.0)  # Reset color to white

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.draw_text(score_text, 10, self.height - 30)

    def draw_lives(self):
        lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.draw_text(lives_text, self.width - 100, self.height - 30)

    def draw_level(self):
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.draw_text(level_text, self.width // 2 - 50, self.height - 30)

    def reset_game(self):
        self.character_pos = [self.width // 4, self.height // 2]
        self.character_velocity = [5, 0]
        self.items = []
        self.obstacles = []
        self.init_platforms()
        self.score = 0
        self.distance = 0
        self.lives = 3
        self.level = 1
        self.obstacle_speed = self.base_obstacle_speed
        self.item_speed = self.base_item_speed
        self.obstacle_frequency = 120
        self.item_frequency = 90
        self.item_timer = 0
        self.obstacle_timer = 0
        self.running = True

        # Restart the background music
        pygame.mixer.music.play(-1)

    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        # Start playing background music
        pygame.mixer.music.load(self.background_music)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely

        while self.running:
            self.handle_events()
            self.update_game_state()
            self.draw_game()
            pygame.display.flip()
            clock.tick(60)

        # Stop the music when the game ends
        pygame.mixer.music.stop()

def main():
    pygame.init()
    width, height = 800, 600
    intro = IntroScreen(width, height)
    intro.run()
    game = Game(width, height)
    game.run()

if __name__ == "__main__":
    main()