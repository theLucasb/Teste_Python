import pgzrun
import random
from pygame import Rect

WIDTH = 640
HEIGHT = 480

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"

game_state = STATE_MENU
sound_on = True

try:
    sound_step = sounds.step
except:
    sound_step = None
try:
    sound_hit = sounds.hit
except:
    sound_hit = None
try:
    background_music = sounds.background_music
except:
    background_music = None

hero_idle_frames = [Actor("hero"), Actor("hero")]
hero_walk_frames = [Actor("hero"), Actor("hero")]
enemy_idle_frames = [Actor("enemy"), Actor("enemy")]
enemy_walk_frames = [Actor("enemy"), Actor("enemy")]

button_start = Rect((WIDTH//2 - 70, HEIGHT//2 - 60), (140, 40))
button_sound = Rect((WIDTH//2 - 70, HEIGHT//2), (140, 40))
button_quit = Rect((WIDTH//2 - 70, HEIGHT//2 + 60), (140, 40))

class Character:
    def __init__(self, x, y, idle_frames, walk_frames, speed=2):
        self.x = x
        self.y = y
        self.idle_frames = idle_frames
        self.walk_frames = walk_frames
        self.speed = speed
        self.frame_index = 0
        self.frame_timer = 0
        self.is_moving = False
        self.actor = Actor(idle_frames[0].image)
        self.actor.pos = (self.x, self.y)
        self.direction = (0, 0)

    def update(self):
        self.frame_timer += 1
        if self.frame_timer >= 10:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.idle_frames)
            self.actor.image = self.walk_frames[self.frame_index].image if self.is_moving else self.idle_frames[self.frame_index].image
        if self.is_moving:
            self.x += self.direction[0] * self.speed
            self.y += self.direction[1] * self.speed
            self.x = max(16, min(WIDTH - 16, self.x))
            self.y = max(16, min(HEIGHT - 16, self.y))
            self.actor.pos = (self.x, self.y)

    def draw(self):
        self.actor.draw()

    def rect(self):
        # Corrigido: cria um Retângulo com base na posição e tamanho do ator
        return Rect((self.actor.left, self.actor.top), self.actor.size)

class Enemy(Character):
    def __init__(self, x, y, idle_frames, walk_frames, patrol_area, speed=1):
        super().__init__(x, y, idle_frames, walk_frames, speed)
        self.patrol_area = patrol_area
        self.direction = (random.choice([-1, 1]), random.choice([-1, 1]))
        self.change_dir_timer = 0

    def update(self):
        super().update()
        self.change_dir_timer += 1
        if self.change_dir_timer > 120:
            self.change_dir_timer = 0
            self.direction = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
            self.is_moving = self.direction != (0, 0)
        min_x, max_x, min_y, max_y = self.patrol_area
        if not (min_x <= self.x + self.direction[0]*self.speed <= max_x):
            self.direction = (-self.direction[0], self.direction[1])
        if not (min_y <= self.y + self.direction[1]*self.speed <= max_y):
            self.direction = (self.direction[0], -self.direction[1])

hero = Character(WIDTH // 2, HEIGHT // 2, hero_idle_frames, hero_walk_frames, speed=3)
enemies = [
    Enemy(100, 100, enemy_idle_frames, enemy_walk_frames, (80, 150, 80, 150), speed=1),
    Enemy(500, 150, enemy_idle_frames, enemy_walk_frames, (480, 550, 130, 180), speed=1),
    Enemy(300, 350, enemy_idle_frames, enemy_walk_frames, (280, 350, 320, 400), speed=1),
]

def draw_menu():
    screen.fill((30, 30, 30))
    screen.draw.text("Roguelike Demo", center=(WIDTH//2, HEIGHT//2 - 120), fontsize=50, color="white")
    screen.draw.filled_rect(button_start, (70, 130, 180))
    screen.draw.text("Start Game", center=button_start.center, color="white", fontsize=30)
    screen.draw.filled_rect(button_sound, (70, 130, 180))
    sound_text = "Sound: ON" if sound_on else "Sound: OFF"
    screen.draw.text(sound_text, center=button_sound.center, color="white", fontsize=30)
    screen.draw.filled_rect(button_quit, (180, 70, 70))
    screen.draw.text("Quit", center=button_quit.center, color="white", fontsize=30)

def draw():
    screen.clear()
    if game_state == STATE_MENU:
        draw_menu()
    elif game_state == STATE_PLAYING:
        hero.draw()
        for e in enemies:
            e.draw()
    elif game_state == STATE_GAMEOVER:
        screen.fill((100, 0, 0))
        screen.draw.text("Game Over!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
        screen.draw.text("Click to return to Menu", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=30, color="white")

def update():
    global game_state
    if game_state == STATE_PLAYING:
        keys = keyboard
        dx = dy = 0
        if keys.left: dx = -1
        elif keys.right: dx = 1
        if keys.up: dy = -1
        elif keys.down: dy = 1
        hero.direction = (dx, dy)
        hero.is_moving = dx != 0 or dy != 0
        hero.update()
        for enemy in enemies:
            enemy.update()
        for enemy in enemies:
            if hero.rect().colliderect(enemy.rect()):
                if sound_on and sound_hit:
                    sound_hit.play()
                if background_music:
                    background_music.stop()
                game_state = STATE_GAMEOVER
        if sound_on and hero.is_moving and sound_step and (hero.frame_timer == 0):
            sound_step.play()

def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == STATE_MENU:
        if button_start.collidepoint(pos):
            game_state = STATE_PLAYING
            if sound_on and background_music:
                background_music.play()
        elif button_sound.collidepoint(pos):
            sound_on = not sound_on
            if not sound_on and background_music:
                background_music.stop()
        elif button_quit.collidepoint(pos):
            exit()
    elif game_state == STATE_GAMEOVER:
        game_state = STATE_MENU

pgzrun.go()
