
import pygame
import random
import json
import math
import os 

# Initialize Pygame
pygame.init()
bg = pygame.image.load("assets/backgroundd.png")
akey = pygame.transform.scale(pygame.image.load("assets/a keyy.png"), (60, 60))
akey2 = pygame.transform.scale(pygame.image.load("assets/akey2.png"), (60, 60))
skey = pygame.transform.scale(pygame.image.load("assets/s_light.png"), (60, 60))
skey2 = pygame.transform.scale(pygame.image.load("assets/s_dark.png"), (60, 60))
dkey = pygame.transform.scale(pygame.image.load("assets/d_light.png"), (60, 60))
dkey2 = pygame.transform.scale(pygame.image.load("assets/d_dark.png"), (60, 60))
fkey = pygame.transform.scale(pygame.image.load("assets/f_light.png"), (60, 60))
fkey2 = pygame.transform.scale(pygame.image.load("assets/f_dark.png"), (60, 60))

note_image = pygame.transform.scale(pygame.image.load("assets/tool.png"), (20, 20))

# Load level data
with open('json/level.json', 'r') as f: 
    level_data = json.load(f)

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
NOTE_SPEED = 73.6
LANE_WIDTH = SCREEN_WIDTH // 4
HIT_Y = 525  # Aligning hit area with key sprites
SCROLLING_TEXT_DURATION = 4000  



NOTE_WIDTH, NOTE_HEIGHT = note_image.get_size()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Key mapping
KEYS = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
LANES = [59, 137, 215, 293]

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Rhythm Game')

clock = pygame.time.Clock()

notes = []
title_font = pygame.font.Font('assets/upheavtt.ttf', 24)  

class TitleState:
    def __init__(self):
        self.frame = 0
        self.animation1_frames = [pygame.image.load(f"animation1/frame{i:04d}.png") for i in range(120)]
        self.animation2_frames = [pygame.image.load(f"animation2/frame{i:04d}.png") for i in range(120)]
        self.animation1_rect = self.animation1_frames[0].get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.animation2_rect = self.animation2_frames[0].get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # start animation
                    self.frame = 0

    def draw(self):
        screen.fill(BLACK)

        # draw animation
        if self.frame < len(self.animation1_frames):
            screen.blit(self.animation1_frames[self.frame], self.animation1_rect)
            screen.blit(self.animation2_frames[self.frame], self.animation2_rect)
            self.frame += 1

        # draw title text
        font = pygame.font.Font('assets/upheavtt.ttf', 64)
        title_text = font.render("Rhythm Game", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        wave_y = SCREEN_HEIGHT / 2 + 10 * math.sin(pygame.time.get_ticks() * 0.005)
        screen.blit(title_text, (title_rect.x, wave_y))

        font = pygame.font.Font('assets/upheavtt.ttf', 32)
        press_space_text = "Press Space to continue"
        for i, char in enumerate(press_space_text):
            char_surface = font.render(char, True, WHITE)
            char_rect = char_surface.get_rect(center=(SCREEN_WIDTH / 2 - len(press_space_text) * 10 / 2 + i * 20, SCREEN_HEIGHT * 0.8 + 5 * math.sin(pygame.time.get_ticks() * 0.005 + math.pi / 2)))
            if char_rect.collidepoint(pygame.mouse.get_pos()):
                color_angle = pygame.time.get_ticks() * 0.01 + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                char_surface = font.render(char, True, (r, g, b))
                char_rect.y += 5 * math.sin(pygame.time.get_ticks() * 0.01 + i * 0.1)
            screen.blit(char_surface, char_rect)

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.size, self.size))

class Menu:
    def __init__(self, options, trails):
        self.options = options
        self.selected_option = 0
        self.sin_offset = 0
        self.hover_option = None
        self.mouse_trail = []
        self.trails = trails
        self.selected_trail = 0
        self.trail_dropdown_open = False
        self.trail_rects = []
        self.trail_dropdown_rect = pygame.Rect(10, 10, 150, 20) 

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected_option  
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.trail_dropdown_rect.collidepoint(mouse_pos):
                self.trail_dropdown_open = not self.trail_dropdown_open
            for i, trail_rect in enumerate(self.trail_rects):
                if trail_rect.collidepoint(mouse_pos):
                    self.selected_trail = i
                    self.trail_dropdown_open = False
        return None

    def draw(self, screen, title_font):
        screen.fill(BLACK)

        self.sin_offset += 0.2
        mouse_pos = pygame.mouse.get_pos()
        self.hover_option = None
        for idx, option in enumerate(self.options):
            option_rect = pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30)
            if option_rect.collidepoint(mouse_pos):
                self.hover_option = idx

            if idx == self.hover_option:
                self.draw_option(screen, title_font, option, idx)
            else:
                text = title_font.render(option, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + idx * 50))

      # Draw trail dropdown button
            pygame.draw.rect(screen, (255, 255, 255), self.trail_dropdown_rect) 
            trail_text = title_font.render("Trail: " + self.trails[self.selected_trail], True, (0, 0, 0))
            screen.blit(trail_text, (self.trail_dropdown_rect.x + 10, self.trail_dropdown_rect.y + 5))  
        if self.trail_dropdown_open:
            if not self.trail_rects:
                self.trail_rects = []
                for i, trail in enumerate(self.trails):
                    trail_rect = pygame.Rect(
                        self.trail_dropdown_rect.x,
                        self.trail_dropdown_rect.y + (i + 1) * 20,
                        self.trail_dropdown_rect.width,
                        20
                    )
                    self.trail_rects.append(trail_rect)

            small_font = pygame.font.Font('assets/upheavtt.ttf', 14)  

            for i, trail_rect in enumerate(self.trail_rects):
                pygame.draw.rect(screen, (255, 255, 255), trail_rect)
                trail_text = small_font.render(self.trails[i], True, (0, 0, 0))
                text_rect = trail_text.get_rect(center=trail_rect.center)
                screen.blit(trail_text, text_rect)
                pygame.draw.line(screen, (0, 0, 0), (trail_rect.x, trail_rect.y), (trail_rect.x + trail_rect.width, trail_rect.y), 1)
        else:
            self.trail_rects = []
        # Draw trail
        if self.selected_trail == 0:
            # No trail
            pass
        elif self.selected_trail == 1:
            # RGB Trail
            self.mouse_trail.append((mouse_pos, self.sin_offset))
            if len(self.mouse_trail) > 100:
                self.mouse_trail.pop(0)

            # Draw magical pixels
            for i, (pos, offset) in enumerate(self.mouse_trail):
                color_angle = offset + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                opacity = int(255 * (1 - i / len(self.mouse_trail)))
                x = pos[0] + math.sin(offset + i * 0.1) * 5
                y = pos[1] + math.sin(offset + i * 0.1 + math.pi / 2) * 5
                s = pygame.Surface((5, 5), pygame.SRCALPHA)
                s.set_alpha(opacity)  # Set alpha value
                pygame.draw.circle(s, (r, g, b), (2, 2), 2)
                screen.blit(s, (int(x), int(y)))
        elif self.selected_trail == 2:
                # Neon Trail
                self.mouse_trail.append((mouse_pos, self.sin_offset))
                if len(self.mouse_trail) > 100:
                    self.mouse_trail.pop(0)

                for i, (pos, offset) in enumerate(self.mouse_trail):
                    color = (57, 255, 20)  # Neon green
                    opacity = int(255 * (1 - i / len(self.mouse_trail)))
                    s = pygame.Surface((5, 5), pygame.SRCALPHA)
                    s.set_alpha(opacity)
                    pygame.draw.circle(s, color, (2, 2), 2)
                    screen.blit(s, pos)
        elif self.selected_trail == 3:
            # Sparkle Trail
            self.mouse_trail.append((mouse_pos, self.sin_offset))
            if len(self.mouse_trail) > 100:
                self.mouse_trail.pop(0)

            for i, (pos, offset) in enumerate(self.mouse_trail):
                opacity = int(255 * (1 - i / len(self.mouse_trail)))
                s = pygame.Surface((8, 8), pygame.SRCALPHA)
                s.set_alpha(opacity)
                # Draw 8-bit star
                pygame.draw.line(s, (255, 255, 255), (0, 4), (8, 4), 2)
                pygame.draw.line(s, (255, 255, 255), (4, 0), (4, 8), 2)
                pygame.draw.line(s, (255, 255, 255), (0, 0), (8, 8), 2)
                pygame.draw.line(s, (255, 255, 255), (8, 0), (0, 8), 2)
                screen.blit(s, (pos[0] - 4, pos[1] - 4))
        elif self.selected_trail == 4:
                # Fire Trail
                self.mouse_trail.append((mouse_pos, self.sin_offset))
                if len(self.mouse_trail) > 100:
                    self.mouse_trail.pop(0)

                for i, (pos, offset) in enumerate(self.mouse_trail):
                    fire_size = random.randint(3, 6)
                    color = (255, random.randint(100, 200), 0)  # Orange-red fire
                    opacity = int(255 * (1 - i / len(self.mouse_trail)))
                    s = pygame.Surface((fire_size, fire_size), pygame.SRCALPHA)
                    s.set_alpha(opacity)
                    pygame.draw.circle(s, color, (fire_size // 2, fire_size // 2), fire_size // 2)
                    screen.blit(s, pos)
        elif self.selected_trail == 5:
            # Rainbow Trail
            self.mouse_trail.append((mouse_pos, self.sin_offset))
            if len(self.mouse_trail) > 100:
                self.mouse_trail.pop(0)

            for i, (pos, offset) in enumerate(self.mouse_trail):
                rainbow_angle = offset + i * 0.1
                r = int(math.sin(rainbow_angle) * 128 + 128)
                g = int(math.sin(rainbow_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(rainbow_angle + 4 * math.pi / 3) * 128 + 128)
                opacity = int(255 * (1 - i / len(self.mouse_trail)))
                s = pygame.Surface((5, 5), pygame.SRCALPHA)
                s.set_alpha(opacity)
                pygame.draw.circle(s, (r, g, b), (2, 2), 2)
                screen.blit(s, pos)
        elif self.selected_trail == 6:
            # Starburst Trail
            if not hasattr(self, 'starburst_trails'):
                self.starburst_trails = []

            self.starburst_trails.append({
                'pos': mouse_pos,
                'stars': [
                    {'x': mouse_pos[0], 'y': mouse_pos[1], 'vx': 2, 'vy': 2, 'opacity': 255},
                    {'x': mouse_pos[0], 'y': mouse_pos[1], 'vx': -2, 'vy': 2, 'opacity': 255},
                    {'x': mouse_pos[0], 'y': mouse_pos[1], 'vx': 2, 'vy': -2, 'opacity': 255},
                    {'x': mouse_pos[0], 'y': mouse_pos[1], 'vx': -2, 'vy': -2, 'opacity': 255}
                ]
            })

            for trail in self.starburst_trails:
                for star in trail['stars']:
                    star['x'] += star['vx']
                    star['y'] += star['vy']

                    if star['x'] < 0 or star['x'] > SCREEN_WIDTH:
                        star['vx'] = -star['vx']
                    if star['y'] < 0 or star['y'] > SCREEN_HEIGHT:
                        star['vy'] = -star['vy']

                    star['opacity'] -= 5
                    if star['opacity'] < 0:
                        star['opacity'] = 0

                    s = pygame.Surface((8, 8), pygame.SRCALPHA)
                    s.set_alpha(star['opacity'])
                    # Draw 8-bit star
                    pygame.draw.line(s, (255, 255, 255), (0, 4), (8, 4), 2)
                    pygame.draw.line(s, (255, 255, 255), (4, 0), (4, 8), 2)
                    pygame.draw.line(s, (255, 255, 255), (0, 0), (8, 8), 2)
                    pygame.draw.line(s, (255, 255, 255), (8, 0), (0, 8), 2)
                    screen.blit(s, (star['x'] - 4, star['y'] - 4))

            self.starburst_trails = [trail for trail in self.starburst_trails if any(star['opacity'] > 0 for star in trail['stars'])]



    def draw_option(self, screen, font, option, idx):
        # Draw hovered option with sine wave movement and RGB letters
        text = ''
        for i, char in enumerate(option):
            color_angle = self.sin_offset + i * 0.1
            r = int(math.sin(color_angle) * 128 + 128)
            g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
            b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
            char_surface = font.render(char, True, (r, g, b))
            screen.blit(char_surface, (SCREEN_WIDTH // 2 - len(option) * 20 // 2 + i * 20, 200 + idx * 50 + math.sin(self.sin_offset + idx) * 5))



options = ['Play Level', 'Settings', 'Quit']

trails = ["No Trail", "RGB Trail", "Neon Trail", "Sparkle Trail", "Fire Trail", "Rainbow Trail", "Starburst Trail"]

menu = Menu(["Play Level", "Settings", "Quit"], trails)


title_text = title_font.render("Rhythm Game", True, WHITE)
title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))


# Define game states
STATE_TITLE = 0
STATE_GAME = 1
STATE_PAUSE = 2
STATE_MENU = 3
STATE_SETTINGS = 4
STATE_TRAIL_SELECTION = 5
STATE_SCROLLED_TEXT = 6  
STATE_FADE_OUT = 7
STATE_FADE_IN = 8

state = STATE_TITLE


explosion_start_time = None



def load_songs():
    songs = []
    for i in range(1, 7):
        song = pygame.mixer.Sound('assets/song' + str(i) + '.mp3')
        songs.append(song)
    return songs

def play_random_song(songs):
    random_song = random.choice(songs)
    random_song.play(-1)  # -1 to loop the song


songs = load_songs()




# Function to calculate NOTE_SPEED based on BPM
def calculate_note_speed(bpm):
    beat_duration = 60 / bpm  # seconds per beat
    travel_distance = HIT_Y  # distance to travel to hit line
    beats_to_hit_line = travel_distance / 60  # Assumption: 60 beats per full screen height
    note_speed = travel_distance / (beats_to_hit_line * beat_duration)
    return note_speed


user_bpm = 135
NOTE_SPEED = calculate_note_speed(user_bpm)

def drawPerfect(x, y):
    font = pygame.font.Font(None, 36)
    perfect_text = font.render("Perfect!", True, (0, 0, 0))
    screen.blit(perfect_text, (x, y))
    pygame.display.update()



def create_checkerboard_pattern(width, height, square_size, color, progress):
    pattern = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            constant_alpha = 200  # Adjust the opacity value as needed
            alpha = constant_alpha
            color_with_alpha = (*color, alpha)
            pygame.draw.rect(pattern, color_with_alpha, (x, y, square_size, square_size))
    return pattern

def load_level_data():
    global notes
    with open('json/level.json', 'r') as f:
        level_data = json.load(f)
    notes = [Note(note['lane'], note['time']) for note in level_data]



menu_font = pygame.font.Font('assets/upheavtt.ttf', 36)

# Note class
class Note:
    def __init__(self, lane, timestamp):
        self.x = LANES[lane] + 10  # Adjust the offset_x as needed
        self.y = 0
        self.lane = lane
        self.timestamp = timestamp
        self.trail_length = 25  # Length of the trail
        self.trail_frequency = 10  
        self.hit = False  
    def update(self, current_time):
        self.y = (current_time - self.timestamp) * NOTE_SPEED / 1000

    def draw(self):
        # Draw the trail as circles
        for i in range(0, self.trail_length, self.trail_frequency):
            trail_y = self.y - i
            if trail_y >= 0:
                alpha = max(0, 255 - (255 * i / self.trail_length))  
                color_with_alpha = (255, 255, 255, alpha) 
                trail_surface = pygame.Surface((NOTE_WIDTH, NOTE_HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, color_with_alpha, (NOTE_WIDTH // 2, NOTE_HEIGHT // 2), NOTE_WIDTH // 2)
                screen.blit(trail_surface, (self.x, trail_y))

        # Draw the note
        screen.blit(note_image, (self.x, self.y))

class Explosion:
    def __init__(self, x, y, frames):
        self.x = x
        self.y = y
        self.frames = frames
        self.start_time = None
        self.frame_index = 0

    def trigger(self):
        self.start_time = pygame.time.get_ticks()
        self.frame_index = 0

    def update(self):
        if self.start_time is not None:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            frame_duration = 1000 // FPS  # 60 FPS, so frame duration is about 16.67 ms
            self.frame_index = elapsed_time // frame_duration

    def draw(self, screen):
        if self.start_time is not None and self.frame_index < len(self.frames):
            screen.blit(self.frames[self.frame_index], (self.x, self.y))
            return True  
        else:
            self.start_time = None  
            return False


explosions = []
explosion_frames = []



explosion_path = 'assets/next'
for i in range(1, 12): 
    frame = pygame.image.load(os.path.join(explosion_path, f'frame{i}.png'))
    explosion_frames.append(frame) 

explosions = [
    Explosion(LANES[0], HIT_Y, explosion_frames),
    Explosion(LANES[1], HIT_Y, explosion_frames),
    Explosion(LANES[2], HIT_Y, explosion_frames),
    Explosion(LANES[3], HIT_Y, explosion_frames)
]

# Load animation frames
animation_frames = []
animation_path = 'assets/wills_magic_particle_effects/black_hole/frames'
for i in range(17, 120):
    frame = pygame.image.load(os.path.join(animation_path, f'frame{i:04d}.png'))
    animation_frames.append(frame)

# Game variables
notes = [Note(note['lane'], note['time']) for note in level_data]
score = 0
animation_start_time = None
animation_frame_index = 0
animation_x = 0  # Initialize animation position
animation_y = 0  # Initialize animation positio








def display_black_scrolling_text(text, duration):
    font = pygame.font.Font('assets/upheavtt.ttf', 32)
    text_surface = font.render(text, True, BLACK)
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()
    
    start_time = pygame.time.get_ticks()
    elapsed_time = pygame.time.get_ticks() - start_time
    x_position = SCREEN_WIDTH - (elapsed_time / duration) * (SCREEN_WIDTH + text_width)
    
    screen.fill(BLACK)
    screen.blit(bg, (0,0))
    screen.blit(text_surface, (x_position, SCREEN_HEIGHT // 2 - text_height // 2))
    pygame.display.flip()
    
   
    return elapsed_time < duration



music_file_path = 'assets/Awesomenarnia 124 (1).mp3'
song_name = os.path.basename(music_file_path).replace('.mp3', '')


enterMusic = 'assets/selection_01.mp3'




running = True
start_time = pygame.time.get_ticks()


key_states = {
    pygame.K_a: False,
    pygame.K_s: False,
    pygame.K_d: False,
    pygame.K_f: False
}



note5_sound = pygame.mixer.Sound('assets/note5.mp3')
note6_sound = pygame.mixer.Sound('assets/note6.mp3')


selection_sounds_played = [False] * len(menu.options)

game_start_time = 0
song_playing = False
trail_enabled = True
back_button_frame = 1
back_button_animation = False
back_button_animation_time = 0
previous_mouse_pos = None

previous_trail_type = None
# Load animation frames
animation1_frames = [pygame.image.load(f"assets/wills_magic_particle_effects/green_spiral/frames/frame{i:04d}.png") for i in range(120)]
animation2_frames = [pygame.image.load(f"assets/wills_magic_particle_effects/green_spiral/frames/frame{i:04d}.png") for i in range(120)]
fade_back = False
animation_started = False
opacity = 0
game_started = False
trail_type = None
star_trail = []


key_states = {
    pygame.K_a: False,
    pygame.K_s: False,
    pygame.K_d: False,
    pygame.K_f: False,
}

key_rgb_values = {
    pygame.K_a: (255, 255, 255),
    pygame.K_s: (255, 255, 255),
    pygame.K_d: (255, 255, 255),
    pygame.K_f: (255, 255, 255),
}

fade_in_start_time = None
game_ended = False
waiting_for_key = False
perfect_chain = 0
perfect_chain_text_alpha = 0
perfect_chain_text_start_time = None
perfect_chain_duration = 2000  # 2 seconds
note_hit = False 

while running:
    current_time = pygame.time.get_ticks() - start_time
    if state == STATE_TITLE:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:

                    pygame.mixer.init()
                    pygame.mixer.music.load(enterMusic)
                    pygame.mixer.music.play()
                    animation_started = True

        # Draw title screen
        screen.fill(BLACK)

        font_size = int(SCREEN_HEIGHT / 15)
        font = pygame.font.Font('assets/upheavtt.ttf', font_size)
        rhythm_game_text = "deadat18 rhythm"
        text_width = 0
        for char in rhythm_game_text:
            char_surface = font.render(char, True, WHITE)
            text_width += char_surface.get_width()
        x_offset = (SCREEN_WIDTH - text_width) / 2
        for i, char in enumerate(rhythm_game_text):
            char_surface = font.render(char, True, WHITE)
            char_rect = char_surface.get_rect(center=(x_offset + char_surface.get_width() / 2, SCREEN_HEIGHT / 2 + 10 * math.sin(pygame.time.get_ticks() * 0.005)))
            x_offset += char_surface.get_width()
            if char_rect.collidepoint(pygame.mouse.get_pos()):
                color_angle = pygame.time.get_ticks() * 0.01 + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                char_surface = font.render(char, True, (r, g, b))
                char_rect.y += 5 * math.sin(pygame.time.get_ticks() * 0.01 + i * 0.1)
            screen.blit(char_surface, char_rect)

        font_size = int(SCREEN_HEIGHT / 30)
        font = pygame.font.Font('assets/upheavtt.ttf', font_size)
        press_space_text = "Press Space to continue"
        text_width = 0
        for char in press_space_text:
            char_surface = font.render(char, True, WHITE)
            text_width += char_surface.get_width()
        x_offset = (SCREEN_WIDTH - text_width) / 2
        for i, char in enumerate(press_space_text):
            char_surface = font.render(char, True, WHITE)
            char_rect = char_surface.get_rect(center=(x_offset + char_surface.get_width() / 2, SCREEN_HEIGHT * 0.8 + 5 * math.sin(pygame.time.get_ticks() * 0.005 + math.pi / 2)))
            x_offset += char_surface.get_width()
            if char_rect.collidepoint(pygame.mouse.get_pos()):
                color_angle = pygame.time.get_ticks() * 0.01 + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                char_surface = font.render(char, True, (r, g, b))
                char_rect.y += 5 * math.sin(pygame.time.get_ticks() * 0.01 + i * 0.1)
            screen.blit(char_surface, char_rect)

        if animation_started:
            # Draw animation
            frame = (current_time // 16) % 120  # 16ms per frame, 120 frames total
            animation1_surface = animation1_frames[frame]
            animation2_surface = animation2_frames[frame]
            animation1_rect = animation1_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            animation2_rect = animation2_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(animation1_surface, animation1_rect)
            #screen.blit(animation2_surface, animation2_rect)

            # Wait for animation to finish
            if frame >= 119:  # 120 frames total
                animation_started = False
                state = STATE_MENU  # Show menu

                    
        pygame.display.flip()
        clock.tick(60)
    elif state == STATE_MENU:
          #  print("Drawing trail with type:", trail_type)
            
            if not song_playing:
                play_random_song(songs)
                song_playing = True

            opacity = 0  
            # Handle menu events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_k:
                        trail_enabled = False
                        if not trail_enabled:
                            star_trail = [] 
                    selected_option = menu.handle_input(event)
                    if selected_option is not None:
                        if selected_option == len(menu.options) - 1:
                            running = False
                        elif selected_option == 0: 
                            state = STATE_SCROLLED_TEXT
                            scroll_text_start_time = pygame.time.get_ticks()  
                            pygame.mixer.stop()
                            
                            load_level_data()
                            notes = [Note(note['lane'], note['time']) for note in level_data] 
                        elif selected_option == 1:  
                            state = STATE_SETTINGS
                                    
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    for idx, option in enumerate(menu.options):
                        option_rect = pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30)
                        if option_rect.collidepoint(mouse_pos) and not selection_sounds_played[idx]:
                            note5_sound.play()
                            selection_sounds_played[idx] = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if menu.trail_dropdown_rect.collidepoint(mouse_pos):
                        menu.trail_dropdown_open = not menu.trail_dropdown_open
                    for i, trail_rect in enumerate(menu.trail_rects):
                        if trail_rect.collidepoint(mouse_pos):
                            menu.selected_trail = i
                            menu.trail_dropdown_open = False
                    for idx, option in enumerate(menu.options):
                        option_rect = pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30)
                        if option_rect.collidepoint(mouse_pos):
                            if idx == len(menu.options) - 1:
                                running = False
                            elif idx == 0:
                                state = STATE_SCROLLED_TEXT
                                scroll_text_start_time = pygame.time.get_ticks()  # Store the start time
                                pygame.mixer.stop()
                                # Load the selected level
                                load_level_data()
                                notes = [Note(note['lane'], note['time']) for note in level_data]
                                pygame.mixer.music.load('assets/Awesomenarnia 124 (1).mp3')
                                pygame.mixer.music.play()
                                start_time = pygame.time.get_ticks()  # Reset the start time
                                state = STATE_GAME
                            elif idx == 1:
                                state = STATE_SETTINGS
                    # Check if settings button is pressed
                    settings_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 150, 20)
                    if settings_button_rect.collidepoint(mouse_pos):
                        state = STATE_SETTINGS

           
            if not any(option_rect.collidepoint(pygame.mouse.get_pos()) for option_rect in [pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30) for idx, option in enumerate(menu.options)]):
                selection_sounds_played = [False] * len(menu.options)

            # Draw menu
            screen.fill(BLACK)
            menu.draw(screen, menu_font)


            if trail_enabled:
                mouse_pos = pygame.mouse.get_pos()

                if previous_mouse_pos is not None and mouse_pos != previous_mouse_pos:
                   
                    screen.fill(BLACK)
                    menu.draw(screen, menu_font)



                for i, (x, y, opacity) in enumerate(star_trail):
                    opacity += 10
                    if opacity > 255:
                        opacity = 255
                    star_trail[i] = (x, y, opacity)

                    '''
                    # Draw star with chosen trail pattern
                    if menu.selected_trail == 2:  # No trail
                        pass
                    elif menu.selected_trail == 0:  # RGB Trail
                        color_angle = pygame.time.get_ticks() * 0.01 + i * 0.1
                        r = int(math.sin(color_angle) * 128 + 128)
                        g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                        b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                        s = pygame.Surface((5, 5), pygame.SRCALPHA)
                        pygame.draw.circle(s, (r, g, b, opacity), (2, 2), 2)
                        screen.blit(s, (x, y))
                    elif menu.selected_trail == 1:  # Fading Trail
                        s = pygame.Surface((5, 5), pygame.SRCALPHA)
                        color = (57, 255, 20)  # Neon green
                        pygame.draw.circle(s, (color[0], color[1], color[2], opacity), (2, 2), 2)
                        screen.blit(s, (x, y))
'''
             
                star_trail = [(x, y, opacity) for x, y, opacity in star_trail if 0 < x < SCREEN_WIDTH and 0 < y < SCREEN_HEIGHT]

               
                previous_mouse_pos = mouse_pos
            else:
                star_trail = []
                previous_mouse_pos = None

            pygame.display.flip()
            clock.tick(60)
   

    elif state == STATE_SETTINGS:
        # Draw settings window
        screen.fill(BLACK)
        settings_window_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 200, 300, 400)
        pygame.draw.rect(screen, WHITE, settings_window_rect, 1)

        # Music volume settings
        music_volume_meter_rect = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 10, 280, 25)
        pygame.draw.rect(screen, WHITE, music_volume_meter_rect, 1)
        music_volume_percentage = pygame.mixer.music.get_volume() * 100
        for i in range(int(music_volume_percentage * 2.8)):
            hue = (music_volume_percentage / 100) * 0.83
            h_i = int(hue * 6)
            f = hue * 6 - h_i
            p = 1 * (1 - 1)
            q = 1 * (1 - f * 1)
            t = 1 * (1 - (1 - f) * 1)

            if h_i == 0:
                r, g, b = 1, t, p
            elif h_i == 1:
                r, g, b = q, 1, p
            elif h_i == 2:
                r, g, b = p, 1, t
            elif h_i == 3:
                r, g, b = p, q, 1
            elif h_i == 4:
                r, g, b = t, p, 1
            elif h_i == 5:
                r, g, b = 1, p, q

            r, g, b = int(r * 255), int(g * 255), int(b * 255)
            pygame.draw.rect(screen, (r, g, b), (music_volume_meter_rect.x + i, music_volume_meter_rect.y, 1, 25))

        music_volume_text = font.render("Music Volume: " + str(int(pygame.mixer.music.get_volume() * 100)) + "%", True, WHITE)
        music_volume_text_rect = music_volume_text.get_rect()
        music_volume_text_rect.x = settings_window_rect.x + 10
        music_volume_text_rect.y = settings_window_rect.y + 40
        screen.blit(music_volume_text, music_volume_text_rect)

        # SFX volume settings
        sfx_volume_meter_rect = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 80, 280, 25)
        pygame.draw.rect(screen, WHITE, sfx_volume_meter_rect, 1)
        sfx_volume_percentage = note5_sound.get_volume() * 100
        for i in range(int(sfx_volume_percentage * 2.8)):
            hue = (sfx_volume_percentage / 100) * 0.83
            h_i = int(hue * 6)
            f = hue * 6 - h_i
            p = 1 * (1 - 1)
            q = 1 * (1 - f * 1)
            t = 1 * (1 - (1 - f) * 1)
            if h_i == 0:
                r, g, b = 1, t, p
            elif h_i == 1:
                r, g, b = q, 1, p
            elif h_i == 2:
                r, g, b = p, 1, t
            elif h_i == 3:
                r, g, b = p, q, 1
            elif h_i == 4:
                r, g, b = t, p, 1
            elif h_i == 5:
                r, g, b = 1, p, q

            r, g, b = int(r * 255), int(g * 255), int(b * 255)
            pygame.draw.rect(screen, (r, g, b), (sfx_volume_meter_rect.x + i, sfx_volume_meter_rect.y, 1, 25))

        sfx_volume_text = font.render("SFX Volume: " + str(int(note5_sound.get_volume() * 100)) + "%", True, WHITE)
        sfx_volume_text_rect = sfx_volume_text.get_rect()
        sfx_volume_text_rect.x = settings_window_rect.x + 10
        sfx_volume_text_rect.y = settings_window_rect.y + 110
        screen.blit(sfx_volume_text, sfx_volume_text_rect)

   
        back_button_image = pygame.image.load('assets/Back' + str(back_button_frame) + '.png')
        back_button_image = pygame.transform.scale(back_button_image, (25, 25))
        back_button_rect = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 140, 25, 25)
        screen.blit(back_button_image, back_button_rect)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if music_volume_meter_rect.collidepoint(mouse_pos):
                    new_volume = (mouse_pos[0] - music_volume_meter_rect.x) / 280
                    pygame.mixer.music.set_volume(new_volume)
                    for song in songs:
                        song.set_volume(new_volume)
                elif sfx_volume_meter_rect.collidepoint(mouse_pos):
                    new_volume = (mouse_pos[0] - sfx_volume_meter_rect.x) / 280
                    note5_sound.set_volume(new_volume)
                    note6_sound.set_volume(new_volume)
                elif back_button_rect.collidepoint(mouse_pos):
                    back_button_animation = True
                    back_button_animation_time = pygame.time.get_ticks()
                    note6_sound.play()
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if music_volume_meter_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                    new_volume = (mouse_pos[0] - music_volume_meter_rect.x) / 280
                    pygame.mixer.music.set_volume(new_volume)
                    for song in songs:
                        song.set_volume(new_volume)
                elif sfx_volume_meter_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                    new_volume = (mouse_pos[0] - sfx_volume_meter_rect.x) / 280
                    note5_sound.set_volume(new_volume)
                    note6_sound.set_volume(new_volume)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = STATE_MENU

       
        if back_button_animation:
            current_time = pygame.time.get_ticks()
            if current_time - back_button_animation_time > 100:
                back_button_frame += 1
                back_button_animation_time = current_time
            if back_button_frame > 5:
                state = STATE_MENU
                back_button_frame = 1
                back_button_animation = False

        pygame.display.flip()
        clock.tick(60)


    elif state == STATE_GAME:
                


        game_started = True
        game_time = current_time - game_start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
       
            if event.type == pygame.KEYDOWN:
                if event.key in key_states:
                    key_states[event.key] = True
                    color_angle = current_time * 0.01
                    r = int(math.sin(color_angle) * 128 + 128)
                    g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                    b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                    key_rgb_values[event.key] = (r, g, b)
            if event.type == pygame.KEYUP:
                if event.key in key_states:
                    key_states[event.key] = False
                    
                    key_rgb_values[event.key] = (255, 255, 255)
                    '''
                    if event.key == pygame.K_a:  # Start animation on "a" key hit
                        animation_start_time = pygame.time.get_ticks()
                        animation_frame_index = 0
                        animation_x = random.randint(0, SCREEN_WIDTH - animation_frames[0].get_width())
                        animation_y = random.randint(0, SCREEN_HEIGHT - animation_frames[0].get_height())
                    '''
          

            
        
        # Update notes
        for note in notes:
            note.update(current_time)
            

      
        keys = pygame.key.get_pressed()
        for note in notes[:]:
            if HIT_Y - NOTE_HEIGHT <= note.y <= HIT_Y + NOTE_HEIGHT:

                if keys[KEYS[note.lane]]:
                    
                   



                    notes.remove(note)
                    score += 1
                    note_hit = True
                        
        
                    explosion_start_time = pygame.time.get_ticks()
                    explosion_frame_index = 0
                    explosion_x = LANES[note.lane] - 7
                    explosion_y = HIT_Y





                if note_hit:
                    perfect_chain += 1
                    note_hit = False  
                else:
                    if perfect_chain > 0:
                        perfect_chain = 0

                if perfect_chain >= 5:
                    perfect_chain_text_start_time = pygame.time.get_ticks()
                    perfect_chain_text_alpha = 255

                    '''
                    if KEYS[note.lane] == pygame.K_a:
                        animation_start_time = pygame.time.get_ticks()
                        animation_frame_index = 0
                        animation_x = random.randint(0, SCREEN_WIDTH - animation_frames[0].get_width())
                        animation_y = random.randint(0, SCREEN_HEIGHT - animation_frames[0].get_height())
                    '''
                print(perfect_chain)
    
        notes = [note for note in notes if note.y <= SCREEN_HEIGHT]


        

        
        screen.fill(BLACK)
        screen.blit(bg, (0,0))
        for note in notes:
            note.draw()

        
        font = pygame.font.Font('assets/upheavtt.ttf', 80)
        keys = ['A', 'S', 'D', 'F']
        key_x_positions = [59, 137, 215, 295] 
        key_y_position = HIT_Y - 18
        wave_amplitude = 10
        wave_frequency = 0.005

        key_press_timers = {
            'A': 0,
            'S': 0,
            'D': 0,
            'F': 0,
        }

        key_rgb_values = {
            'A': (255, 255, 255),
            'S': (255, 255, 255),
            'D': (255, 255, 255),
            'F': (255, 255, 255),
        }

        for i, key in enumerate(keys):
            color = key_rgb_values[key]
            if key == 'A' and key_states[pygame.K_a]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)
            elif key == 'S' and key_states[pygame.K_s]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)
            elif key == 'D' and key_states[pygame.K_d]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)
            elif key == 'F' and key_states[pygame.K_f]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)

            if key_press_timers[key] != 0 and pygame.time.get_ticks() - key_press_timers[key] < 5000:
                color = key_rgb_values[key]
            else:
                key_press_timers[key] = 0
                key_rgb_values[key] = (255, 255, 255)

            key_surface = font.render(key, True, color)
            key_width = key_surface.get_width()
            key_height = key_surface.get_height()
            wave_y = key_y_position + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
            screen.blit(key_surface, (key_x_positions[i], wave_y))
                



        
        if perfect_chain >= 5:
            font = pygame.font.Font('assets/upheavtt.ttf', 32)
            perfect_chain_text = f'Perfect Chain: {perfect_chain}'
            perfect_chain_surface = font.render(perfect_chain_text, True, (255, 255, 255))
            perfect_chain_x = SCREEN_WIDTH / 2 - perfect_chain_surface.get_width() / 2
            perfect_chain_y = 20

            if perfect_chain_text_start_time is not None:
                elapsed_time = pygame.time.get_ticks() - perfect_chain_text_start_time
                perfect_chain_text_alpha = int(255 * (1 - (elapsed_time / perfect_chain_duration)))
                if perfect_chain_text_alpha < 0:
                    perfect_chain_text_alpha = 0

            perfect_chain_surface.set_alpha(perfect_chain_text_alpha)
            screen.blit(perfect_chain_surface, (perfect_chain_x, perfect_chain_y))      

        
        if animation_start_time is not None:
            elapsed_time = pygame.time.get_ticks() - animation_start_time
            frame_duration = 1000 // FPS  
            animation_frame_index = elapsed_time // frame_duration
            if animation_frame_index < len(animation_frames):   
                screen.blit(animation_frames[animation_frame_index], (animation_x, animation_y))
            else:
                animation_start_time = None  

        
        if explosion_start_time is not None:
            elapsed_time = pygame.time.get_ticks() - explosion_start_time
            frame_duration = 1000 // FPS 
            explosion_frame_index = elapsed_time // frame_duration
            if explosion_frame_index < len(explosion_frames):
                screen.blit(explosion_frames[explosion_frame_index], (explosion_x, explosion_y))
            else:
                explosion_start_time = None  

        
        pygame.draw.line(screen, WHITE, (0, HIT_Y + NOTE_HEIGHT // 2), (SCREEN_WIDTH, HIT_Y + NOTE_HEIGHT // 2))



        
        font = pygame.font.Font('assets/upheavtt.ttf', 32)
        score_text = f'Score: {score}'
        base_x = 15  
        base_y = 15  
        wave_amplitude = 10
        wave_frequency = 0.005
        
       
        text_width = sum(font.render(char, True, BLACK).get_width() for char in score_text)
        
        
        if notes:
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, BLACK)
                char_width = char_surface.get_width()
                
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                
                base_x += char_width

            base_x = 10  
            base_y = 10  
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, WHITE)
                char_width = char_surface.get_width()
                # Calculate the wave y-offset
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                
                base_x += char_width
            fade_in_start_time = None
        else:
            if fade_in_start_time is None:
                fade_in_start_time = pygame.time.get_ticks()

            fade_out_time = 1000  
            fade_in_time = 1000 
            fade_out_start_time = pygame.time.get_ticks() - fade_out_time

            font = pygame.font.Font('assets/upheavtt.ttf', 32)
            score_text = f'Score: {score}'
            base_x = 15  
            base_y = 15  
            wave_amplitude = 10
            wave_frequency = 0.005

            fade_out_alpha = int(255 * (1 - (pygame.time.get_ticks() - fade_out_start_time) / fade_out_time))
            if fade_out_alpha < 0:
                fade_out_alpha = 0
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, (0, 0, 0, fade_out_alpha))
                char_surface.set_alpha(fade_out_alpha)
                char_width = char_surface.get_width()
                
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                
                base_x += char_width

            base_x = 10  
            base_y = 10  
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, (255, 255, 255, fade_out_alpha))
                char_surface.set_alpha(fade_out_alpha)
                char_width = char_surface.get_width()
                
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                
                base_x += char_width

            font = pygame.font.Font('assets/upheavtt.ttf', 30)
            score_text = f'Score: {score}'
            base_x = SCREEN_WIDTH / 2 - text_width / 2
            base_y = SCREEN_HEIGHT / 2 - 32
            color_angle = current_time * 0.01
            r = int(math.sin(color_angle) * 128 + 128)
            g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
            b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
            fade_in_alpha = int(255 * (pygame.time.get_ticks() - fade_in_start_time) / fade_in_time)
            if fade_in_alpha > 255:
                fade_in_alpha = 255
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, (r, g, b))
                char_surface.set_alpha(fade_in_alpha)
                char_width = char_surface.get_width()
                
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                
                base_x += char_width

        
            
            button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 50, 200, 50)
            button_color = (255, 255, 255)
            button_hover_color = (200, 200, 200)
            button_text_color = (0, 0, 0)
            button_font = pygame.font.Font('assets/upheavtt.ttf', 24)
            button_text = 'Back to Menu'
            button_text_surface = button_font.render(button_text, True, button_text_color)

            if fade_in_start_time is None:
                fade_in_start_time = pygame.time.get_ticks()
                fade_in_time = 1000  # 1 second

            fade_in_alpha = int(255 * (pygame.time.get_ticks() - fade_in_start_time) / fade_in_time)
            if fade_in_alpha > 255:
                fade_in_alpha = 255

            if button_rect.collidepoint(pygame.mouse.get_pos()):
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                button_text_color = (r, g, b)

            pygame.draw.rect(screen, button_color, button_rect, border_radius=10)

            text_x = button_rect.x + 25
            text_y = button_rect.y + 15 + math.sin(current_time * 0.01) * 5
            button_text_surface = button_font.render(button_text, True, button_text_color)
            button_text_surface.set_alpha(fade_in_alpha)
            screen.blit(button_text_surface, (text_x, text_y))

            pygame.draw.rect(screen, (255, 255, 255), (button_rect.x - 2, button_rect.y - 2, button_rect.width + 4, button_rect.height + 4), 1, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), (button_rect.x - 4, button_rect.y - 4, button_rect.width + 8, button_rect.height + 8), 1, border_radius=10)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                     
                        pygame.mixer.music.stop()
                        song_playing = False
                        
                        fade_out_start_time = pygame.time.get_ticks()
                        fade_out_time = 500  # 0.5 seconds
                        state = STATE_FADE_OUT
    elif state == STATE_FADE_OUT:
        
        fade_out_alpha = int(255 * (1 - (pygame.time.get_ticks() - fade_out_start_time) / fade_out_time))
        if fade_out_alpha < 0:
            fade_out_alpha = 0
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, fade_out_alpha))
        screen.blit(s, (0, 0))

        
        if fade_out_alpha == 0:
            state = STATE_FADE_IN
            fade_in_start_time = pygame.time.get_ticks()
            fade_in_time = 500  # 0.5 seconds                    
        
    
    elif state == STATE_FADE_IN:
       
        fade_in_alpha = int(255 * (pygame.time.get_ticks() - fade_in_start_time) / fade_in_time)
        if fade_in_alpha > 255:
            fade_in_alpha = 255
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 255 - fade_in_alpha))
        screen.blit(s, (0, 0))


       
        menu.draw(screen, menu_font)

        
        if fade_in_alpha == 255:
            state = STATE_MENU 

    pygame.display.flip()

    
    clock.tick(FPS)

pygame.quit()